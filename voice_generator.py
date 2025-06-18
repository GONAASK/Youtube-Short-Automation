import os
import requests
import time
from config import Config
from api_config import api_config

class VoiceGenerator:
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.elevenlabs.io/v1"
        self.update_api_key()
    
    def update_api_key(self):
        """Update API key from config"""
        if api_config.elevenlabs_keys:
            self.api_key = api_config.elevenlabs_keys[0]
        else:
            self.api_key = os.getenv('ELEVENLABS_API_KEY', '')
    
    def generate_voice(self, text, video_id=None):
        """Generate voice from text using ElevenLabs"""
        if not self.api_key:
            print("❌ No ElevenLabs API key configured!")
            return None
        
        try:
            # Clean text for voice generation
            cleaned_text = self.clean_text_for_voice(text)
            
            # Generate unique filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"voice_{video_id}_{timestamp}.mp3" if video_id else f"voice_{timestamp}.mp3"
            output_path = os.path.join(Config.TEMP_DIR, filename)
            
            # Ensure temp directory exists
            os.makedirs(Config.TEMP_DIR, exist_ok=True)
            
            # API request parameters
            url = f"{self.base_url}/text-to-speech/{Config.ELEVENLABS_VOICE_ID}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": cleaned_text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            print(f"🎤 Generating voice for {len(cleaned_text)} characters...")
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                print(f"✅ Voice generated successfully: {output_path}")
                return output_path
            else:
                print(f"❌ Voice generation failed: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Try to switch API key if available
                if len(api_config.elevenlabs_keys) > 1:
                    print("🔄 Trying alternative API key...")
                    api_config.elevenlabs_keys.append(api_config.elevenlabs_keys.pop(0))
                    self.update_api_key()
                    return self.generate_voice(text, video_id)
                
                return None
                
        except Exception as e:
            print(f"❌ Error generating voice: {e}")
            return None
    
    def clean_text_for_voice(self, text):
        """Clean text for better voice generation"""
        # Remove any metadata or unwanted content
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and metadata
            if line and not line.startswith('TITLE:') and not line.startswith('GENRE:') and not line.startswith('DATE:'):
                cleaned_lines.append(line)
        
        # Join lines and clean up
        cleaned_text = ' '.join(cleaned_lines)
        
        # Remove extra spaces and punctuation issues
        cleaned_text = ' '.join(cleaned_text.split())
        
        # Ensure it ends with proper punctuation
        if cleaned_text and not cleaned_text[-1] in '.!?':
            cleaned_text += '.'
        
        return cleaned_text
    
    def list_popular_voices(self):
        """List popular ElevenLabs voices"""
        if not self.api_key:
            print("❌ No ElevenLabs API key configured!")
            return
        
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                voices = response.json().get("voices", [])
                
                print("\n🎤 Popular ElevenLabs Voices:")
                print("-" * 40)
                
                popular_voices = [
                    {"name": "Josh", "id": "21m00Tcm4TlvDq8ikWAM", "description": "Deep male voice"},
                    {"name": "Arnold", "id": "VR6AewLTigWG4xSOukaG", "description": "Strong male voice"},
                    {"name": "Domi", "id": "AZnzlk1XvdvUeBnXmlld", "description": "Female voice"},
                    {"name": "Bella", "id": "EXAVITQu4vr4xnSDxMaL", "description": "Soft female voice"}
                ]
                
                for voice in popular_voices:
                    print(f"• {voice['name']} ({voice['id']}) - {voice['description']}")
                
                print(f"\nCurrent voice: {Config.ELEVENLABS_VOICE_ID}")
                
            else:
                print(f"❌ Failed to fetch voices: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error listing voices: {e}")
    
    def test_voice(self, text="Hello, this is a test of the voice generation system."):
        """Test voice generation with a simple text"""
        print("🎤 Testing voice generation...")
        result = self.generate_voice(text)
        if result:
            print(f"✅ Test successful! Audio saved to: {result}")
        else:
            print("❌ Test failed!")
        return result 