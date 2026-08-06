import pyttsx3

class AashuMouth:
    def __init__(self, rate=165, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)
            
            # Set a nice voice (typically female/assistant voice if available)
            voices = self.engine.getProperty("voices")
            if voices:
                # Select English voice if possible, fallback to first voice
                selected = False
                for v in voices:
                    if "english" in v.name.lower() or "en" in v.languages:
                        self.engine.setProperty("voice", v.id)
                        selected = True
                        break
                if not selected:
                    self.engine.setProperty("voice", voices[0].id)
        except Exception as e:
            print(f"Failed to initialize pyttsx3 voice engine: {e}")
            self.engine = None

    def speak(self, text):
        """Converts text to speech and outputs it through the speakers."""
        if not text:
            return
        
        print(f"Aashu Speaks: {text}")
        
        if not self.engine:
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Speech Error: {e}")
            # Try to reinitialize in case engine session became corrupted
            self._init_engine()
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass

    def get_voices(self):
        if not self.engine:
            return []
        try:
            voices = self.engine.getProperty("voices")
            return [v.name for v in voices]
        except Exception:
            return []

    def set_voice(self, name_or_index):
        if not self.engine:
            return False
        try:
            voices = self.engine.getProperty("voices")
            try:
                idx = int(name_or_index)
                if 0 <= idx < len(voices):
                    self.engine.setProperty("voice", voices[idx].id)
                    return True
            except ValueError:
                pass
            
            for v in voices:
                if name_or_index.lower() in v.name.lower():
                    self.engine.setProperty("voice", v.id)
                    return True
            return False
        except Exception:
            return False
