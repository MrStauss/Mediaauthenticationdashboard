# backend/analyzers/metadata_analyzer.py
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

class MetadataAnalyzer:
    """Extract and verify C2PA, EXIF, and forensic metadata"""
    
    def __init__(self):
        self.weights = {
            'c2pa_valid': 0.4,
            'camera_signature': 0.3,
            'editing_software': 0.2,
            'consistency': 0.1
        }
    
    async def analyze(self, file_path: Path) -> Dict[str, Any]:
        results = {
            'c2pa': await self._check_c2pa(file_path),
            'exif': await self._extract_exif(file_path),
            'forensic_metadata': await self._forensic_metadata(file_path),
            'score': 0.0,
            'risk_factors': []
        }
        
        # Calculate score
        score = 0.0
        
        # C2PA validation
        if results['c2pa'].get('valid'):
            score += self.weights['c2pa_valid']
        elif results['c2pa'].get('exists'):
            results['risk_factors'].append("C2PA manifest present but invalid")
        
        # Camera signature check
        if results['exif'].get('make') and results['exif'].get('model'):
            score += self.weights['camera_signature']
        else:
            results['risk_factors'].append("Missing camera EXIF data")
        
        # Editing software detection
        software = results['exif'].get('software', '')
        if not software or software in ['GIMP', 'Adobe Photoshop', 'Affinity Photo']:
            score += self.weights['editing_software']
        else:
            results['risk_factors'].append(f"Edited with: {software}")
        
        results['score'] = min(score, 1.0)
        return results
    
    async def _check_c2pa(self, file_path: Path) -> Dict[str, Any]:
        """Check Content Authenticity Initiative manifest"""
        try:
            # Try to use c2pa-python if available
            from c2pa import Reader
            reader = Reader.from_file(str(file_path))
            manifest = reader.get_active_manifest()
            
            return {
                'exists': True,
                'valid': True,
                'claim_generator': manifest.claim_generator,
                'title': manifest.title,
                'format': manifest.format,
                'ingredients': len(manifest.ingredients) if hasattr(manifest, 'ingredients') else 0
            }
        except ImportError:
            # Fallback: check for C2PA box in file
            return await self._check_c2pa_manual(file_path)
        except Exception as e:
            return {'exists': False, 'valid': False, 'error': str(e)}
    
    async def _check_c2pa_manual(self, file_path: Path) -> Dict[str, Any]:
        """Manual C2PA box detection"""
        with open(file_path, 'rb') as f:
            header = f.read(5000)  # Check first 5KB
        
        # Look for C2PA box signatures
        c2pa_signatures = [b'c2pa', b'C2PA', b'caBX']
        found = any(sig in header for sig in c2pa_signatures)
        
        return {
            'exists': found,
            'valid': None,  # Cannot validate without full SDK
            'method': 'manual_scan'
        }
    
    async def _extract_exif(self, file_path: Path) -> Dict[str, Any]:
        """Extract EXIF data using ExifTool"""
        try:
            result = subprocess.run(
                ['exiftool', '-json', '-a', '-u', str(file_path)],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return {'error': result.stderr}
            
            data = json.loads(result.stdout)[0]
            
            return {
                'make': data.get('Make'),
                'model': data.get('Model'),
                'software': data.get('Software'),
                'datetime': data.get('DateTimeOriginal'),
                'gps': {
                    'lat': data.get('GPSLatitude'),
                    'lon': data.get('GPSLongitude')
                } if 'GPSLatitude' in data else None,
                'dimensions': {
                    'width': data.get('ImageWidth'),
                    'height': data.get('ImageHeight')
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def _forensic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Check for forensic metadata inconsistencies"""
        # Check for multiple JPEG qualities (suggesting re-compression)
        # Check for thumbnail mismatches
        # Check for ICC profile consistency
        return {
            'multiple_qualities': False,  # Implement JPEG quality analysis
            'thumbnail_mismatch': False,
            'icc_consistent': True
        }
