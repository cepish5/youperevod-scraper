# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
# Разрешаем CORS запросы только с вашего домена
CORS(app, origins=["https://youperevod.ru"])

# Хранилище результатов (в памяти, для демонстрации)
results_storage = {}

@app.route('/', methods=['GET'])
def home():
    """Главная страница API"""
    return jsonify({
        "message": "API для анализа заголовков YouTube",
        "status": "running"
    })

@app.route('/api/process', methods=['POST'])
def process_keywords():
    """Обработка списка ключевых слов"""
    try:
        # Получаем данные из запроса
        data = request.get_json()
        keywords = data.get('keywords', [])
        
        if not keywords:
            return jsonify({"success": False, "error": "Список ключевых слов пуст"}), 400
        
        # Здесь будет ваша логика парсинга
        # Пока возвращаем тестовые данные
        results = []
        for kw in keywords:
            for attempt in range(3):  # 3 измерения для каждого ключа
                results.append({
                    "keyword": kw,
                    "overall_score": str(80 + attempt * 2),  # Тестовые данные
                    "max_views": str(100000 + attempt * 50000),
                    "avg_views": str(25000 + attempt * 10000),
                    "attempt": attempt + 1
                })
        
        # Генерируем уникальный ID для результатов
        file_id = str(uuid.uuid4())
        
        # Сохраняем результаты в памяти
        results_storage[file_id] = results
        
        return jsonify({
            "success": True,
            "processed": len(keywords),
            "file_id": file_id,
            "message": f"Обработано {len(keywords)} заголовков"
        })
        
    except Exception as e:
        print(f"Ошибка в /api/process: {e}") # Для логирования на Render
        return jsonify({"success": False, "error": "Внутренняя ошибка сервера"}), 500

@app.route('/results/<file_id>', methods=['GET'])
def view_results(file_id):
    """Просмотр результатов в браузере"""
    try:
        if file_id not in results_storage:
            return "<h1>Ошибка 404: Результаты не найдены</h1>", 404
        
        results = results_storage[file_id]
        
        # Создаем HTML страницу с результатами
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Результаты анализа YouTube</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #007cba; color: white; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                h1 { color: #333; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Результаты анализа YouTube заголовков</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Заголовок</th>
                            <th>Общая оценка</th>
                            <th>Макс. просмотры</th>
                            <th>Средние просмотры</th>
                            <th>Попытка</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for row in results:
            html += f"""
                        <tr>
                            <td>{row['keyword']}</td>
                            <td>{row['overall_score']}</td>
                            <td>{row['max_views']}</td>
                            <td>{row['avg_views']}</td>
                            <td>{row['attempt']}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        print(f"Ошибка в /results/{file_id}: {e}")
        return "<h1>Ошибка 500: Внутренняя ошибка сервера</h1>", 500

if __name__ == '__main__':
    import os
    # Render передает порт через переменную окружения PORT
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
