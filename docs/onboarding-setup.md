# User Onboarding Setup Guide

## Обзор

Эта система позволяет пользователям заполнить свой профиль с информацией о параметрах тела, предпочтениях и фотографиями. Все данные являются опциональными - пользователь может выбрать, что он хочет предоставить.

## Что было добавлено

### 1. База данных
- **Новая таблица**: `user_profiles` для хранения информации о пользователе
- **Поля профиля**:
  - Измерения тела: рост, вес, обхват груди/талии/бедер, размер обуви
  - Размер одежды (S, M, L, XL и т.д.)
  - Личная информация: возраст, пол, предпочитаемый стиль
  - Фотографии: полное тело и лицо
  - Timestamps: created_at, updated_at

### 2. API Endpoints
- `GET /api/user/profile` - Получить профиль пользователя
- `POST /api/user/profile` - Создать или обновить профиль
- `PUT /api/user/profile` - Обновить профиль (алиас для POST)
- `DELETE /api/user/profile` - Удалить профиль
- `GET /api/user/profile/completeness` - Получить процент заполненности профиля

### 3. Файлы
```
hackseoul_fe/
├── src/
│   ├── api/
│   │   └── user_info.py          # Новый API модуль
│   ├── database/
│   │   └── user_db.py            # Обновлен: добавлена модель UserProfile
│   └── models.py                  # Обновлен: добавлены Pydantic модели
├── data/
│   └── user_images/               # Новая директория для фото пользователей
├── docs/
│   ├── user-profile-api.md        # Полная документация API
│   └── onboarding-setup.md        # Этот файл
├── migrate_db.py                  # Скрипт миграции БД
└── test_user_profile.py           # Тестовый скрипт
```

## Установка и настройка

### Шаг 1: Миграция базы данных

После клонирования/обновления кода, запустите миграцию:

```bash
python migrate_db.py
```

Этот скрипт:
- Создаст новую таблицу `user_profiles`
- Создаст директорию `data/user_images/` для хранения фотографий
- Проверит все таблицы в базе данных

### Шаг 2: Запуск сервера

```bash
python app.py
```

Сервер запустится на `http://localhost:8000`

### Шаг 3: Тестирование

Запустите тестовый скрипт для проверки функциональности:

```bash
python test_user_profile.py
```

Этот скрипт автоматически:
1. Зарегистрирует тестового пользователя
2. Проверит начальную заполненность профиля (0%)
3. Создаст профиль с частичными данными
4. Обновит профиль с дополнительными данными
5. Покажет финальный процент заполненности

## Использование в Frontend

### Базовый пример (React)

```jsx
import { useState, useEffect } from 'react';

function OnboardingForm({ token }) {
  const [profile, setProfile] = useState({
    height: '',
    weight: '',
    chest_size: '',
    waist_size: '',
    hip_size: '',
    shoe_size: '',
    clothing_size: '',
    age: '',
    gender: '',
    preferred_style: ''
  });
  const [completeness, setCompleteness] = useState(0);
  
  // Загрузить существующий профиль при монтировании
  useEffect(() => {
    loadProfile();
    loadCompleteness();
  }, []);
  
  const loadProfile = async () => {
    const response = await fetch('http://localhost:8000/api/user/profile', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      setProfile(data);
    }
  };
  
  const loadCompleteness = async () => {
    const response = await fetch('http://localhost:8000/api/user/profile/completeness', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      setCompleteness(data.completeness);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const response = await fetch('http://localhost:8000/api/user/profile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(profile)
    });
    
    if (response.ok) {
      alert('Profile saved!');
      loadCompleteness();
    }
  };
  
  return (
    <div>
      <h2>Complete Your Profile ({completeness}%)</h2>
      <form onSubmit={handleSubmit}>
        {/* Поля формы */}
        <input
          type="number"
          placeholder="Height (cm)"
          value={profile.height}
          onChange={(e) => setProfile({...profile, height: e.target.value})}
        />
        {/* ... остальные поля ... */}
        <button type="submit">Save Profile</button>
      </form>
    </div>
  );
}
```

### Загрузка изображений

```jsx
function ImageUpload({ token, onUpdate }) {
  const handleImageUpload = async (e, type) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Конвертировать в base64
    const reader = new FileReader();
    reader.onload = async () => {
      const base64Image = reader.result;
      
      // Отправить на сервер
      const body = type === 'body' 
        ? { body_image: base64Image }
        : { face_image: base64Image };
      
      const response = await fetch('http://localhost:8000/api/user/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(body)
      });
      
      if (response.ok) {
        onUpdate();
      }
    };
    reader.readAsDataURL(file);
  };
  
  return (
    <div>
      <label>
        Body Photo:
        <input
          type="file"
          accept="image/*"
          onChange={(e) => handleImageUpload(e, 'body')}
        />
      </label>
      
      <label>
        Face Photo:
        <input
          type="file"
          accept="image/*"
          onChange={(e) => handleImageUpload(e, 'face')}
        />
      </label>
    </div>
  );
}
```

## UX рекомендации

### 1. Постепенное заполнение
Не заставляйте пользователя заполнять все сразу. Позвольте:
- Пропускать шаги
- Заполнять позже
- Сохранять частично заполненный профиль

