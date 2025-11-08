# Model Validation Guide

## Обзор

Скрипт `validate_model.py` выполняет полную валидацию модели персонального цветового анализа на тестовом датасете и генерирует детальные визуализации результатов.

## Датасет

**Расположение**: `data/valid/`

**Классы (4 основных сезона)**:
- 🍂 **Fall (Autumn)** - Осенний цветотип
- 🌸 **Spring** - Весенний цветотип  
- 🌺 **Summer** - Летний цветотип
- ❄️ **Winter** - Зимний цветотип

**Важно**: Модель возвращает **12 детальных цветотипов** (3 подтипа на сезон):
- **Spring**: Warm Spring, Bright Spring, Light Spring
- **Summer**: Light Summer, True Summer, Soft Summer  
- **Autumn/Fall**: Warm Autumn, Deep Autumn, Soft Autumn
- **Winter**: Cool Winter, Bright Winter, Deep Winter

Скрипт валидации автоматически мапит 12 детальных типов → 4 основных сезона.

**Структура**:
```
data/valid/
├── _classes.csv           # Ground truth labels
├── img1.jpg              # Test images
├── img2.jpg
└── ...
```

## Установка зависимостей

```bash
# Обновить зависимости
uv sync

# Или установить вручную
pip install matplotlib seaborn numpy requests
```

## Запуск валидации

### 1. Запустить сервер API

```bash
cd /Users/vadim/Coding/Hackaton/hackseoul_fe
uv run python app.py
```

Сервер должен быть запущен на `http://localhost:8000`

### 2. Запустить валидацию

```bash
# В отдельном терминале
uv run python validate_model.py
```

## Что делает скрипт

1. **Загружает ground truth** из `_classes.csv`
2. **Обрабатывает каждое изображение**:
   - Конвертирует в base64
   - Отправляет на API `/api/analyze/color`
   - Получает предсказание и confidence
3. **Вычисляет метрики**:
   - Overall accuracy
   - Per-class precision, recall, F1-score
   - Confusion matrix
   - Confidence analysis
4. **Генерирует визуализации**:
   - Confusion matrix (обычная и детальная)
   - Per-class metrics bar chart
   - Class distribution
   - Confidence distribution
   - Accuracy by season
   - Overall summary

## Результаты

Все результаты сохраняются в `validation_results/`:

### Файлы

1. **`validation_results.png`** - Главная панель с 6 графиками:
   - Confusion Matrix
   - Per-Class Metrics (Precision, Recall, F1)
   - Class Distribution
   - Confidence Distribution
   - Accuracy per Season
   - Summary Statistics

2. **`confusion_matrix_detailed.png`** - Детальная confusion matrix с процентами

3. **`validation_results.json`** - Полные результаты в JSON:
   ```json
   {
     "timestamp": "2025-11-08T...",
     "overall_metrics": {
       "accuracy": 0.85,
       "total_predictions": 50,
       "correct_predictions": 42
     },
     "class_metrics": {...},
     "predictions": [...]
   }
   ```

4. **`validation_summary.txt`** - Текстовое резюме для быстрого просмотра

## Интерпретация результатов

### Метрики

- **Accuracy**: Процент правильных предсказаний
- **Precision**: Из всех предсказанных как класс X, сколько действительно X
- **Recall**: Из всех истинных X, сколько мы нашли
- **F1-Score**: Гармоническое среднее precision и recall

### Confusion Matrix

```
               Predicted
             F   Sp  Su  W
True    F   [10   2   0   1]
        Sp  [ 1  12   1   0]
        Su  [ 0   2   8   0]
        W   [ 1   0   0  12]
```

- Диагональ = правильные предсказания
- Вне диагонали = ошибки

### Confidence Analysis

- **High confidence + correct** ✅ = Модель уверена и права
- **High confidence + incorrect** ⚠️ = Модель ошибается, но уверена (проблема)
- **Low confidence + correct** 🤔 = Модель права, но не уверена
- **Low confidence + incorrect** ❌ = Модель не уверена и ошибается

## Пример вывода

