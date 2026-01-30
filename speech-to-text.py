import serial
import wave
import time
import subprocess
import os
from gpiozero import Button

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 921600       
SAMPLE_RATE = 16000      
BUTTON_PIN = 17          

# UPDATED PATH (Using the CLI tool you found)
WHISPER_EXEC = "./whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "./whisper.cpp/models/ggml-tiny.bin"

btn = Button(BUTTON_PIN)

def save_audio(frames):
    if not frames:
        return None
    
    filename = "temp_audio.wav"
    raw_data = b''.join(frames)
    
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)       
        wf.setsampwidth(2)       
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(raw_data)
    
    return filename

def transcribe_audio(filename):
    print("Transcribing...")
    if not os.path.exists(WHISPER_EXEC):
        print(f"Error: Could not find whisper executable at: {WHISPER_EXEC}")
        return

    # -nt means "no timestamp"
    command = [WHISPER_EXEC, "-m", WHISPER_MODEL, "-f", filename, "-nt"]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        text = result.stdout.strip()
        print("\n" + "="*40)
        print(f"TRANSCRIPTION: {text}")
        print("="*40 + "\n")
    except Exception as e:
        print(f"Transcription failed: {e}")

def main():
    print("--- Instant Recorder Ready ---")
    print(f"Opening Serial Port {SERIAL_PORT} (Please wait)...")
    
    try:
        # FIX: Open Serial Port ONCE at the start
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        ser.timeout = 0.1  # Small timeout to keep loop moving
        print("Serial Port Open! Hold GPIO 17 to record.")
        
        while True:
            # 1. Idle Loop: Flush "garbage" audio while waiting
            while not btn.is_pressed:
                if ser.in_waiting > 0:
                    ser.read(ser.in_waiting) # Throw away audio when not button is not pressed
                time.sleep(0.01)

            # 2. Recording Loop: Button is held, SAVE the audio
            print("\nRecording...", end="", flush=True)
            frames = []
            
            # Grab the last chunk immediately so we don't miss the start
            if ser.in_waiting > 0:
                frames.append(ser.read(ser.in_waiting))

            while btn.is_pressed:
                if ser.in_waiting > 0:
                    frames.append(ser.read(ser.in_waiting))
                # No sleep here needed, we want to read as fast as possible

            print(" Done.")
            
            # 3. Process
            filename = save_audio(frames)
            if filename:
                transcribe_audio(filename)

    except serial.SerialException as e:
        print(f"\nCRITICAL ERROR: Could not open serial port {SERIAL_PORT}")
        print(f"Details: {e}")
    except KeyboardInterrupt:
        print("\nExiting.")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()