# Auto AI Video Generator

An automated system for generating engaging story videos with AI voiceovers, background videos, and subtitles. Perfect for creating YouTube Shorts and social media content.

## Features

- 🤖 **AI Story Generation**: Create unique, viral-worthy stories using Cohere AI
- 🎤 **AI Voice Generation**: Generate natural-sounding voiceovers with ElevenLabs
- 🎬 **Background Video Processing**: Unique background videos for each story
- 📝 **Automatic Subtitles**: Clean, readable subtitles for better engagement
- 📚 **Story Continuation**: Continue existing stories with new parts
- 🎯 **Multiple Genres**: AITA, Confessions, Horror, Malicious Compliance, Inspiring
- 📱 **YouTube Shorts Optimized**: 9:16 aspect ratio, 30-60 second duration
**CAPTIONS ARE STILL IN TESTING PHASE**
## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install ImageMagick (Required for Subtitles)

**Windows:**
1. Download ImageMagick from [https://imagemagick.org/script/download.php#windows](https://imagemagick.org/script/download.php#windows)
2. Install with default settings
3. Set environment variable in your script:
   ```python
   os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
   ```

**macOS:**
```bash
brew install imagemagick
```

**Linux:**
```bash
sudo apt-get install imagemagick
```

### 3. Configure API Keys

Run the API configuration script:
```bash
python api_config.py
```

Or add your API keys directly:
```bash
python -c "from api_config import api_config; api_config.add_cohere_key('your-cohere-key'); api_config.add_elevenlabs_key('your-elevenlabs-key')"
```

### 4. Add Background Video

1. Place your background video file in the project directory
2. Update the path in `config.py`:
   ```python
   BACKGROUND_VIDEOS = [
       "path/to/your/background/video.mp4"
   ]
   ```

## Usage

### Generate a Single Video

```bash
python main.py
```

Then select:
1. Generate single video
2. Choose genre
3. Wait for generation to complete

### Generate Multiple Videos

```bash
python main.py
```

Then select:
1. Generate batch videos
2. Enter number of videos (1-5)
3. Choose genre
4. Wait for batch generation

### Continue Existing Story

```bash
python main.py
```

Then select:
1. Continue existing story
2. Choose from available scripts
3. Generate continuation

## Configuration

### Video Settings

Edit `config.py` to customize:
- Video dimensions (default: 1080x1920 for Shorts)
- Maximum duration (default: 60 seconds)
- Voice settings
- Genre prompts

### API Keys

- **Cohere**: Get from [https://cohere.com/](https://cohere.com/)
- **ElevenLabs**: Get from [https://elevenlabs.io/](https://elevenlabs.io/)

## File Structure

```
Auto AI video/
├── main.py                 # Main application
├── config.py              # Configuration settings
├── api_config.py          # API key management
├── story_generator.py     # AI story generation
├── voice_generator.py     # AI voice generation
├── background_video.py    # Background video processing
├── video_editor.py        # Video creation and editing
├── subtitle_assemblyai.py # Subtitle generation
├── requirements.txt       # Python dependencies
├── output/               # Generated videos
├── scripts/              # Saved story scripts
├── temp/                 # Temporary files
└── assets/               # Background videos and assets
```

## Output

- **Videos**: Saved in `output/` directory
- **Scripts**: Saved in `scripts/` directory as JSON files
- **Temporary files**: Automatically cleaned up

## Troubleshooting

### Subtitles Not Showing
- Ensure ImageMagick is installed and path is set correctly
- Check that the binary path in `subtitle_assemblyai.py` matches your installation

### API Errors
- Verify API keys are valid and have sufficient credits
- Check rate limits and quotas
- Use the API configuration tool to manage multiple keys

### Video Generation Issues
- Ensure background video file exists and is accessible
- Check available disk space for temporary files
- Verify all dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Disclaimer

This tool is for educational and content creation purposes. Ensure you comply with all applicable terms of service for the APIs used (Cohere, ElevenLabs) and respect copyright laws when using background videos. 
