from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["https://youperevod.ru"])

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API работает"})

@app.route('/api/process', methods=['POST'])  # ⚠️ ВАЖНО: methods=['POST']
def process_keywords():
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        
        # Тестовая заглушка
        results = []
        for kw in keywords:
            results.append({
                "keyword": kw,
                "overall_score": "85",
                "max_views": "100000",
                "avg_views": "25000"
            })
        
        return jsonify({
            "processed": len(keywords),
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # ⚠️ Render использует PORT 10000
    app.run(host='0.0.0.0', port=port)
