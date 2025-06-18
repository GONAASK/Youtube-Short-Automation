import os
import json
import time
import datetime
import uuid
import random
import cohere
from config import Config
from api_config import api_config

class StoryGenerator:
    def __init__(self):
        self.cohere_client = None
        self.update_cohere_client()
        self.ensure_directories()
    
    def update_cohere_client(self):
        """Update Cohere client with current API key"""
        cohere_key = api_config.get_preferred_ai_key()
        if cohere_key:
            self.cohere_client = cohere.Client(cohere_key)
        else:
            self.cohere_client = None
    
    def ensure_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs("scripts", exist_ok=True)
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    def generate_story(self, genre="inspiring"):
        """Generate a complete story with engaging hook"""
        if not self.cohere_client:
            print("❌ No Cohere API key configured!")
            return None
        
        try:
            # Get genre-specific prompts
            genre_prompts = Config.GENRE_PROMPTS.get(genre, Config.GENRE_PROMPTS["inspiring"])
            prompt = random.choice(genre_prompts)
            
            # Add powerful hook instruction
            hook_instruction = self.get_hook_instruction(genre)
            full_prompt = f"{hook_instruction}\n\n{prompt}"
            
            print(f"📝 Generating {genre} story with engaging hook...")
            
            response = self.cohere_client.generate(
                model=Config.COHERE_MODEL,
                prompt=full_prompt,
                max_tokens=800,
                temperature=0.8,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            story_text = response.generations[0].text.strip()
            
            if not story_text:
                print("❌ No story generated!")
                return None
            
            # Clean the story
            cleaned_story = self.clean_story_text(story_text)
            
            # Generate unique video ID
            video_id = str(uuid.uuid4())[:8]
            
            # Create story data
            story_data = {
                'story': cleaned_story,
                'genre': genre,
                'video_id': video_id,
                'title': self.generate_title(cleaned_story),
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'hook_type': self.get_hook_type(genre)
            }
            
            # Save script
            self.save_script(story_data)
            
            print(f"✅ Story generated successfully! ID: {video_id}")
            return story_data
            
        except Exception as e:
            print(f"❌ Error generating story: {e}")
            
            # Try to switch API key if available
            if len(api_config.cohere_keys) > 1:
                print("🔄 Trying alternative API key...")
                api_config.cohere_keys.append(api_config.cohere_keys.pop(0))
                self.update_cohere_client()
                return self.generate_story(genre)
            
            return None
    
    def generate_continuation(self, continuation_id):
        """Generate a continuation of an existing story"""
        if not self.cohere_client:
            print("❌ No Cohere API key configured!")
            return None
        
        try:
            # Load the original story
            original_script = self.load_script_by_id(continuation_id)
            if not original_script:
                print(f"❌ No script found with ID: {continuation_id}")
                return None
            
            original_story = original_script['story']
            genre = original_script['genre']
            
            # Create continuation prompt
            continuation_prompt = f"""
            This is a continuation of a {genre} story. The original story was:
            
            "{original_story}"
            
            Now write the next part of this story. Make it engaging and continue the narrative naturally. 
            Keep it around 60 seconds when read aloud. Make sure it has a satisfying continuation that builds on the original story.
            """
            
            print(f"📝 Generating continuation of {genre} story...")
            
            response = self.cohere_client.generate(
                model=Config.COHERE_MODEL,
                prompt=continuation_prompt,
                max_tokens=800,
                temperature=0.8,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            continuation_text = response.generations[0].text.strip()
            
            if not continuation_text:
                print("❌ No continuation generated!")
                return None
            
            # Clean the continuation
            cleaned_continuation = self.clean_story_text(continuation_text)
            
            # Generate new video ID for continuation
            video_id = str(uuid.uuid4())[:8]
            
            # Create continuation data
            continuation_data = {
                'story': cleaned_continuation,
                'genre': genre,
                'video_id': video_id,
                'title': f"Continuation: {original_script['title']}",
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'original_id': continuation_id,
                'is_continuation': True
            }
            
            # Save continuation script
            self.save_script(continuation_data)
            
            print(f"✅ Continuation generated successfully! ID: {video_id}")
            return continuation_data
            
        except Exception as e:
            print(f"❌ Error generating continuation: {e}")
            return None
    
    def get_hook_instruction(self, genre):
        """Get genre-specific hook instruction"""
        hooks = {
            "aita": "Start with a shocking revelation or controversial statement that immediately grabs attention. Use phrases like 'You won't believe what happened next' or 'This changed everything'.",
            "confessions": "Begin with a surprising admission or secret that creates instant curiosity. Use phrases like 'I've been hiding this for years' or 'What I'm about to tell you will shock you'.",
            "horror": "Start with an eerie atmosphere or unexplained event that creates tension. Use phrases like 'Something wasn't right' or 'I should have known better'.",
            "malicious_compliance": "Begin with a situation where someone follows rules to the extreme with unexpected results. Use phrases like 'I did exactly what they asked' or 'They got what they wanted, but not what they expected'.",
            "inspiring": "Start with a relatable problem or challenge that everyone faces. Use phrases like 'We've all been there' or 'This moment changed everything'."
        }
        return hooks.get(genre, hooks["inspiring"])
    
    def get_hook_type(self, genre):
        """Get the type of hook used"""
        hook_types = {
            "aita": "controversial_statement",
            "confessions": "surprising_admission", 
            "horror": "eerie_atmosphere",
            "malicious_compliance": "rule_following_extreme",
            "inspiring": "relatable_problem"
        }
        return hook_types.get(genre, "relatable_problem")
    
    def generate_title(self, story):
        """Generate a title from the story"""
        # Take first sentence or first 50 characters
        lines = story.split('\n')
        first_line = lines[0].strip()
        
        if len(first_line) > 50:
            title = first_line[:50] + "..."
        else:
            title = first_line
        
        return title
    
    def clean_story_text(self, text):
        """Clean story text for better processing"""
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
        
        # Remove extra spaces
        cleaned_text = ' '.join(cleaned_text.split())
        
        # Ensure it ends with proper punctuation
        if cleaned_text and not cleaned_text[-1] in '.!?':
            cleaned_text += '.'
        
        return cleaned_text
    
    def save_script(self, story_data):
        """Save story script to file"""
        try:
            filename = f"script_{story_data['video_id']}_{int(time.time())}.json"
            filepath = os.path.join("scripts", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(story_data, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Script saved: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving script: {e}")
    
    def load_script_by_id(self, video_id):
        """Load script by video ID"""
        try:
            scripts_dir = "scripts"
            if not os.path.exists(scripts_dir):
                return None
            
            for filename in os.listdir(scripts_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(scripts_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('video_id') == video_id:
                            return data
            
            return None
            
        except Exception as e:
            print(f"❌ Error loading script: {e}")
            return None
    
    def list_available_stories(self):
        """List all available story scripts"""
        try:
            scripts_dir = "scripts"
            if not os.path.exists(scripts_dir):
                return []
            
            scripts = []
            for filename in os.listdir(scripts_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(scripts_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            scripts.append({
                                'filename': filename,
                                'path': filepath,
                                'data': data,
                                'modified': datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                            })
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
            
            # Sort by modification time (newest first)
            scripts.sort(key=lambda x: x['modified'], reverse=True)
            return scripts
            
        except Exception as e:
            print(f"❌ Error listing stories: {e}")
            return []
    
    def get_available_genres(self):
        """Get list of available genres"""
        return list(Config.GENRE_PROMPTS.keys()) 