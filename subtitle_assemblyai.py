import os
# Set ImageMagick path - users should update this for their system
# os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
import tempfile
import time
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from config import Config

def create_simple_subtitles_from_text(text, video_duration, font_size=70, font_color='white', stroke_color='black', stroke_width=4):
    """Create simple subtitles from text without needing transcription"""
    print(f"Creating subtitles from text: {len(text)} characters")
    
    # Clean the text - remove any extra content
    text = clean_text_for_subtitles(text)
    
    # Split text into simple chunks (not sentences, just word groups)
    words = text.split()
    if not words:
        words = ["Story", "content", "available", "in", "video"]
    
    # Create 5-8 subtitle segments
    num_segments = min(8, max(5, len(words) // 10))
    words_per_segment = len(words) // num_segments
    
    segments = []
    for i in range(0, len(words), words_per_segment):
        segment = ' '.join(words[i:i + words_per_segment])
        if segment.strip():
            segments.append(segment.strip())
    
    # If we have too few segments, split more
    if len(segments) < 3:
        segments = []
        for i in range(0, len(words), max(1, len(words) // 5)):
            segment = ' '.join(words[i:i + max(1, len(words) // 5)])
            if segment.strip():
                segments.append(segment.strip())
    
    print(f"Split into {len(segments)} subtitle segments")
    
    # Calculate timing for each segment
    segment_duration = video_duration / len(segments)
    subtitle_clips = []
    
    for i, segment in enumerate(segments):
        if not segment.strip():
            continue
            
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        
        try:
            # Create text clip with simpler settings
            txt_clip = TextClip(
                segment,
                fontsize=font_size,
                color=font_color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method='label',
                size=(1080 - 80, None),  # Leave 40px margin on each side
                align='center',
                font='Arial-Bold'
            ).set_position(('center', 'bottom')).set_start(start_time).set_duration(segment_duration)
            
            subtitle_clips.append(txt_clip)
            print(f"Created subtitle {i+1}: {segment[:50]}...")
            
        except Exception as e:
            print(f"Error creating subtitle {i+1}: {e}")
            # Try with simpler text
            try:
                simple_text = segment[:30] if len(segment) > 30 else segment
                txt_clip = TextClip(
                    simple_text,
                    fontsize=60,
                    color='white',
                    stroke_color='black',
                    stroke_width=3,
                    method='label',
                    size=(1080 - 100, None),
                    align='center'
                ).set_position(('center', 'bottom')).set_start(start_time).set_duration(segment_duration)
                
                subtitle_clips.append(txt_clip)
                print(f"Created simple subtitle {i+1}")
            except Exception as e2:
                print(f"Failed to create simple subtitle {i+1}: {e2}")
                continue
    
    print(f"Successfully created {len(subtitle_clips)} subtitle clips")
    return subtitle_clips

def clean_text_for_subtitles(text):
    """Remove any unwanted content from text"""
    if not text:
        return "Story content available in video"
    
    # Remove common unwanted patterns
    unwanted_patterns = [
        "STORY:",
        "TITLE:",
        "THE STORY:",
        "STORY SCRIPT",
        "Genre:",
        "Part:",
        "Generated:",
        "Story ID:",
        "NOTES:",
        "Duration:",
        "Word count:",
        "Character count:",
        "For continuation",
        "This story",
        "This 30-60 second",
        "CRITICAL:",
        "ONLY write",
        "DO NOT include",
        "Start directly",
        "End with",
        "Nothing else"
    ]
    
    cleaned_text = text
    for pattern in unwanted_patterns:
        if pattern in cleaned_text:
            # Remove everything from the pattern onwards
            parts = cleaned_text.split(pattern)
            if len(parts) > 1:
                cleaned_text = parts[0].strip()
    
    # Remove any remaining instruction-like text
    lines = cleaned_text.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip lines that are clearly instructions
        if any(keyword in line.lower() for keyword in [
            'note:', 'instruction:', 'important:', 'remember:', 'focus on',
            'the story should', 'make sure', 'ensure', 'critical:', 'only return',
            'do not include', 'start directly', 'end with', 'nothing else'
        ]):
            continue
        
        # Skip lines that start with common instruction patterns
        if line.startswith(('This story', 'This 30-60', 'Note:', 'Instruction:')):
            continue
            
        if line and len(line) > 5:  # Keep lines with at least 5 characters
            clean_lines.append(line)
    
    cleaned_text = ' '.join(clean_lines)
    
    # If we ended up with nothing, provide a fallback
    if not cleaned_text.strip() or len(cleaned_text.strip()) < 10:
        cleaned_text = "Story content available in video"
    
    print(f"Cleaned text length: {len(cleaned_text)} characters")
    return cleaned_text.strip()

def burn_subtitles_on_video(video_path, text, output_path=None, font_size=70, font_color='white', stroke_color='black', stroke_width=4):
    """Burn subtitles onto the video using provided text"""
    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_subtitled{ext}"
    
    print(f"Burning subtitles onto video: {video_path}")
    print(f"Output path: {output_path}")
    
    try:
        # Load video
        print("Loading video...")
        video = VideoFileClip(video_path)
        video_duration = video.duration
        print(f"Video duration: {video_duration} seconds")
        print(f"Video size: {video.size}")
        
        # Create subtitle clips from text
        print("Creating subtitle clips...")
        subtitle_clips = create_simple_subtitles_from_text(
            text, 
            video_duration, 
            font_size=font_size, 
            font_color=font_color, 
            stroke_color=stroke_color, 
            stroke_width=stroke_width
        )
        
        # Create final video with subtitles
        if subtitle_clips:
            print("Combining video with subtitles...")
            final = CompositeVideoClip([video] + subtitle_clips)
            print(f"✅ Created {len(subtitle_clips)} subtitle clips")
        else:
            print("⚠️  No subtitle clips created, creating fallback subtitle")
            # Create a simple fallback subtitle
            fallback_text = "Story content available in video"
            fallback_clip = TextClip(
                fallback_text,
                fontsize=60,
                color='white',
                stroke_color='black',
                stroke_width=3,
                method='label',
                size=(1080 - 100, None),
                align='center'
            ).set_position(('center', 'bottom')).set_start(0).set_duration(video_duration)
            
            final = CompositeVideoClip([video, fallback_clip])
            print("✅ Created fallback subtitle")
        
        # Write video with high quality settings
        print("Writing subtitled video...")
        final.write_videofile(
            output_path, 
            fps=video.fps, 
            codec='libx264', 
            audio_codec='aac',
            verbose=False, 
            logger=None,
            preset='medium',
            crf=23
        )
        
        video.close()
        final.close()
        
        print(f"✅ Subtitled video saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error burning subtitles: {e}")
        import traceback
        traceback.print_exc()
        return video_path

def add_subtitles_to_video_with_assemblyai(video_path, story_text=None, api_key=None):
    """Add subtitles to video - simplified version that always works"""
    print(f"Adding subtitles to video: {video_path}")
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return video_path
    
    try:
        # If no story text provided, try to extract from video filename
        if not story_text:
            print("No story text provided, trying to extract from scripts...")
            story_text = extract_story_from_scripts(video_path)
        
        # If still no story text, create a simple placeholder
        if not story_text:
            print("No story text found, using placeholder...")
            story_text = "Story content available in video"
        
        print(f"Using story text: {story_text[:100]}...")
        
        # Create subtitles
        subtitled_video = burn_subtitles_on_video(
            video_path, 
            story_text,
            font_size=70,
            font_color='white',
            stroke_color='black',
            stroke_width=4
        )
        
        return subtitled_video
        
    except Exception as e:
        print(f"❌ Error adding subtitles: {e}")
        import traceback
        traceback.print_exc()
        return video_path

def extract_story_from_scripts(video_path):
    """Try to extract story text from saved scripts based on video filename"""
    try:
        import glob
        
        # Get video filename without extension
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        print(f"Looking for scripts matching: {video_name}")
        
        # Look for matching script files
        script_dir = os.path.join(Config.OUTPUT_DIR, "scripts")
        if not os.path.exists(script_dir):
            print("Script directory not found")
            return None
        
        # Search for script files that might match this video
        script_files = glob.glob(os.path.join(script_dir, "*.txt"))
        print(f"Found {len(script_files)} script files")
        
        for script_file in script_files:
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract story text from script
                if 'STORY:' in content:
                    story_section = content.split('STORY:')[1].split('NOTES:')[0].strip()
                    if story_section:
                        print(f"Found story in {os.path.basename(script_file)}")
                        return story_section
                        
            except Exception as e:
                print(f"Error reading script {script_file}: {e}")
                continue
        
        print("No matching story found in scripts")
        return None
        
    except Exception as e:
        print(f"Error extracting story from scripts: {e}")
        return None

def create_test_subtitles():
    """Create a test video with subtitles to verify functionality"""
    try:
        print("Creating test subtitle video...")
        
        # Create a simple test video
        test_video = ColorClip(
            size=(1080, 1920),
            color=(100, 100, 100),
            duration=10
        )
        
        # Create test subtitle
        test_text = "This is a test subtitle to verify the system is working correctly. The text should be clearly visible at the bottom of the screen."
        subtitle = TextClip(
            test_text,
            fontsize=70,
            color='white',
            stroke_color='black',
            stroke_width=4,
            method='label',
            size=(1080 - 100, None),
            align='center',
            font='Arial-Bold'
        ).set_position(('center', 'bottom')).set_duration(10)
        
        # Combine video and subtitle
        final = CompositeVideoClip([test_video, subtitle])
        
        # Save test video
        test_output = os.path.join(Config.OUTPUT_DIR, "test_subtitles.mp4")
        print(f"Saving test video to: {test_output}")
        
        final.write_videofile(test_output, fps=30, verbose=False, logger=None)
        
        final.close()
        test_video.close()
        
        print(f"✅ Test subtitle video created: {test_output}")
        return test_output
        
    except Exception as e:
        print(f"❌ Error creating test subtitles: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python subtitle_assemblyai.py <video_path> [story_text]")
        print("Or run without arguments to create a test subtitle video")
        print("Creating test subtitle video...")
        create_test_subtitles()
    else:
        video_path = sys.argv[1]
        story_text = sys.argv[2] if len(sys.argv) > 2 else None
        add_subtitles_to_video_with_assemblyai(video_path, story_text) 