import numpy as np
import sounddevice as sd
import whisper

whisper_model = whisper.load_model("base")


def record_audio(duration=3, fs=16000):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    return np.squeeze(recording)


def transcribe_audio(audio):
    result = whisper_model.transcribe(audio, fp16=False)
    return result["text"].strip()
