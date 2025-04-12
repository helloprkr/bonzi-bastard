#!/usr/bin/env python3
"""
Test script to verify Claude API is working properly
"""

import os
import sys
import yaml
import json
import time

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("ERROR: Anthropic SDK not installed. Run: pip install anthropic")
    ANTHROPIC_AVAILABLE = False
    sys.exit(1)

def load_config():
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        print(f"Error loading config.yaml: {e}")
        return {
            "anthropic_api_key": "",
            "model": "claude-3-haiku-20240307",
            "temp": 1.0,
            "max_tokens": 150,
            "api_enabled": True
        }

def test_claude_api():
    print("Testing Claude API connection...")
    
    # Load configuration
    config = load_config()
    
    # Check if API is enabled
    if not config.get("api_enabled", True):
        print("ERROR: API is disabled in config.yaml")
        return False
    
    # Check API key
    api_key = config.get("anthropic_api_key", "")
    if not api_key:
        print("ERROR: Missing API key in config.yaml")
        return False
    
    # Initialize Anthropic client
    try:
        client = Anthropic(api_key=api_key)
        print(f"Initialized Anthropic client")
    except Exception as e:
        print(f"ERROR initializing Anthropic client: {e}")
        return False
    
    # Get model from config
    model = config.get("model", "claude-3-haiku-20240307")
    print(f"Using model: {model}")
    
    # Define system prompt
    system_prompt = """
    You are BonziBuddy, a sassy desktop assistant.
    
    Respond with JSON in the following format:
    {
      "dialogue": "Your response here with some snark",
      "wave": true/false,
      "backflip": true/false
    }
    
    Choose 0-1 animations that match your mood.
    """
    
    # Send a test message
    print("Sending test message to Claude API...")
    start_time = time.time()
    
    try:
        response = client.messages.create(
            model=model,
            max_tokens=100,
            temperature=1.0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": "Hello! Tell me a fun fact about space."}
            ]
        )
        
        elapsed = time.time() - start_time
        print(f"Received response in {elapsed:.2f} seconds")
        
        # Extract the response content
        if not hasattr(response, 'content') or not response.content:
            print("ERROR: No content in response")
            print(f"Raw response: {response}")
            return False
        
        response_text = response.content[0].text
        print(f"Raw response: {response_text}")
        
        # Try to extract JSON
        import re
        json_match = re.search(r'({[\s\S]*})', response_text)
        if json_match:
            try:
                json_str = json_match.group(1)
                json_data = json.loads(json_str)
                print(f"Parsed JSON: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError:
                print("WARNING: Could not parse JSON in response")
        else:
            print("WARNING: No JSON found in response")
        
        print("\nAPI TEST SUCCESSFUL! Claude API is working properly.")
        return True
        
    except Exception as e:
        print(f"ERROR during API call: {e}")
        return False

if __name__ == "__main__":
    if not ANTHROPIC_AVAILABLE:
        print("Anthropic SDK not available. Please install it with: pip install anthropic")
        sys.exit(1)
    
    success = test_claude_api()
    sys.exit(0 if success else 1)