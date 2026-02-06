import wave
import subprocess
import os

class SpeechEngine:
    def __init__(self, whisper_path, model_path):
        self.whisper_exec = whisper_path
        self.whisper_model = model_path
        self.sample_rate = 16000

    def _save_audio(self, frames):
        filename = "temp_audio.wav"
        raw_data = b''.join(frames)
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(raw_data)
        return filename

    def _run_whisper(self, filename):
        if not os.path.exists(self.whisper_exec):
            return "Error: Whisper executable not found."
            
        command = [self.whisper_exec, "-m", self.whisper_model, "-f", filename, "-nt"]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"

    # --- THIS IS THE ONE FUNCTION YOU CALL ---
    def get_transcript(self, ser, btn):
        print("\n[Speech] Listening...", end="", flush=True)
        frames = []

        # 1. Record until the button is released
        while btn.is_pressed:
            if ser.in_waiting > 0:
                frames.append(ser.read(ser.in_waiting))
        
        print(" Processing...")

        # 2. Save & Transcribe
        filename = self._save_audio(frames)
        text = self._run_whisper(filename)
        
        return text