### 2. Показывайте прогресс
```jsx
<ProgressBar value={completeness} />
<p>{completeness}% complete</p>
```

### 3. Объясните зачем нужны данные
```jsx
<Tooltip>
  "We use your height and weight to recommend the best fitting clothes"
</Tooltip>
```

### 4. Предпросмотр фото
Покажите превью загруженных фотографий перед отправкой.

### 5. Мобильная оптимизация
- Используйте `capture="environment"` для камеры на мобильных
- Оптимизируйте размер изображений перед отправкой
- Показывайте индикатор загрузки для больших файлов

## Примеры UI компонентов

### Шаговая форма onboarding

```jsx
function OnboardingWizard() {
  const [step, setStep] = useState(1);
  const totalSteps = 4;
  
  return (
    <div className="wizard">
      <StepIndicator current={step} total={totalSteps} />
      
      {step === 1 && <MeasurementsStep />}
      {step === 2 && <PersonalInfoStep />}
      {step === 3 && <PhotosStep />}
      {step === 4 && <ReviewStep />}
      
      <div className="navigation">
        {step > 1 && <button onClick={() => setStep(step - 1)}>Back</button>}
        {step < totalSteps && <button onClick={() => setStep(step + 1)}>Next</button>}
        {step === totalSteps && <button>Complete</button>}
        <button>Skip for now</button>
      </div>
    </div>
  );
}
```

### Карточка профиля

```jsx
function ProfileCard({ profile, completeness }) {
  return (
    <div className="profile-card">
      <div className="avatar">
        {profile.face_image_url ? (
          <img src={profile.face_image_url} alt="Profile" />
        ) : (
          <DefaultAvatar />
        )}
      </div>
      
      <h3>{profile.email}</h3>
      
      <div className="stats">
        <Stat label="Height" value={`${profile.height} cm`} />
        <Stat label="Size" value={profile.clothing_size} />
      </div>
      
      <ProgressBar value={completeness} label="Profile completeness" />
      
      <button>Edit Profile</button>
    </div>
  );
}
```

## Безопасность

### Изображения
- Изображения хранятся локально в `data/user_images/`
- Имена файлов включают user_id для изоляции
- При удалении профиля изображения также удаляются

### Авторизация
- Все endpoints требуют JWT токен
- Пользователь может работать только со своим профилем
- Токен проверяется middleware `get_current_user`

### Валидация
- Все числовые значения должны быть > 0
- Возраст ограничен: 0 < age < 150
- Base64 изображения проверяются на валидность

## Интеграция с другими функциями

### Подбор одежды
Данные профиля можно использовать для:
- Рекомендации размера
- Фильтрация по стилю
- Персонализированные предложения

Пример:
```python
# В сервисе рекомендаций
def get_recommendations(user_id, db):
    profile = db.query(UserProfile).filter_by(user_id=user_id).first()
    
    filters = {}
    if profile:
        if profile.clothing_size:
            filters['size'] = profile.clothing_size
        if profile.preferred_style:
            filters['style'] = profile.preferred_style
    
    return filter_products(filters)
```

### Виртуальная примерка
Используйте body_image_url для try-on функциональности:
```python
if profile and profile.body_image_url:
    result = generate_try_on(profile.body_image_url, product_image)
```

## Troubleshooting

### Проблема: 404 при GET /api/user/profile
**Решение**: Это нормально, если пользователь еще не создал профиль. Обработайте этот случай в UI.

### Проблема: 400 Bad Request при загрузке изображения
**Решение**: Проверьте формат base64. Убедитесь, что используется правильный префикс `data:image/xxx;base64,`

### Проблема: Изображения не сохраняются
**Решение**: Убедитесь, что директория `data/user_images/` существует и имеет права на запись.

### Проблема: Старая схема БД
**Решение**: Запустите `python migrate_db.py` для обновления схемы.

## API тестирование с curl

```bash
# 1. Зарегистрироваться
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 2. Получить токен (из ответа выше или логин)
TOKEN="your_token_here"

# 3. Создать профиль
curl -X POST http://localhost:8000/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "height": 175,
    "weight": 70,
    "clothing_size": "M",
    "gender": "female"
  }'

# 4. Получить профиль
curl http://localhost:8000/profile \
  -H "Authorization: Bearer $TOKEN"

# 5. Проверить заполненность
curl http://localhost:8000/profile/completeness \
  -H "Authorization: Bearer $TOKEN"
```

## Следующие шаги

1. **Frontend разработка**: Создайте красивый onboarding flow
2. **Валидация**: Добавьте больше валидаций на фронте
3. **Оптимизация изображений**: Сжимайте изображения перед загрузкой
4. **Аналитика**: Отслеживайте, какие поля заполняются чаще всего
5. **A/B тестирование**: Тестируйте разные подходы к onboarding

## Контакты и поддержка

При возникновении вопросов:
1. Проверьте логи сервера
2. Запустите тестовый скрипт
3. Проверьте документацию API в `/docs/user-profile-api.md`
4. Посмотрите Swagger UI на `http://localhost:8000/docs`

