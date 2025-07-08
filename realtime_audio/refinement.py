import os
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_groq_api_key():
    """Get Groq API key from settings API or environment variable"""
    try:
        # Determine API URL based on environment
        api_base_url = os.environ.get('API_BASE_URL', 'http://localhost:5001')
        
        # First try to get from settings API
        response = requests.get(f'{api_base_url}/api/settings', timeout=2)
        if response.status_code == 200:
            settings = response.json().get('settings', {})
            groq_key = settings.get('groq_api_key')
            if groq_key and groq_key != "••••••••••••••••••••••••••••••••••••••••":
                return groq_key
    except:
        pass
    
    # Fallback to environment variable
    return os.environ.get("GROQ_API_KEY")

def refine_transcription(raw_output, prompt_message, api_key=None):
    """Refine transcription using Groq API"""
    # Use provided API key or get from settings/environment
    groq_api_key = api_key or get_groq_api_key()
    
    if not groq_api_key:
        raise Exception("No Groq API key available. Please configure it in Settings or set GROQ_API_KEY environment variable.")
    
    client = Groq(
        api_key=groq_api_key,
    )
    
    # Enhanced system message to prevent questions and ensure clean transcription
    system_message = f"""You are a professional transcription editor. Your task is to clean up audio transcriptions.

{prompt_message}

IMPORTANT RULES:
- Respond ONLY with the corrected transcription text
- Do NOT ask questions or provide explanations
- Do NOT add commentary or analysis
- Keep the original meaning intact
- Focus only on grammar, spelling, punctuation, and clarity improvements"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    'role' : 'system',
                    'content' : system_message
                },
                {
                    'role' : 'user',
                    'content' : f"Please clean up this transcription: {raw_output}"
                }
            ],
            model = 'llama-3.1-8b-instant'  # Faster, less congested model
        )
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        error_msg = str(e).lower()
        
        # Provide more specific error messages
        if "invalid api key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
            raise Exception("Invalid Groq API key. Please check your API key in Settings.")
        elif "rate limit" in error_msg or "429" in error_msg:
            raise Exception("Groq API rate limit exceeded. Please try again later.")
        elif "over capacity" in error_msg or "503" in error_msg:
            raise Exception("Groq API is over capacity. Please try again in a moment.")
        elif "connection" in error_msg or "network" in error_msg or "timeout" in error_msg:
            raise Exception("Network error connecting to Groq API. Please check your internet connection.")
        else:
            raise Exception(f"Groq AI refinement failed: {str(e)}")

