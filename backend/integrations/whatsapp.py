# backend/integrations/whatsapp.py
from fastapi import Request, BackgroundTasks
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import aiohttp
import os
from pathlib import Path

class WhatsAppIntegration:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.client = Client(self.account_sid, self.auth_token)
        self.from_number = "whatsapp:+14155238886"  # Twilio sandbox number
        
    async def handle_webhook(self, request: Request, background_tasks: BackgroundTasks) -> str:
        """Handle incoming WhatsApp messages"""
        form = await request.form()
        from_number = form.get('From', '').replace('whatsapp:', '')
        body = form.get('Body', '').lower()
        num_media = int(form.get('NumMedia', 0))
        
        response = MessagingResponse()
        
        if num_media == 0:
            response.message(
                "👋 Welcome to Media Authenticator!\n\n"
                "Send me an image or video and I'll analyze it for:\n"
                "• AI-generated content (deepfakes)\n"
                "• Photoshop manipulation\n"
                "• Metadata verification\n"
                "• C2PA authenticity\n\n"
                "Your media will be analyzed securely."
            )
            return str(response)
        
        # Process each media item
        for i in range(num_media):
            media_url = form.get(f'MediaUrl{i}')
            media_type = form.get(f'MediaContentType{i}')
            
            if media_type.startswith('image/') or media_type.startswith('video/'):
                background_tasks.add_task(
                    self._process_and_respond,
                    media_url,
                    media_type,
                    from_number
                )
                
                response.message(
                    "🔍 Analysis started! I'm examining your media for signs of manipulation. "
                    "This takes 10-30 seconds..."
                )
            else:
                response.message(f"❌ Unsupported file type: {media_type}")
        
        return str(response)
    
    async def _process_and_respond(self, media_url: str, media_type: str, to_number: str):
        """Download, analyze, and respond"""
        # Download media
        async with aiohttp.ClientSession() as session:
            async with session.get(
                media_url, 
                auth=aiohttp.BasicAuth(self.account_sid, self.auth_token)
            ) as resp:
                if resp.status == 200:
                    # Save and analyze (integrate with your analysis pipeline)
                    content = await resp.read()
                    
                    # TODO: Integrate with your analysis pipeline
                    # result = await analyze_media(content, media_type)
                    
                    # Send results
                    message = self._format_result_message({"status": "completed", "trust_score": 85})
                    self.client.messages.create(
                        from_=self.from_number,
                        body=message,
                        to=f"whatsapp:{to_number}"
                    )
    
    def _format_result_message(self, result: dict) -> str:
        """Format analysis results for WhatsApp"""
        score = result.get('trust_score', 0)
        verdict = result.get('verdict', 'uncertain')
        
        emoji = "✅" if verdict == "authentic" else "⚠️" if verdict == "suspicious" else "❌"
        
        return (
            f"{emoji} *Analysis Complete*\n\n"
            f"*Trust Score:* {score}/100\n"
            f"*Verdict:* {verdict.replace('_', ' ').title()}\n\n"
            f"View detailed report: https://your-dashboard.com/result/{result.get('id')}"
        )
