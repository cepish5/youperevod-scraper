from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["https://youperevod.ru/2"])

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Backend is running"})

@app.route("/api/parse", methods=["POST"])
def parse_keywords():
    data = request.get_json()
    keywords = data.get("keywords", [])
    
    # Здесь будет ваш парсер
    results = [{"keyword": kw, "score": 85} for kw in keywords]
    
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
