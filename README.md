# YouTube vidiq Scraper API

Backend для анализа заголовков YouTube через vidiq.

## API Endpoints

- `GET /` - Проверка работы API
- `POST /api/process` - Обработка списка ключевых слов
- `GET /api/download/csv` - Скачать результаты в CSV
- `GET /api/download/xlsx` - Скачать результаты в Excel

## Использование

1. Отправьте POST запрос на `/api/process` с JSON:
   ```json
   {
     "keywords": ["заголовок 1", "заголовок 2"]
   }
