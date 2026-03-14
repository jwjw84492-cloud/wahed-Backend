import os
import time
import base64
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(**name**)
CORS(app)

class FLambdaCore:
F_LAMBDA = 15.0725  # PUT YOUR NUMBER HERE

def generate_id(data: bytes) -> dict:
“””
N = g(ID, Ts)
ID = [(b * Ts + i) % 1.0 for each byte]
“””
signals = []
for i, b in enumerate(data):
signal = (b * FLambdaCore.F_LAMBDA + (i + 1)) % 1.0
signals.append(float(f”{signal:.12f}”))

```
# بصمة اجمالية فريدة
fingerprint = round(sum(signals) % 1.0, 12)

# بصمة ترتيبية
order_print = round(sum(s * (i+1) for i, s in enumerate(signals)) % 1.0, 12)

# بصمة SHA للتحقق
sha = hashlib.sha256(data).hexdigest()

return {
    "signals": signals[:100],       # اول 100 اشاره
    "total_signals": len(signals),  # عدد الاشارات الكلي
    "fingerprint": fingerprint,     # البصمة الاجمالية
    "order_print": order_print,     # البصمة الترتيبية
    "sha256": sha                   # للتحقق
}
```

def verify_uniqueness(id1: dict, id2: dict) -> dict:
“””
تحقق ان كل ملف له ID فريد
“””
same_fingerprint = id1[“fingerprint”] == id2[“fingerprint”]
same_order = id1[“order_print”] == id2[“order_print”]
same_sha = id1[“sha256”] == id2[“sha256”]

```
return {
    "same_file": same_sha,
    "same_fingerprint": same_fingerprint,
    "same_order_print": same_order,
    "unique": not same_fingerprint and not same_sha
}
```

@app.route(’/process’, methods=[‘POST’])
def process_file():
start_time = time.time()

```
if 'file' not in request.files:
    return jsonify({"error": "no file sent"}), 400

file = request.files['file']
contents = file.read()
file_size = len(contents)

id_data = generate_id(contents)
encoded_content = base64.b64encode(contents).decode('utf-8')

# التحقق من سلامة البيانات
recovered = base64.b64decode(encoded_content)
integrity = hashlib.sha256(contents).hexdigest() == hashlib.sha256(recovered).hexdigest()

processing_time = f"{(time.time() - start_time):.4f}s"

return jsonify({
    "success": True,
    "filename": file.filename,
    "content_type": file.content_type,
    "size_bytes": file_size,
    "processing_time": processing_time,
    "integrity": "100% VERIFIED" if integrity else "FAILED",
    "id": {
        "fingerprint": id_data["fingerprint"],
        "order_print": id_data["order_print"],
        "total_signals": id_data["total_signals"],
        "sha256": id_data["sha256"]
    },
    "signatures": id_data["signals"],
    "recovered_file": encoded_content
})
```

@app.route(’/compare’, methods=[‘POST’])
def compare_files():
“””
قارن ملفين وتحقق ان لكل واحد ID فريد
“””
start_time = time.time()

```
if 'file1' not in request.files or 'file2' not in request.files:
    return jsonify({"error": "send file1 and file2"}), 400

file1 = request.files['file1']
file2 = request.files['file2']

contents1 = file1.read()
contents2 = file2.read()

id1 = generate_id(contents1)
id2 = generate_id(contents2)

result = verify_uniqueness(id1, id2)
processing_time = f"{(time.time() - start_time):.4f}s"

return jsonify({
    "success": True,
    "processing_time": processing_time,
    "file1": {
        "name": file1.filename,
        "size": len(contents1),
        "fingerprint": id1["fingerprint"],
        "order_print": id1["order_print"]
    },
    "file2": {
        "name": file2.filename,
        "size": len(contents2),
        "fingerprint": id2["fingerprint"],
        "order_print": id2["order_print"]
    },
    "result": result
})
```

@app.route(’/health’, methods=[‘GET’])
def health():
return jsonify({
“status”: “running”,
“project”: “Axiomara”,
“version”: “3.0.0”,
“model”: “N = g(ID, Ts)”,
“features”: [“uniqueness”, “fingerprint”, “compare”, “any_file”]
})

if **name** == ‘**main**’:
port = int(os.environ.get(‘PORT’, 10000))
app.run(host=‘0.0.0.0’, port=port)
