#!/usr/bin/env python3
"""
API Configuration Helper
Use this to manage your API keys and switch between different providers
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

class APIConfig:
    def __init__(self):
        self.config_file = "api_keys.json"
        self.cohere_keys = []
        self.elevenlabs_keys = []
        self.preferred_ai_provider = "cohere"
        self.load_api_keys()
    
    def load_api_keys(self):
        """Load API keys from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.cohere_keys = data.get('cohere_keys', [])
                    self.elevenlabs_keys = data.get('elevenlabs_keys', [])
                    self.preferred_ai_provider = data.get('preferred_ai_provider', 'cohere')
            except Exception as e:
                print(f"Error loading API keys: {e}")
    
    def save_api_keys(self):
        """Save API keys to file"""
        try:
            data = {
                'cohere_keys': self.cohere_keys,
                'elevenlabs_keys': self.elevenlabs_keys,
                'preferred_ai_provider': self.preferred_ai_provider
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving API keys: {e}")
    
    def get_preferred_ai_key(self):
        """Get the preferred AI API key"""
        if self.preferred_ai_provider == "cohere" and self.cohere_keys:
            return self.cohere_keys[0]
        elif self.elevenlabs_keys:
            return self.elevenlabs_keys[0]
        return None
    
    def add_cohere_key(self, key):
        """Add a new Cohere API key"""
        if key not in self.cohere_keys:
            self.cohere_keys.append(key)
            self.save_api_keys()
            print("✅ Cohere API key added successfully!")
        else:
            print("⚠️  Cohere API key already exists!")
    
    def add_elevenlabs_key(self, key):
        """Add a new ElevenLabs API key"""
        if key not in self.elevenlabs_keys:
            self.elevenlabs_keys.append(key)
            self.save_api_keys()
            print("✅ ElevenLabs API key added successfully!")
        else:
            print("⚠️  ElevenLabs API key already exists!")
    
    def list_api_keys(self):
        """List all stored API keys"""
        print("\n📋 Stored API Keys:")
        print("-" * 40)
        
        if self.cohere_keys:
            print(f"Cohere Keys ({len(self.cohere_keys)}):")
            for i, key in enumerate(self.cohere_keys, 1):
                print(f"  {i}. {key[:10]}...{key[-4:]}")
        else:
            print("No Cohere keys stored")
        
        if self.elevenlabs_keys:
            print(f"\nElevenLabs Keys ({len(self.elevenlabs_keys)}):")
            for i, key in enumerate(self.elevenlabs_keys, 1):
                print(f"  {i}. {key[:10]}...{key[-4:]}")
        else:
            print("No ElevenLabs keys stored")
        
        print(f"\nPreferred AI Provider: {self.preferred_ai_provider}")
    
    def remove_api_key(self, provider, index):
        """Remove an API key"""
        try:
            if provider == "cohere" and 0 <= index < len(self.cohere_keys):
                removed_key = self.cohere_keys.pop(index)
                self.save_api_keys()
                print(f"✅ Removed Cohere key: {removed_key[:10]}...{removed_key[-4:]}")
            elif provider == "elevenlabs" and 0 <= index < len(self.elevenlabs_keys):
                removed_key = self.elevenlabs_keys.pop(index)
                self.save_api_keys()
                print(f"✅ Removed ElevenLabs key: {removed_key[:10]}...{removed_key[-4:]}")
            else:
                print("❌ Invalid key index")
        except Exception as e:
            print(f"❌ Error removing key: {e}")
    
    def switch_ai_provider(self):
        """Switch between AI providers"""
        self.preferred_ai_provider = "elevenlabs" if self.preferred_ai_provider == "cohere" else "cohere"
        self.save_api_keys()
        print(f"✅ Switched to {self.preferred_ai_provider}")

# Global instance
api_config = APIConfig()

def setup_api_keys():
    """Interactive setup for API keys"""
    print("🔑 API Key Setup")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Add Cohere API key")
        print("2. Add ElevenLabs API key")
        print("3. List all API keys")
        print("4. Remove API key")
        print("5. Switch AI provider")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            key = input("Enter Cohere API key: ").strip()
            if key:
                api_config.add_cohere_key(key)
            else:
                print("❌ Invalid key")
        
        elif choice == "2":
            key = input("Enter ElevenLabs API key: ").strip()
            if key:
                api_config.add_elevenlabs_key(key)
            else:
                print("❌ Invalid key")
        
        elif choice == "3":
            api_config.list_api_keys()
        
        elif choice == "4":
            api_config.list_api_keys()
            provider = input("Enter provider (cohere/elevenlabs): ").strip().lower()
            if provider in ["cohere", "elevenlabs"]:
                try:
                    index = int(input("Enter key index (0-based): ").strip())
                    api_config.remove_api_key(provider, index)
                except ValueError:
                    print("❌ Invalid index")
            else:
                print("❌ Invalid provider")
        
        elif choice == "5":
            api_config.switch_ai_provider()
        
        elif choice == "6":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

def add_api_key():
    """Quick add API key"""
    print("🔑 Quick API Key Addition")
    print("=" * 30)
    
    provider = input("Enter provider (cohere/elevenlabs): ").strip().lower()
    key = input("Enter API key: ").strip()
    
    if not key:
        print("❌ Invalid key")
        return
    
    if provider == "cohere":
        api_config.add_cohere_key(key)
    elif provider == "elevenlabs":
        api_config.add_elevenlabs_key(key)
    else:
        print("❌ Invalid provider")

def set_ai_provider():
    """Set the preferred AI provider (only Cohere is supported)"""
    print("\n🤖 Set AI Provider")
    print("=" * 20)
    print("Only Cohere is supported as AI provider.")
    api_config.preferred_ai_provider = "cohere"

if __name__ == "__main__":
    setup_api_keys() 