import numpy as np
from transcription import Transcription
from audio_capture import start_stream
from refinement import refine_transcription
from console_ui import prompt_message


def main():
    trans = Transcription()

    def audiostream_callback(audio_chunk):
        trans.add_audio(audio_chunk.astype(np.float32))

    stream = start_stream(audiostream_callback, blocksize=3000, device=1)

    user_prompt = prompt_message()

    try:
        while True:
            raw_output = trans.get_next_transcription()
            if raw_output:
                refined = refine_transcription(raw_output, user_prompt)
                print("[Stream: Groq] Refined:", refined + "\n")

    except KeyboardInterrupt:
        print("Stopping...")
        trans.stop()
        stream.stop()


if __name__ == "__main__":
    main()
