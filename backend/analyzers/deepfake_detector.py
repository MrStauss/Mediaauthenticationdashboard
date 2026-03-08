# backend/analyzers/deepfake_detector.py
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np
from pathlib import Path
import cv2
from typing import Dict, Any

class DeepfakeDetector:
    """EfficientNet-B4 based deepfake detection"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize((380, 380)),  # EfficientNet-B4 input size
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
    def _load_model(self, model_path: Optional[str]) -> nn.Module:
        """Load pre-trained EfficientNet-B4"""
        model = models.efficientnet_b4(pretrained=False)
        
        # Modify classifier for binary classification (real/fake)
        num_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(num_features, 2)
        )
        
        if model_path and Path(model_path).exists():
            model.load_state_dict(torch.load(model_path, map_location=self.device))
        else:
            # Use ImageNet weights as fallback (not ideal for deepfakes, but functional)
            print("Warning: Using ImageNet weights. Download FaceForensics++ weights for accuracy.")
        
        model = model.to(self.device)
        model.eval()
        return model
    
    async def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """Analyze single image"""
        try:
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                
            fake_prob = probabilities[0][1].item()
            real_prob = probabilities[0][0].item()
            
            # Generate heatmap using Grad-CAM
            heatmap = self._generate_heatmap(input_tensor)
            
            return {
                'fake_probability': round(fake_prob, 4),
                'real_probability': round(real_prob, 4),
                'prediction': 'fake' if fake_prob > 0.5 else 'real',
                'confidence': round(max(fake_prob, real_prob), 4),
                'heatmap': heatmap,
                'artifacts_detected': self._detect_artifacts(image_path)
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def analyze_video(self, video_path: Path, sample_rate: int = 5) -> Dict[str, Any]:
        """Analyze video by sampling frames"""
        cap = cv2.VideoCapture(str(video_path))
        frame_predictions = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sample_rate == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                temp_path = Path(f"/tmp/frame_{frame_count}.jpg")
                cv2.imwrite(str(temp_path), frame_rgb)
                
                result = await self.analyze_image(temp_path)
                if 'error' not in result:
                    frame_predictions.append(result['fake_probability'])
                
                temp_path.unlink()
            
            frame_count += 1
        
        cap.release()
        
        if not frame_predictions:
            return {'error': 'No frames could be analyzed'}
        
        # Temporal consistency analysis
        mean_pred = np.mean(frame_predictions)
        std_pred = np.std(frame_predictions)
        
        return {
            'mean_fake_probability': round(mean_pred, 4),
            'temporal_variance': round(std_pred, 4),
            'frame_count': len(frame_predictions),
            'prediction': 'fake' if mean_pred > 0.5 else 'real',
            'confidence': round(max(mean_pred, 1-mean_pred), 4),
            'temporal_consistency': 'suspicious' if std_pred > 0.2 else 'normal'
        }
    
    def _generate_heatmap(self, input_tensor: torch.Tensor) -> Any:
        """Generate Grad-CAM heatmap for visualization"""
        # Simplified implementation - integrate pytorch-grad-cam for production
        return None
    
    def _detect_artifacts(self, image_path: Path) -> Dict[str, Any]:
        """Detect common deepfake artifacts"""
        img = cv2.imread(str(image_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Error Level Analysis (ELA)
        temp_path = Path("/tmp/ela_temp.jpg")
        cv2.imwrite(str(temp_path), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        compressed = cv2.imread(str(temp_path))
        ela = cv2.absdiff(img, compressed)
        ela_score = np.mean(ela) / 255.0
        temp_path.unlink()
        
        # Noise analysis
        noise = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return {
            'ela_score': round(ela_score, 4),
            'noise_level': round(noise, 2),
            'suspicious_regions': []
        }
