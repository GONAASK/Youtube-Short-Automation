import os
import sys
import time
import random
import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from api_config import api_config, setup_api_keys
from story_generator import StoryGenerator
from voice_generator import VoiceGenerator
from background_video import BackgroundVideoManager
from video_editor import VideoEditor
from subtitle_assemblyai import SubtitleGenerator

class AutoVideoGenerator:
    def __init__(self):
        self.story_generator = StoryGenerator()
        self.voice_generator = VoiceGenerator()
        self.background_manager = BackgroundVideoManager()
        self.video_editor = VideoEditor()
        self.subtitle_generator = SubtitleGenerator()
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = [
            Config.OUTPUT_DIR,
            Config.TEMP_DIR,
            "assets/backgrounds",
            "scripts"
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def check_api_keys(self):
        """Check if API keys are configured"""
        cohere_key = api_config.get_preferred_ai_key()
        elevenlabs_key = api_config.elevenlabs_keys[0] if api_config.elevenlabs_keys else None
        
        if not cohere_key:
            print("❌ No Cohere API key found!")
            print("Please run: python api_config.py")
            return False
        
        if not elevenlabs_key:
            print("❌ No ElevenLabs API key found!")
            print("Please run: python api_config.py")
            return False
        
        print("✅ API keys configured!")
        return True
    
    def generate_video(self, genre=None, continuation_id=None):
        """Generate a single video"""
        try:
            # Generate story
            print("\n📝 Generating story...")
            if continuation_id:
                story_data = self.story_generator.generate_continuation(continuation_id)
            else:
                story_data = self.story_generator.generate_story(genre)
            
            if not story_data:
                print("❌ Failed to generate story!")
                return None
            
            story_text = story_data['story']
            video_id = story_data['video_id']
            
            # Generate voice
            print("🎤 Generating voice...")
            audio_path = self.voice_generator.generate_voice(story_text, video_id)
            if not audio_path:
                print("❌ Failed to generate voice!")
                return None
            
            # Get background video
            print("🎬 Processing background video...")
            background_path = self.background_manager.get_random_background(
                target_duration=Config.MAX_DURATION,
                video_id=video_id
            )
            if not background_path:
                print("❌ Failed to get background video!")
                return None
            
            # Create video with subtitles
            print("🎥 Creating final video...")
            output_path = self.video_editor.create_video_with_subtitles(
                audio_path=audio_path,
                background_path=background_path,
                story_text=story_text,
                video_id=video_id
            )
            
            if output_path:
                print(f"✅ Video created successfully: {output_path}")
                return output_path
            else:
                print("❌ Failed to create video!")
                return None
                
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            return None
    
    def generate_batch(self, count=1, genre=None):
        """Generate multiple videos"""
        print(f"\n🚀 Starting batch generation of {count} videos...")
        
        if not self.check_api_keys():
            return
        
        successful_videos = []
        
        for i in range(count):
            print(f"\n--- Generating Video {i+1}/{count} ---")
            
            video_path = self.generate_video(genre)
            if video_path:
                successful_videos.append(video_path)
            
            # Small delay between videos
            if i < count - 1:
                time.sleep(2)
        
        print(f"\n✅ Batch complete! {len(successful_videos)}/{count} videos created successfully.")
        return successful_videos
    
    def list_available_scripts(self):
        """List all available scripts for continuation"""
        scripts_dir = Path("scripts")
        if not scripts_dir.exists():
            print("No scripts directory found!")
            return []
        
        script_files = list(scripts_dir.glob("*.json"))
        if not script_files:
            print("No scripts found!")
            return []
        
        print("\n📚 Available Scripts for Continuation:")
        print("-" * 50)
        
        scripts = []
        for i, script_file in enumerate(script_files, 1):
            try:
                import json
                with open(script_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                title = data.get('title', 'Untitled')
                genre = data.get('genre', 'Unknown')
                date = data.get('date', 'Unknown')
                video_id = data.get('video_id', 'Unknown')
                
                print(f"{i}. {title}")
                print(f"   Genre: {genre} | Date: {date} | ID: {video_id}")
                print()
                
                scripts.append({
                    'index': i,
                    'file': script_file,
                    'data': data
                })
                
            except Exception as e:
                print(f"Error reading {script_file}: {e}")
        
        return scripts
    
    def continue_story(self):
        """Continue an existing story"""
        scripts = self.list_available_scripts()
        if not scripts:
            return
        
        try:
            choice = int(input("\nEnter script number to continue (or 0 to cancel): "))
            if choice == 0:
                return
            
            if 1 <= choice <= len(scripts):
                selected_script = scripts[choice - 1]
                continuation_id = selected_script['data']['video_id']
                
                print(f"\nContinuing story: {selected_script['data']['title']}")
                self.generate_video(continuation_id=continuation_id)
            else:
                print("❌ Invalid choice!")
                
        except ValueError:
            print("❌ Please enter a valid number!")

def main():
    print("🎬 Auto AI Video Generator")
    print("=" * 40)
    
    generator = AutoVideoGenerator()
    
    while True:
        print("\nOptions:")
        print("1. Generate single video")
        print("2. Generate batch videos")
        print("3. Continue existing story")
        print("4. Setup API keys")
        print("5. List available scripts")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\nAvailable genres:")
            genres = list(Config.GENRE_PROMPTS.keys())
            for i, genre in enumerate(genres, 1):
                print(f"{i}. {genre.title()}")
            
            try:
                genre_choice = int(input(f"\nSelect genre (1-{len(genres)}) or 0 for random: "))
                if genre_choice == 0:
                    genre = random.choice(genres)
                elif 1 <= genre_choice <= len(genres):
                    genre = genres[genre_choice - 1]
                else:
                    print("❌ Invalid choice!")
                    continue
                
                generator.generate_video(genre=genre)
                
            except ValueError:
                print("❌ Please enter a valid number!")
        
        elif choice == "2":
            try:
                count = int(input("Enter number of videos to generate (1-5): "))
                if 1 <= count <= 5:
                    print("\nAvailable genres:")
                    genres = list(Config.GENRE_PROMPTS.keys())
                    for i, genre in enumerate(genres, 1):
                        print(f"{i}. {genre.title()}")
                    
                    genre_choice = int(input(f"\nSelect genre (1-{len(genres)}) or 0 for random: "))
                    if genre_choice == 0:
                        genre = random.choice(genres)
                    elif 1 <= genre_choice <= len(genres):
                        genre = genres[genre_choice - 1]
                    else:
                        print("❌ Invalid choice!")
                        continue
                    
                    generator.generate_batch(count=count, genre=genre)
                else:
                    print("❌ Please enter a number between 1 and 5!")
            except ValueError:
                print("❌ Please enter a valid number!")
        
        elif choice == "3":
            generator.continue_story()
        
        elif choice == "4":
            setup_api_keys()
        
        elif choice == "5":
            generator.list_available_scripts()
        
        elif choice == "6":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main() 