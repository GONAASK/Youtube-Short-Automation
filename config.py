import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Cohere Configuration
    COHERE_API_KEY = os.getenv('COHERE_API_KEY', '')
    COHERE_MODEL = "command"  # Cohere's Command model for text generation
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')  # Default male voice
    
    # Video Configuration - Optimized for YouTube Shorts
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920  # 9:16 aspect ratio for Shorts
    VIDEO_FPS = 30
    MAX_DURATION = 60  # seconds (YouTube Shorts max is 60 seconds)
    
    # Output Configuration
    OUTPUT_DIR = "output"
    TEMP_DIR = "temp"
    
    # User Preferences
    PREFERRED_VOICE_TYPE = "male"
    BATCH_SIZE = 3  # 1-3 videos per session
    USE_WATERMARK = False  # No watermark as requested
    
    # Genre-specific Story Generation Prompts - Original content for YouTube monetization
    GENRE_PROMPTS = {
        "aita": [
            "Write a 60-second original story about someone questioning if they were wrong in a situation. Make it relatable and family-friendly, suitable for all audiences.",
            "Create a short original story about a moral dilemma where the person wonders if they made the right choice. Keep it clean and thought-provoking.",
            "Write an original story about a conflict where the person seeks validation about their actions. Make it engaging without being controversial.",
            "Generate an original story about someone questioning their behavior in a social situation. Keep it wholesome and relatable.",
            "Create an original story about a person wondering if they overreacted to something. Make it entertaining and suitable for all ages."
        ],
        "confessions": [
            "Write a 60-second original story about someone sharing a secret or hidden truth. Make it light-hearted and family-friendly.",
            "Create a short original story about someone revealing something they've kept hidden. Keep it positive and uplifting.",
            "Write an original story about someone confessing to a small mistake or misunderstanding. Make it relatable and humorous.",
            "Generate an original story about someone sharing a surprising revelation. Keep it clean and entertaining.",
            "Create an original story about someone admitting to an embarrassing but harmless situation. Make it funny and wholesome."
        ],
        "horror": [
            "Write a 60-second original story about a spooky but not terrifying experience. Make it family-friendly and more mystery than horror.",
            "Create a short original story about an unexplained event that turns out to have a logical explanation. Keep it suitable for all audiences.",
            "Write an original story about someone's imagination playing tricks on them. Make it light-hearted and not scary.",
            "Generate an original story about a mysterious situation that gets resolved positively. Keep it engaging but not frightening.",
            "Create an original story about a 'haunted' place that turns out to be something else entirely. Make it fun and family-safe."
        ],
        "malicious_compliance": [
            "Write a 60-second original story about someone following rules exactly as written with unexpected results. Make it clever and family-friendly.",
            "Create a short original story about someone technically following instructions but not as intended. Keep it humorous and clean.",
            "Write an original story about someone using the letter of the law against itself. Make it smart and entertaining.",
            "Generate an original story about someone following directions literally with funny consequences. Keep it light-hearted and positive.",
            "Create an original story about someone using rules creatively to solve a problem. Make it clever and inspiring."
        ],
        "inspiring": [
            "Write a 60-second original story about a relatable everyday situation with a surprising twist. Make it engaging and family-friendly.",
            "Create a short original story about a workplace misunderstanding that gets resolved in an unexpected way. Keep it clean and entertaining.",
            "Write an original story about a friendship challenge that teaches a valuable lesson. Make it inspiring and suitable for all audiences.",
            "Generate an original story about a family gathering that takes an unexpected turn. Keep it wholesome and relatable.",
            "Create a short original story about a neighborly dispute that gets resolved through kindness. Make it heartwarming and positive."
        ]
    }
    
    # Background video options - User should specify their own video file
    BACKGROUND_VIDEOS = [
        "path/to/your/background/video.mp4"  # Replace with your video path
    ] 