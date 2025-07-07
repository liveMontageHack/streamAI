import sounddevice as sd

print("Available audio devices:")
print(sd.query_devices())

print("\nDefault device indices [input, output]:")
print(sd.default.device)

def start_stream(callback, samplerate=16000, blocksize=0, device=None):
    print(f"audio sample captured.")
    def audio_callback(input_data, frames, time, status):
        if status:
            print(f"stream status': {status}" )
        audio = input_data[:, 0]
        callback(audio.copy())  # copy audio chunk

    if device is None:
        device = sd.query_devices(kind="input")["name"]

    stream = sd.InputStream(callback=audio_callback,samplerate=samplerate, blocksize=blocksize, channels=1, device=device)
    stream.start()
    return stream
