from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import pandas as pd
import uuid
import io

app = Flask(__name__)

# Настройка CORS для разрешения запросов с вашего домена
CORS(app, origins=["https://youperevod.ru"])

# Папки для файлов (в Render файловая система эфемерна)
RESULTS_FOLDER = '/tmp/results'  # Используем /tmp для временных файлов
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    """Главная страница API"""
    return jsonify({
        "message": "API для анализа заголовков YouTube",
        "status": "running",
        "version": "1.0"
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
        
        # Генерируем уникальный ID для файлов
        file_id = str(uuid.uuid4())
        
        # Создаем DataFrame и сохраняем в файлы
        df = pd.DataFrame(results)
        
        # Сохраняем CSV
        csv_path = os.path.join(RESULTS_FOLDER, f"{file_id}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Сохраняем Excel
        xlsx_path = os.path.join(RESULTS_FOLDER, f"{file_id}.xlsx")
        df.to_excel(xlsx_path, index=False)
        
        return jsonify({
            "success": True,
            "processed": len(keywords),
            "file_id": file_id,
            "message": f"Обработано {len(keywords)} заголовков"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/download/<filetype>', methods=['GET'])
def download_file(filetype):
    """Скачивание результатов"""
    try:
        # Создаем тестовые данные для скачивания
        sample_data = [
            {
                "keyword": "Тестовый заголовок",
                "overall_score": "85",
                "max_views": "100000",
                "avg_views": "25000",
                "attempt": 1
            },
            {
                "keyword": "Еще один заголовок",
                "overall_score": "92",
                "max_views": "150000",
                "avg_views": "35000",
                "attempt": 1
            }
        ]
        
        df = pd.DataFrame(sample_data)
        
        if filetype == 'csv':
            # Создаем CSV в памяти
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            
            # Возвращаем как файл
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=vidiq_results.csv'}
            )
            
        elif filetype == 'xlsx':
            # Создаем Excel в памяти
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            
            # Возвращаем как файл
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='vidiq_results.xlsx'
            )
        else:
            return jsonify({"error": "Неверный тип файла. Доступны: csv, xlsx"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Ошибка при создании файла: {str(e)}"}), 500

if __name__ == '__main__':
    # Render передает порт через переменную окружения PORT
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
