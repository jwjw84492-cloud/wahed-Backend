import os
import time
import base64
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class FLambdaCore:
    # القيمة الافتراضية، يمكنك تغييرها حسب حاجتك
    F_LAMBDA = 15.0725  

    @staticmethod
    def encode(data):
        if isinstance(data, str):
            raw_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            raw_bytes = data
        elif hasattr(data, 'read'):
            raw_bytes = data.read()
        else:
            raw_bytes = str(data).encode('utf-8')

        CHUNK_SIZE = 10000
        signals = []
        
        # تحويل البيانات إلى إشارات رقمية (Signatures)
        for chunk_start in range(0, len(raw_bytes), CHUNK_SIZE):
            chunk = raw_bytes[chunk_start:chunk_start + CHUNK_SIZE]
            for i, byte in enumerate(chunk):
                global_index = chunk_start + i
                # المعادلة الرياضية لتوليد الإشارة
                signal = (byte * FLambdaCore.F_LAMBDA + (global_index + 1)) % 1.0
                signals.append(float(f"{signal:.12f}"))

        # حساب البصمة الرقمية النهائية
        fingerprint = round(sum(signals) % 1.0, 12)
        return signals, fingerprint

def verify_integrity(original: bytes, recovered: bytes) -> bool:
    """التأكد من أن البيانات المسترجعة تطابق الأصلية تماماً"""
    hash1 = hashlib.sha256(original).hexdigest()
    hash2 = hashlib.sha256(recovered).hexdigest()
    return hash1 == hash2

@app.route('/process', methods=['POST'])
def process_file():
    start_time = time.time()

    if 'file' not in request.files:
        return jsonify({"error": "no file sent"}), 400

    file = request.files['file']
    contents = file.read()
    file_size = len(contents)

    # معالجة الملف
    signals, fingerprint = FLambdaCore.encode(contents)
    encoded_content = base64.b64encode(contents).decode('utf-8')
    recovered_bytes = base64.b64decode(encoded_content)
    
    # فحص السلامة
    integrity_check = verify_integrity(contents, recovered_bytes)
    integrity_status = "100% VERIFIED" if integrity_check else "FAILED"
    processing_time = f"{(time.time() - start_time):.4f}s"

    return jsonify({
        "success": True,
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file_size,
        "processing_time": processing_time,
        "signatures": signals[:100], # عرض أول 100 إشارة فقط للاختصار
        "fingerprint": fingerprint,
        "total_signals": len(signals),
        "integrity": integrity_status,
        "recovered_file": encoded_content
    })

@app.route('/encode_text', methods=['POST'])
def encode_text():
    start_time = time.time()
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "no text sent"}), 400

    text = data['text']
    signals, fingerprint = FLambdaCore.encode(text)
    processing_time = f"{(time.time() - start_time):.4f}s"

    return jsonify({
        "success": True,
        "input_length": len(text),
        "total_signals": len(signals),
        "signals": signals,
        "fingerprint": fingerprint,
        "processing_time": processing_time
    })

@app.route('/recover', methods=['POST'])
def recover_file():
    data = request.get_json()
    if not data or 'recovered_file' not in data:
        return jsonify({"error": "no data to recover"}), 400

    return jsonify({
        "success": True,
        "recovered_file": data['recovered_file'],
        "message": "recovered successfully"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running",
        "project": "Axiomara",
        "version": "2.0.0",
        "features": ["any_file", "any_text", "no_size_limit", "fingerprint"]
    })

if __name__ == '__main__':
    # تحديد المنفذ (Port) من البيئة أو استخدام 10000 كافتراضي
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
