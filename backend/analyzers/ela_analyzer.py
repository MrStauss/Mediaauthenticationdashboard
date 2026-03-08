# backend/analyzers/ela_analyzer.py
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import io
import base64

class ELAAnalyzer:
    """Error Level Analysis for detecting image manipulation"""
    
    def __init__(self, quality: int = 90):
        self.quality = quality
    
    async def analyze(self, image_path: Path) -> Dict[str, Any]:
        """Perform ELA on image"""
        original = cv2.imread(str(image_path))
        
        # Save compressed version
        temp_path = Path("/tmp/ela_compressed.jpg")
        cv2.imwrite(str(temp_path), original, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        compressed = cv2.imread(str(temp_path))
        
        # Calculate difference
        diff = cv2.absdiff(original, compressed)
        
        # Enhance differences
        diff_enhanced = cv2.convertScaleAbs(diff, alpha=10, beta=0)
        
        # Calculate statistics
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Find hotspots (potential manipulation)
        _, thresh = cv2.threshold(diff_gray, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter significant regions
        min_area = (original.shape[0] * original.shape[1]) * 0.001  # 0.1% of image
        suspicious_regions = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                suspicious_regions.append({
                    'x': x, 'y': y, 'width': w, 'height': h,
                    'area': area
                })
        
        # Calculate overall ELA score (0 = original, 1 = highly manipulated)
        mean_diff = np.mean(diff_gray) / 255.0
        max_diff = np.max(diff_gray) / 255.0
        
        # Normalize score
        ela_score = min(mean_diff * 5, 1.0)  # Scale up for visibility
        
        temp_path.unlink()
        
        return {
            'ela_score': round(ela_score, 4),
            'max_difference': round(max_diff, 4),
            'mean_difference': round(mean_diff, 4),
            'suspicious_regions': suspicious_regions[:10],  # Top 10 regions
            'heatmap_base64': self._generate_heatmap_base64(diff_enhanced)
        }
    
    def _generate_heatmap_base64(self, diff_image: np.ndarray) -> str:
        """Convert ELA difference to base64 heatmap"""
        # Apply colormap
        heatmap = cv2.applyColorMap(diff_image, cv2.COLORMAP_JET)
        
        # Convert to PIL and then base64
        pil_img = Image.fromarray(cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB))
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
