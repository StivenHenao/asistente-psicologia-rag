import numpy as np
import sounddevice as sd
import whisper

model = whisper.load_model("base")  # O tiny/small/medium/large


def record_and_transcribe(duration=3, fs=16000):
    """Graba audio y devuelve la transcripción como texto."""
    print("Por favor, diga su código de voz de 4 dígitos...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    audio = np.squeeze(recording)
    result = model.transcribe(audio, fp16=False)
    code_spoken = "".join(filter(str.isdigit, result["text"]))
    if len(code_spoken) != 4:
        print(f"Código detectado inválido: {code_spoken}")
        return None

    print(f"Transcripción detectada: {code_spoken}")
    return code_spoken
