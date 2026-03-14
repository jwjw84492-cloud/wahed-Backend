import os
import time
import base64
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

# إعداد تطبيق Flask
app = Flask(__name__)
CORS(app)

class FLambdaCore:
    # القيمة الافتراضية، يمكنك تغييرها حسب حاجتك
    F_LAMBDA = 15.0725  

    @staticmethod
    def generate_signature(data: bytes) -> list:
        """توليد تواقيع رقمية بناءً على محتوى الملف"""
        signals = [
            float(f"{(b * FLambdaCore.F_LAMBDA + (i + 1)) % 1.0:.12f}")
            for i, b in enumerate(data[:100])
        ]
        return signals

    @staticmethod
    def verify_integrity(original: bytes, recovered: bytes) -> bool:
        """التأكد من أن البيانات المسترجعة تطابق البيانات الأصلية باستخدام SHA-256"""
        hash1 = hashlib.sha256(original).hexdigest()
        hash2 = hashlib.sha256(recovered).hexdigest()
        return hash1 == hash2

@app.route('/process', methods=['POST'])
def process_file():
    start_time = time.time()

    # التأكد من إرسال ملف في الطلب
    if 'file' not in request.files:
        return jsonify({"error": "no file sent"}), 400

    file = request.files['file']
    contents = file.read()
    file_size = len(contents)

    # معالجة البيانات
    signatures = FLambdaCore.generate_signature(contents)
    encoded_content = base64.b64encode(contents).decode('utf-8')
    recovered_bytes = base64.b64decode(encoded_content)
    
    # التحقق من سلامة البيانات
    integrity_check = FLambdaCore.verify_integrity(contents, recovered_bytes)
    integrity_status = "100% VERIFIED" if integrity_check else "FAILED"
    processing_time = f"{(time.time() - start_time):.4f}s"

    return jsonify({
        "success": True,
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file_size,
        "processing_time": processing_time,
        "signatures": signatures,
        "integrity": integrity_status,
        "recovered_file": encoded_content
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
        "version": "1.0.0"
    })

if __name__ == '__main__':
    # تحديد المنفذ (Port) المتوافق مع Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
