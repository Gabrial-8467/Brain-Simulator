import os
import tempfile
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from .config import MIC_SAMPLE_RATE, MIC_THRESHOLD, MIC_SILENCE_DURATION

class AashuEars:
    def __init__(self, sample_rate=MIC_SAMPLE_RATE, threshold=MIC_THRESHOLD, silence_duration=MIC_SILENCE_DURATION):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()

    def record_until_silence(self):
        """
        Listens dynamically and starts recording when voice goes above the threshold.
        Stops recording after a sustained duration of silence.
        """
        chunk_size = 1024
        audio_buffer = []
        recording_active = False
        silent_chunks = 0
        max_silent_chunks = int((self.silence_duration * self.sample_rate) / chunk_size)
        
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        def callback(indata, frames, time, status):
            nonlocal recording_active, silent_chunks
            # Calculate RMS (root-mean-square) volume of the current chunk
            rms = np.sqrt(np.mean(indata**2))
            
            if not recording_active:
                if rms > self.threshold:
                    recording_active = True
                    audio_buffer.append(indata.copy())
            else:
                audio_buffer.append(indata.copy())
                if rms < self.threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if silent_chunks >= max_silent_chunks:
                    # Silence detected, raise StopIteration or queue stopping signal
                    self.audio_queue.put("STOP")

        # Open input audio stream
        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=callback,
            blocksize=chunk_size
        )
        
        with stream:
            print("Listening...")
            while True:
                try:
                    # Block and wait for stop signal
                    val = self.audio_queue.get(timeout=0.1)
                    if val == "STOP":
                        break
                except queue.Empty:
                    if len(audio_buffer) > (self.sample_rate * 15 / chunk_size): # Max 15 seconds safety limit
                        break
                    continue

        if not audio_buffer:
            return None

        # Concatenate audio chunks
        audio_data = np.concatenate(audio_buffer, axis=0)
        
        # Save to temporary WAV file
        temp_dir = tempfile.gettempdir()
        temp_wav = os.path.join(temp_dir, "aashu_mic.wav")
        sf.write(temp_wav, audio_data, self.sample_rate)
        
        return temp_wav

    def transcribe(self, wav_file):
        if not wav_file or not os.path.exists(wav_file):
            return ""
        
        try:
            with sr.AudioFile(wav_file) as source:
                audio = self.recognizer.record(source)
            # Transcribe via Google speech recognizer (no API key required)
            text = self.recognizer.recognize_google(audio)
            return text.strip()
        except sr.UnknownValueError:
            pass # Speech was unintelligible
        except sr.RequestError as e:
            print(f"STT Service Request Error: {e}")
        except Exception as e:
            print(f"STT Error: {e}")
        finally:
            try:
                os.remove(wav_file)
            except:
                pass
        return ""

    def listen_and_transcribe(self):
        wav = self.record_until_silence()
        if wav:
            return self.transcribe(wav)
        return ""
