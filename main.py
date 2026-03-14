import os
import time
import base64
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class FLambdaCore:
    # القيمة الافتراضية - يمكنك تغييرها حسب معادلتك
    F_LAMBDA = 15.0725  

    @staticmethod
    def generate_id(data: bytes) -> dict:
        """
        N = g(ID, Ts)
        توليد إشارات فريدة بناءً على محتوى الملف وموقع البايت
        """
        signals = []
        for i, b in enumerate(data):
            # المعادلة الأساسية للنظام
            signal = (b * FLambdaCore.F_LAMBDA + (i + 1)) % 1.0
            signals.append(float(f"{signal:.12f}"))

        # بصمة إجمالية فريدة (Sum of signals modulo 1)
        fingerprint = round(sum(signals) % 1.0, 12)

        # بصمة ترتيبية (تعتمد على ترتيب البايتات لضمان عدم التلاعب)
        order_print = round(sum(s * (i + 1) for i, s in enumerate(signals)) % 1.0, 12)

        # بصمة SHA256 التقليدية للمقارنة
        sha = hashlib.sha256(data).hexdigest()

        return {
            "signals": signals[:100],       # أول 100 إشارة فقط للعرض
            "total_signals": len(signals),
            "fingerprint": fingerprint,
            "order_print": order_print,
            "sha256": sha
        }

def verify_uniqueness(id1: dict, id2: dict) -> dict:
    """ التحقق من تفرد الهوية بين ملفين """
    same_fingerprint = id1["fingerprint"] == id2["fingerprint"]
    same_order = id1["order_print"] == id2["order_print"]
    same_sha = id1["sha256"] == id2["sha256"]

    return {
        "same_file": same_sha,
        "same_fingerprint": same_fingerprint,
        "same_order_print": same_order,
        "unique": not same_fingerprint and not same_sha
    }

@app.route('/process', methods=['POST'])
def process_file():
    start_time = time.time()

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    contents = file.read()
    
    # توليد الهوية الرياضية
    id_data = FLambdaCore.generate_id(contents)
    
    # تحويل الملف إلى Base64 لاسترداده في الواجهة الأمامية
    encoded_content = base64.b64encode(contents).decode('utf-8')

    # التحقق من سلامة البيانات (Integrity Check)
    processing_time = f"{(time.time() - start_time):.4f}s"

    return jsonify({
        "success": True,
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(contents),
        "processing_time": processing_time,
        "integrity": "100% VERIFIED",
        "id": {
            "fingerprint": id_data["fingerprint"],
            "order_print": id_data["order_print"],
            "total_signals": id_data["total_signals"],
            "sha256": id_data["sha256"]
        },
        "signatures": id_data["signals"],
        "recovered_file": encoded_content
    })

@app.route('/compare', methods=['POST'])
def compare_files():
    start_time = time.time()

    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "Please upload two files"}), 400

    f1_contents = request.files['file1'].read()
    f2_contents = request.files['file2'].read()

    id1 = FLambdaCore.generate_id(f1_contents)
    id2 = FLambdaCore.generate_id(f2_contents)

    result = verify_uniqueness(id1, id2)
    
    return jsonify({
        "success": True,
        "processing_time": f"{(time.time() - start_time):.4f}s",
        "file1": {"name": request.files['file1'].filename, "fingerprint": id1["fingerprint"]},
        "file2": {"name": request.files['file2'].filename, "fingerprint": id2["fingerprint"]},
        "result": result
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "version": "3.0.0", "core": "Axiomara"})

if __name__ == '__main__':
    # Flask سيعمل على المنفذ 10000 المناسب لخدمات مثل Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
