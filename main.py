import time
import base64
import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- Core Engine ---
class MultimediaEngine:
    def __init__(self, f_lambda=15.0725):
        self.f_lambda = f_lambda

    def process_data(self, data_bytes):
        encoded_signals = []
        decoded_output = bytearray()
        
        # Encoding
        for i, byte in enumerate(data_bytes):
            signal = (byte * self.f_lambda + (i + 1)) % 1.0
            encoded_signals.append(signal)
        
        # Decoding
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

engine = MultimediaEngine()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Read and process data
    start_time = time.time()
    raw_data = file.read()
    recovered_data, success = engine.process_data(raw_data)
    end_time = time.time()

    if not success:
        return jsonify({"error": "Processing failed"}), 500

    # Prepare response
    duration = f"{end_time - start_time:.4f}s"
    encoded_file = base64.b64encode(recovered_data).decode('utf-8')
    
    return jsonify({
        "filename": file.filename,
        "content_type": file.content_type,
        "recovered_file": encoded_file,
        "processing_time": duration
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
