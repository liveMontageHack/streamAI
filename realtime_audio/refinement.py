import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def refine_transcription(raw_output, prompt_message):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                'role' : 'system',
                'content' : prompt_message # the prompt from the user
            },
            {
                'role' : 'user',
                'content' : raw_output  # the text coming from the input device
            }
        ],
        model = 'llama-3.3-70b-versatile'
    )
    return chat_completion.choices[0].message.content

