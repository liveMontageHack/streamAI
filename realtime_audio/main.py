import numpy as np
from transcription import Transcription
from audio_capture import start_stream
from refinement import refine_transcription
from console_ui import prompt_message
import os


def main():
    # Check if Groq API key is available
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("Warning: GROQ_API_KEY environment variable not set.")
        print("Refinement will be skipped unless you configure it in the web interface settings.")
        print("You can set the environment variable or use the web interface at http://localhost:5001")
        print()

    trans = Transcription()

    def audiostream_callback(audio_chunk):
        trans.add_audio(audio_chunk.astype(np.float32))

    stream = start_stream(audiostream_callback, blocksize=3000, device=1)

    user_prompt = prompt_message()

    try:
        while True:
            raw_output = trans.get_next_transcription()
            if raw_output:
                try:
                    refined = refine_transcription(raw_output, user_prompt)
                    print("[Stream: Groq] Refined:", refined + "\n")
                except Exception as e:
                    error_msg = str(e)
                    if "No Groq API key available" in error_msg:
                        print("[Stream] Groq API key not configured, showing raw transcription:", raw_output + "\n")
                    else:
                        print(f"[Stream] Refinement error: {error_msg}")
                        print("[Stream] Raw transcription:", raw_output + "\n")

    except KeyboardInterrupt:
        print("Stopping...")
        trans.stop()
        stream.stop()


if __name__ == "__main__":
    main()
