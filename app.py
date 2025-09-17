from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import pandas as pd
import uuid

app = Flask(__name__)

# Настройка CORS для разрешения запросов с вашего домена
CORS(app, origins=["https://youperevod.ru"])

# Хранилище для результатов (в памяти, для демонстрации)
results_storage = {}

# HTML шаблон для отображения результатов
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Результаты анализа YouTube</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .container { max-width: 1200px; margin: 0 auto; }
        .results { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Результаты анализа YouTube заголовков</h1>
        <div class="results">
            <h2>Обработанные данные:</h2>
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
                    {% for row in data %}
                    <tr>
                        <td>{{ row.keyword }}</td>
                        <td>{{ row.overall_score }}</td>
                        <td>{{ row.max_views }}</td>
                        <td>{{ row.avg_views }}</td>
                        <td>{{ row.attempt }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    """Главная страница API"""
    return jsonify({
        "message": "API для анализа заголовков YouTube",
        "status": "running",
        "version": "1.0",
        "endpoints": {
            "process": "/api/process (POST)",
            "view_results": "/results/<file_id> (GET)"
        }
    })

@app.route('/api/process', methods=['POST'])
def process_keywords():
    """Обработка списка ключевых слов"""
    try:
        # Получаем данные из запроса
        data = request.get_json()
        keywords = data.get('keywords', [])
        
        if not keywords:
            return jsonify({"error": "Список ключевых слов пуст"}), 400
        
        # Здесь будет ваша логика парсинга
        # Пока возвращаем тестовые данные
        results = []
        for kw in keywords:
            for attempt in range(3):  # 3 измерения для каждого ключа
                results.append({
                    "keyword": kw,
                    "overall_score": "85",  # Тестовые данные
                    "max_views": "100000",
                    "avg_views": "25000",
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
            "view_url": f"/results/{file_id}",
            "message": f"Обработано {len(keywords)} заголовков. Просмотрите результаты по ссылке выше."
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/results/<file_id>', methods=['GET'])
def view_results(file_id):
    """Просмотр результатов в браузере"""
    try:
        if file_id not in results_storage:
            return jsonify({"error": "Результаты не найдены"}), 404
        
        results = results_storage[file_id]
        
        # Создаем HTML страницу с результатами
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Результаты анализа YouTube</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #007cba; color: white; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                h1 {{ color: #333; text-align: center; }}
                .download-buttons {{ text-align: center; margin: 20px 0; }}
                .download-buttons a {{ 
                    display: inline-block;
                    background: #007cba;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 0 10px;
                }}
                .download-buttons a:hover {{ background: #005a87; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Результаты анализа YouTube заголовков</h1>
                
                <div class="download-buttons">
                    <a href="/api/download/csv/{file_id}">📥 Скачать CSV</a>
                    <a href="/api/download/xlsx/{file_id}">📊 Скачать Excel</a>
                </div>
                
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
            html_content += f"""
                        <tr>
                            <td>{row['keyword']}</td>
                            <td>{row['overall_score']}</td>
                            <td>{row['max_views']}</td>
                            <td>{row['avg_views']}</td>
                            <td>{row['attempt']}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return jsonify({"error": f"Ошибка при отображении результатов: {str(e)}"}), 500

@app.route('/api/download/csv/<file_id>', methods=['GET'])
def download_csv(file_id):
    """Скачивание результатов в CSV"""
    try:
        if file_id not in results_storage:
            return jsonify({"error": "Результаты не найдены"}), 404
        
        results = results_storage[file_id]
        df = pd.DataFrame(results)
        
        from flask import Response
        import io
        
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=vidiq_results.csv'}
        )
        
    except Exception as e:
        return jsonify({"error": f"Ошибка при создании CSV: {str(e)}"}), 500

@app.route('/api/download/xlsx/<file_id>', methods=['GET'])
def download_xlsx(file_id):
    """Скачивание результатов в Excel"""
    try:
        if file_id not in results_storage:
            return jsonify({"error": "Результаты не найдены"}), 404
        
        results = results_storage[file_id]
        df = pd.DataFrame(results)
        
        import io
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='vidiq_results.xlsx'
        )
        
    except Exception as e:
        return jsonify({"error": f"Ошибка при создании Excel: {str(e)}"}), 500

# Добавим импорт send_file в начало файла
from flask import send_file

if __name__ == '__main__':
    # Render передает порт через переменную окружения PORT
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
