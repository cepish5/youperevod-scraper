# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from collections import defaultdict

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
    """Просмотр результатов в браузере в новом формате"""
    try:
        if file_id not in results_storage:
            return "<h1>Ошибка 404: Результаты не найдены</h1>", 404
        
        results = results_storage[file_id]
        
        # Группируем результаты по ключевому слову
        grouped_results = defaultdict(list)
        for item in results:
            grouped_results[item['keyword']].append(item)
        
        # Создаем HTML страницу с результатами
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Результаты анализа YouTube</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        h1 { 
            color: #333; 
            text-align: center; 
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin-top: 20px; 
            table-layout: fixed; 
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: center; 
            vertical-align: middle;
        }
        th { 
            background-color: #007cba; 
            color: white; 
            font-weight: bold; 
        }
        tr:nth-child(even) { 
            background-color: #f9f9f9; 
        }
        .keyword-cell { 
            text-align: left; 
        }
        .merged-header {
            text-align: center;
        }
        /* Для корректного отображения таблицы */
        col.keyword-col { width: 30%; }
        col.metric-col { width: 10%; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Результаты анализа YouTube заголовков</h1>
        <table>
            <colgroup>
                <col class="number-col">
                <col class="keyword-col">
                <col class="metric-col"><col class="metric-col"><col class="metric-col">
                <col class="metric-col"><col class="metric-col"><col class="metric-col">
                <col class="metric-col"><col class="metric-col"><col class="metric-col">
            </colgroup>
            <thead>
                <tr>
                    <th rowspan="2">№</th>
                    <th rowspan="2">Заголовок</th>
                    <th class="merged-header" colspan="3">Общая оценка</th>
                    <th class="merged-header" colspan="3">Макс. просмотры (тыс.)</th>
                    <th class="merged-header" colspan="3">Средние просмотры (тыс.)</th>
                </tr>
                <tr>
                    <th>1</th>
                    <th>2</th>
                    <th>3</th>
                    <th>1</th>
                    <th>2</th>
                    <th>3</th>
                    <th>1</th>
                    <th>2</th>
                    <th>3</th>
                </tr>
            </thead>
            <tbody>
"""

        row_number = 1
        for keyword, attempts in grouped_results.items():
            # Сортируем попытки по номеру
            attempts_sorted = sorted(attempts, key=lambda x: x['attempt'])
            
            # Извлекаем значения
            scores = [attempt['overall_score'] for attempt in attempts_sorted]
            max_views_raw = [int(attempt['max_views']) for attempt in attempts_sorted]
            avg_views_raw = [int(attempt['avg_views']) for attempt in attempts_sorted]
            
            # Преобразуем просмотры в тысячи
            max_views_thousands = [f"{views // 1000}" for views in max_views_raw]
            avg_views_thousands = [f"{views // 1000}" for views in avg_views_raw]
            
            html += f"""                <tr>
                    <td>{row_number}</td>
                    <td class="keyword-cell">{keyword}</td>
                    <td>{scores[0] if len(scores) > 0 else ''}</td>
                    <td>{scores[1] if len(scores) > 1 else ''}</td>
                    <td>{scores[2] if len(scores) > 2 else ''}</td>
                    <td>{max_views_thousands[0] if len(max_views_thousands) > 0 else ''}</td>
                    <td>{max_views_thousands[1] if len(max_views_thousands) > 1 else ''}</td>
                    <td>{max_views_thousands[2] if len(max_views_thousands) > 2 else ''}</td>
                    <td>{avg_views_thousands[0] if len(avg_views_thousands) > 0 else ''}</td>
                    <td>{avg_views_thousands[1] if len(avg_views_thousands) > 1 else ''}</td>
                    <td>{avg_views_thousands[2] if len(avg_views_thousands) > 2 else ''}</td>
                </tr>
"""
            row_number += 1
        
        html += """            </tbody>
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
