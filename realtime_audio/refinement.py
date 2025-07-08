import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def refine_transcription(raw_output, prompt_message):
    # Enhanced system message to prevent questions and ensure clean transcription
    system_message = f"""You are a professional transcription editor. Your task is to clean up audio transcriptions.

{prompt_message}

IMPORTANT RULES:
- Respond ONLY with the corrected transcription text
- Do NOT ask questions or provide explanations
- Do NOT add commentary or analysis
- Keep the original meaning intact
- Focus only on grammar, spelling, punctuation, and clarity improvements"""

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

