import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from config import Config
from subtitle_assemblyai import SubtitleGenerator

class VideoEditor:
    def __init__(self):
        self.subtitle_generator = SubtitleGenerator()
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
    def create_video_with_subtitles(self, audio_path, background_path, story_text, video_id):
        """Create final video with subtitles"""
        try:
            print("🎬 Creating video with subtitles...")
            
            # Load audio and background
            audio_clip = AudioFileClip(audio_path)
            background_clip = VideoFileClip(background_path)
            
            # Get audio duration
            audio_duration = audio_clip.duration
            
            # Trim background to match audio duration
            if background_clip.duration > audio_duration:
                background_clip = background_clip.subclip(0, audio_duration)
            else:
                # Loop background if it's shorter than audio
                loops_needed = int(audio_duration / background_clip.duration) + 1
                background_clip = background_clip.loop(loops_needed).subclip(0, audio_duration)
            
            # Resize background to match target dimensions
            background_clip = background_clip.resize((Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT))
            
            # Set audio
            background_clip = background_clip.set_audio(audio_clip)
            
            # Generate output filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_filename = f"{video_id}_{timestamp}.mp4"
            output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
            
            # Create video with subtitles
            final_video = self.subtitle_generator.add_subtitles_to_video(
                background_clip, 
                story_text, 
                output_path
            )
            
            # Clean up
            audio_clip.close()
            background_clip.close()
            
            if final_video:
                print(f"✅ Video created successfully: {output_path}")
                return output_path
            else:
                print("❌ Failed to create video with subtitles")
                return None
                
        except Exception as e:
            print(f"❌ Error creating video: {e}")
            return None
    
    def create_video(self, background_path, audio_path, output_path):
        """Create basic video without subtitles (legacy method)"""
        try:
            print("🎬 Creating basic video...")
            
            # Load clips
            audio_clip = AudioFileClip(audio_path)
            background_clip = VideoFileClip(background_path)
            
            # Get audio duration
            audio_duration = audio_clip.duration
            
            # Trim background to match audio duration
            if background_clip.duration > audio_duration:
                background_clip = background_clip.subclip(0, audio_duration)
            else:
                # Loop background if it's shorter than audio
                loops_needed = int(audio_duration / background_clip.duration) + 1
                background_clip = background_clip.loop(loops_needed).subclip(0, audio_duration)
            
            # Resize background to match target dimensions
            background_clip = background_clip.resize((Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT))
            
            # Set audio
            final_video = background_clip.set_audio(audio_clip)
            
            # Write video
            final_video.write_videofile(
                output_path,
                fps=Config.VIDEO_FPS,
                codec='libx264',
                audio_codec='aac'
            )
            
            # Clean up
            audio_clip.close()
            background_clip.close()
            final_video.close()
            
            print(f"✅ Basic video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error creating basic video: {e}")
            return None
    
    def add_watermark(self, video_path, watermark_text):
        """Add watermark to video (disabled as requested)"""
        print("💧 Watermark feature is disabled")
        return video_path
    
    def get_video_duration(self, video_path):
        """Get video duration"""
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            return duration
        except:
            return 0 