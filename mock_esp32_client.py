import os
import time
import uuid
from urllib.parse import unquote

import numpy as np
import pygame
import requests
import scipy.io.wavfile as wav
import sounddevice as sd

API_URL = "http://127.0.0.1:8000/api/esp32/interact"
CLIENT_ID = "mock_client_001"

def record_audio(duration=5, fs=16000):
    print(f"🎤 Grabando {duration}s... (habla CLARO y FUERTE)")
    
    recording = sd.rec(
        int(duration * fs), 
        samplerate=fs, 
        channels=1,
        dtype="int16"
    )
    sd.wait()
    
    audio_float = recording.astype(np.float32) / 32768.0
    max_amp = np.max(np.abs(audio_float))
    rms = np.sqrt(np.mean(audio_float**2))
    
    print(f"⏹️ Grabación terminada.")
    print(f"   📊 Amplitud máxima: {max_amp:.4f}")
    
    if max_amp < 0.01:
        print("   ⚠️ ALERTA: Audio MUY bajo, casi silencio!")
    elif max_amp < 0.05:
        print("   ⚠️ Audio bajo, habla más fuerte")
    elif max_amp > 0.95:
        print("   ⚠️ Audio saturado, aleja el micrófono")
    
    return recording, fs

def save_audio(audio, fs, filename):
    wav.write(filename, fs, audio)
    print(f"💾 Audio guardado: {filename} ({os.path.getsize(filename)} bytes)")

def play_audio(filename):
    print("🔊 Reproduciendo respuesta...")
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()

def test_microphone():
    print("\n🎤 PRUEBA DE MICRÓFONO")
    print("=" * 50)
    
    default_input = sd.query_devices(kind='input')
    print(f"\n🎙️ Dispositivo de entrada por defecto: {default_input['name']}")
    
    input("\nPresiona ENTER para hacer una prueba de 3 segundos...")
    
    print("🎤 Habla ahora...")
    test_audio, fs = record_audio(duration=3)
    
    test_file = "test_mic.wav"
    save_audio(test_audio, fs, test_file)
    
    print(f"\n✅ Prueba completada. Archivo guardado: {test_file}")
    
    keep = input("\n¿Borrar archivo de prueba? (s/n): ")
    if keep.lower() == 's' and os.path.exists(test_file):
        os.remove(test_file)

def main():
    print("=" * 60)
    print("🤖 MOCK ESP32 CLIENT")
    print("=" * 60)
    print(f"Client ID: {CLIENT_ID}")
    
    do_test = input("\n¿Hacer prueba de micrófono primero? (s/n): ")
    if do_test.lower() == 's':
        test_microphone()
    
    print("\n" + "=" * 60)
    print("INICIANDO SESIÓN")
    print("=" * 60)
    
    current_duration = 5
    interaction_count = 0
    
    while True:
        try:
            interaction_count += 1
            print(f"\n{'─' * 60}")
            print(f"INTERACCIÓN #{interaction_count}")
            print(f"{'─' * 60}")
            
            input(f"Presiona ENTER para hablar ({current_duration}s)... ")
            
            audio_data, fs = record_audio(duration=current_duration)
            temp_wav = f"recording_{interaction_count}_{uuid.uuid4().hex[:6]}.wav"
            save_audio(audio_data, fs, temp_wav)
            
            print("\n📤 Enviando audio al servidor...")
            try:
                with open(temp_wav, "rb") as f:
                    files = {"audio_file": (temp_wav, f, "audio/wav")}
                    data = {"client_id": CLIENT_ID}
                    
                    start_time = time.time()
                    response = requests.post(API_URL, files=files, data=data, timeout=60)
                    elapsed = time.time() - start_time
                    
                    print(f"⏱️ Respuesta recibida en {elapsed:.2f}s")
                
                if response.status_code == 200:
                    transcription = unquote(response.headers.get("X-Transcription", ""))
                    response_text = unquote(response.headers.get("X-Response-Text", ""))
                    
                    duration_header = response.headers.get("X-Record-Duration")
                    if duration_header and duration_header.isdigit():
                        current_duration = int(duration_header)
                    
                    print(f"\n{'─' * 60}")
                    print(f"📝 TÚ DIJISTE: '{transcription}'")
                    
                    if not transcription.strip():
                        print("   ⚠️ WARNING: Transcripción vacía!")
                    
                    print(f"🤖 IA RESPONDE: {response_text}")
                    print(f"⏱️ Próxima duración: {current_duration}s")
                    print(f"{'─' * 60}")

                    response_file = f"response_{interaction_count}.mp3"
                    with open(response_file, "wb") as f:
                        f.write(response.content)
                    
                    play_audio(response_file)
                    
                    time.sleep(0.5)
                    if os.path.exists(response_file):
                        os.remove(response_file)
                    
                else:
                    print(f"\n❌ Error del servidor: {response.status_code}")
                    print(f"Detalles: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                print("❌ Timeout: El servidor tardó demasiado en responder")
            except requests.exceptions.ConnectionError:
                print("❌ Error de conexión: ¿Está el servidor corriendo?")
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
            
            finally:
                if not transcription or not transcription.strip():
                    print(f"💾 Audio guardado para debug: {temp_wav}")
                elif os.path.exists(temp_wav):
                    os.remove(temp_wav)
        
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo...")
            break

if __name__ == "__main__":
    main()