```
======================================================================
PERSONAL COLOR ANALYSIS MODEL VALIDATION
======================================================================

📋 Loading ground truth labels...
✓ Loaded 50 images with labels

📊 Dataset distribution:
  Fall: 12 images
  Spring: 15 images
  Summer: 10 images
  Winter: 13 images

🔮 Running predictions...
  [1/50] Processing img94.jpg... ✓ Predicted: spring (confidence: 0.87)
  [2/50] Processing img57.jpg... ✓ Predicted: spring (confidence: 0.92)
  ...

======================================================================
RESULTS
======================================================================

📈 Overall Accuracy: 84.00% (42/50)

📊 Per-Class Metrics:
  Fall     - Precision: 83.33%, Recall: 83.33%, F1: 83.33%
  Spring   - Precision: 85.71%, Recall: 86.67%, F1: 86.19%
  Summer   - Precision: 80.00%, Recall: 80.00%, F1: 80.00%
  Winter   - Precision: 85.71%, Recall: 92.31%, F1: 88.89%

📊 Confidence Analysis:
  Average confidence (correct predictions): 87.35%
  Average confidence (incorrect predictions): 65.12%

📊 Generating visualizations...
  ✓ Saved visualization: validation_results/validation_results.png
  ✓ Saved detailed confusion matrix: validation_results/confusion_matrix_detailed.png
  ✓ Saved results to: validation_results/validation_results.json
  ✓ Saved summary to: validation_results/validation_summary.txt

✓ All results saved to validation_results/

======================================================================
```

## Анализ проблем

### Если accuracy низкая (<70%)

1. Проверьте качество входных изображений
2. Проверьте правильность ground truth labels
3. Проверьте промпт модели
4. Возможно нужно fine-tuning или другая модель

### Если confusion между определенными классами

Например, если Spring часто путается с Fall:
- Посмотрите примеры ошибок
- Возможно нужно улучшить описание этих сезонов в промпте
- Или добавить больше специфичных признаков

### Если confidence низкая

- Модель не уверена в своих предсказаниях
- Возможно изображения неоднозначные
- Или нужно более четкий промпт

## Расширения

### Добавить анализ ошибок по изображениям

Можно модифицировать скрипт для отображения самых проблемных изображений:

```python
# В конце run_validation()
show_error_examples(ground_truth, predictions, confidences, n=5)
```

### Добавить сравнение с baseline

Сравнить с random guess или simple heuristic:

```python
random_accuracy = 0.25  # 25% для 4 классов
improvement = (accuracy - random_accuracy) / random_accuracy * 100
print(f"Improvement over random: {improvement:.1f}%")
```

### Экспорт для презентации

```python
# Сохранить в PDF
from matplotlib.backends.backend_pdf import PdfPages
with PdfPages('validation_report.pdf') as pdf:
    for fig in figures:
        pdf.savefig(fig)
```

## Troubleshooting

### Ошибка: "Connection refused"
- Проверьте, что сервер запущен на `http://localhost:8000`
- Проверьте порт в `API_BASE` переменной

### Ошибка: "Image not found"
- Проверьте путь к `data/valid/`
- Проверьте что все файлы из `_classes.csv` существуют

### Ошибка: "Module not found: matplotlib"
- Запустите `uv sync` для установки зависимостей

### Predictions fail with timeout
- Увеличьте `timeout` в `predict_image()`
- Или обрабатывайте меньшими батчами

## Автоматизация

### Cron job для регулярной валидации

```bash
# Добавить в crontab
0 2 * * * cd /path/to/project && ./run_validation.sh
```

### CI/CD интеграция

```yaml
# .github/workflows/validate.yml
name: Model Validation
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run validation
        run: |
          uv sync
          uv run python validate_model.py
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: validation-results
          path: validation_results/
```

## Советы

1. **Запускайте валидацию регулярно** - после каждого изменения промпта или модели
2. **Сохраняйте результаты с версионированием** - для отслеживания прогресса
3. **Анализируйте ошибки детально** - смотрите на конкретные проблемные изображения
4. **Сравнивайте между версиями** - какие изменения улучшили результаты
5. **Документируйте находки** - что работает, что нет

---

Удачи с валидацией! 🚀

