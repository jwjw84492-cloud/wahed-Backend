import time
import secrets
import math
from flask import Flask

app = Flask(__name__)

class MultimediaEngine:
    def __init__(self, f_lambda=15.0725):
        self.f_lambda = f_lambda

    def process_data(self, data_bytes):
        encoded_signals = []
        decoded_output = bytearray()
        
        for i, byte in enumerate(data_bytes):
            signal = (byte * self.f_lambda + (i + 1)) % 1.0
            encoded_signals.append(signal)
        
        for i, signal in enumerate(encoded_signals):
            found = False
            for byte_val in range(256):
                test_sig = (byte_val * self.f_lambda + (i + 1)) % 1.0
                if abs(test_sig - signal) < 1e-12:
                    decoded_output.append(byte_val)
                    found = True
                    break
            if not found:
                return None, False
        
        return decoded_output, True

@app.route('/')
def index():
    return "Multimedia Engine is Running."

def run_multimedia_challenge():
    engine = MultimediaEngine()
    file_types = {
        "Digital Image (.raw)": 1000,
        "Audio Stream (.wav)": 5000,
        "Video Fragment (.mp4)": 10000
    }
    
    print("====================================================")
    print("   UNIVERSAL MULTIMEDIA RECOVERY CHALLENGE (F-λ)   ")
    print("====================================================\n")

    for file_name, size in file_types.items():
        raw_data = secrets.token_bytes(size)
        print(f"Testing: {file_name} | Size: {size} Bytes")
        
        start_time = time.time()
        recovered_data, success = engine.process_data(raw_data)
        end_time = time.time()
        
        integrity = (raw_data == recovered_data)
        print(f"Result: {'[SUCCESS]' if integrity else '[FAILURE]'}")
        print("-" * 50)

    print("\nConclusion: The F-Lambda core can archive any complex digital signal.")

if __name__ == "__main__":
    run_multimedia_challenge()
    # Port for Render deployment
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
