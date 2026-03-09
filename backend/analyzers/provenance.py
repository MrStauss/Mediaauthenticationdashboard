import c2pa
import json

def verify_content_credentials(file_path):
    """
    Reads the 'Digital Nutrition Label' (C2PA manifest) from the file.
    """
    try:
        # Load the manifest reader
        reader = c2pa.Reader.from_file(file_path)
        manifest = reader.get_active_manifest()
        
        # Check for specific 'Assertions' like AI Generation or DNT
        is_ai = any(a['label'] == 'c2pa.ai_generated' for a in manifest.v1_manifest.get('assertions', []))
        is_dnt = any(a['label'] == 'cawg.training-mining' for a in manifest.v1_manifest.get('assertions', []))
        
        return {
            "status": "Authentic" if not is_ai else "AI Generated",
            "trust_score": 99 if not is_ai else 50,
            "signer": manifest.v1_manifest.get("signature_info", {}).get("issuer", "Unknown"),
            "dnt_enabled": is_dnt,
            "raw_manifest": manifest.v1_manifest
        }
    except Exception as e:
        # If no manifest exists, we mark it as 'Unsigned' and move to AI Forensics (Phase 3)
        return {"status": "Unsigned", "trust_score": 0, "error": "No Content Credentials found"}
