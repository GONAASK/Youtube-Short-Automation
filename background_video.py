import os
import random
import datetime
from config import Config

class BackgroundVideoManager:
    def __init__(self):
        self.background_dir = "assets/backgrounds"
        # User should specify their own background video path
        self.local_background = Config.BACKGROUND_VIDEOS[0] if Config.BACKGROUND_VIDEOS else None
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs(self.background_dir, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    def get_random_background(self, target_duration=None, video_id=None):
        """Get background video - create unique processed video for each request"""
        # Generate unique filename with timestamp and video ID
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        if video_id:
            filename = f"processed_background_{video_id}_{timestamp}.mp4"
        else:
            filename = f"processed_background_{timestamp}.mp4"
        
        output_path = os.path.join(self.background_dir, filename)
        
        # Always create a new processed background
        if self.local_background and os.path.exists(self.local_background):
            print(f"Processing local video for YouTube Shorts (unique: {filename})...")
            self.process_video_for_shorts(self.local_background, output_path, target_duration)
        else:
            print("Local video not found, creating animated background...")
            self.create_animated_background(output_path)
        
        return output_path
    
    def create_animated_background(self, output_path):
        """Create an animated background video"""
        try:
            from moviepy.editor import ColorClip, CompositeVideoClip
            import numpy as np
            
            # Create a base color clip with random colors for uniqueness
            base_clip = ColorClip(
                size=(Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT),
                color=(random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)),
                duration=Config.MAX_DURATION
            )
            
            # Add some animated elements (simple moving shapes)
            def make_frame(t):
                # Create a frame with moving gradient
                frame = np.zeros((Config.VIDEO_HEIGHT, Config.VIDEO_WIDTH, 3), dtype=np.uint8)
                
                # Create moving gradient effect with random seed for uniqueness
                seed = hash(output_path) % 1000  # Use output path as seed for consistency
                random.seed(seed)
                
                for y in range(Config.VIDEO_HEIGHT):
                    for x in range(Config.VIDEO_WIDTH):
                        # Moving gradient based on time with unique pattern
                        intensity = int(128 + 64 * np.sin(t * 0.5 + x * 0.01 + y * 0.01 + seed * 0.1))
                        frame[y, x] = [intensity, intensity//2, intensity//3]
                
                return frame
            
            animated_clip = ColorClip(
                size=(Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT),
                color=(0, 0, 0),
                duration=Config.MAX_DURATION
            ).set_make_frame(make_frame)
            
            # Combine clips
            final_clip = CompositeVideoClip([base_clip, animated_clip])
            
            final_clip.write_videofile(
                output_path,
                fps=Config.VIDEO_FPS,
                codec='libx264',
                verbose=False,
                logger=None
            )
            
            final_clip.close()
            print(f"Animated background created: {output_path}")
            
        except Exception as e:
            print(f"Error creating animated background: {e}")
            # Fallback to simple color clip
            self.create_simple_background(output_path)

    def create_simple_background(self, output_path):
        """Create a simple colored background"""
        try:
            from moviepy.editor import ColorClip
            
            clip = ColorClip(
                size=(Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT),
                color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                duration=Config.MAX_DURATION
            )
            
            clip.write_videofile(output_path, fps=Config.VIDEO_FPS, verbose=False, logger=None)
            print(f"Simple background created: {output_path}")
            
        except Exception as e:
            print(f"Error creating simple background: {e}")

    def process_video_for_shorts(self, input_path, output_path, target_duration=None):
        """Process video to extract random segment and convert to 9:16 for YouTube Shorts"""
        try:
            from moviepy.editor import VideoFileClip
            video = VideoFileClip(input_path)
            total_duration = video.duration
            
            # Use target duration if provided, otherwise use Config.MAX_DURATION
            if target_duration is None:
                target_duration = Config.MAX_DURATION
            
            # Ensure target duration doesn't exceed video length
            target_duration = min(target_duration, total_duration)
            
            # Calculate maximum start time to ensure we can extract the full target duration
            max_start_time = max(0, total_duration - target_duration)
            
            # Extract random segment with more randomness for uniqueness
            if max_start_time > 0:
                # Use output path as seed for consistent but unique randomness
                random.seed(hash(output_path) % 10000)
                start_time = random.uniform(0, max_start_time)
            else:
                start_time = 0
                
            end_time = start_time + target_duration
            segment = video.subclip(start_time, end_time)
            
            # Convert to 9:16 aspect ratio for YouTube Shorts
            w, h = segment.size
            target_w, target_h = Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT
            
            # Calculate crop dimensions to maintain aspect ratio
            if w / h > target_w / target_h:
                # Video is wider than 9:16, crop width
                new_w = int(h * target_w / target_h)
                x1 = (w - new_w) // 2
                segment = segment.crop(x1=x1, y1=0, x2=x1+new_w, y2=h)
            elif w / h < target_w / target_h:
                # Video is taller than 9:16, crop height
                new_h = int(w * target_h / target_w)
                y1 = (h - new_h) // 2
                segment = segment.crop(x1=0, y1=y1, x2=w, y2=y1+new_h)
            
            # Resize to exact dimensions
            segment = segment.resize((target_w, target_h))
            
            # Write processed video
            print(f"Processing video segment from {start_time:.1f}s to {end_time:.1f}s...")
            segment.write_videofile(
                output_path,
                fps=Config.VIDEO_FPS,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            video.close()
            segment.close()
            print(f"Background video processed for YouTube Shorts: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error processing background video: {e}")
            return self.create_animated_background(output_path)
    
    def download_sample_backgrounds(self):
        """No-op: Always use local video."""
        pass
    
    def cleanup_old_videos(self, max_files=10):
        """Clean up old background videos to save space"""
        try:
            import glob
            background_files = glob.glob(os.path.join(self.background_dir, "processed_background_*.mp4"))
            
            if len(background_files) > max_files:
                # Sort by modification time (oldest first)
                background_files.sort(key=os.path.getmtime)
                
                # Remove oldest files
                files_to_remove = background_files[:-max_files]
                for file_path in files_to_remove:
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up old background: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"Error removing {file_path}: {e}")
                        
        except Exception as e:
            print(f"Error cleaning up old videos: {e}") 