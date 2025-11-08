# User Profile API Documentation

API для управления профилем пользователя в системе подбора одежды.

## Обзор

Все endpoints требуют авторизации через JWT токен в заголовке `Authorization: Bearer <token>`.

Базовый URL: `/api/user`

## Endpoints

### 1. GET /api/user/profile
Получить профиль текущего пользователя.

**Требования:**
- Авторизация: Да

**Ответ:**
- 200 OK: Возвращает профиль пользователя
- 404 Not Found: Профиль не найден (еще не создан)

**Пример ответа:**
```json
{
  "id": 1,
  "user_id": 1,
  "height": 175.5,
  "weight": 70.0,
  "chest_size": 95.0,
  "waist_size": 80.0,
  "hip_size": 98.0,
  "shoe_size": 42.0,
  "clothing_size": "M",
  "age": 25,
  "gender": "female",
  "preferred_style": "casual",
  "body_image_url": "data/user_images/user_1_body_20250108_143022.jpg",
  "face_image_url": "data/user_images/user_1_face_20250108_143022.jpg",
  "created_at": "2025-01-08T14:30:22",
  "updated_at": "2025-01-08T14:30:22"
}
```

### 2. POST /api/user/profile
Создать или обновить профиль пользователя.

**Требования:**
- Авторизация: Да
- Все поля опциональны - пользователь может заполнить только те данные, которые хочет

**Тело запроса:**
```json
{
  "height": 175.5,
  "weight": 70.0,
  "chest_size": 95.0,
  "waist_size": 80.0,
  "hip_size": 98.0,
  "shoe_size": 42.0,
  "clothing_size": "M",
  "age": 25,
  "gender": "female",
  "preferred_style": "casual",
  "body_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Параметры:**
- `height` (float, optional): Рост в сантиметрах (должен быть > 0)
- `weight` (float, optional): Вес в килограммах (должен быть > 0)
- `chest_size` (float, optional): Обхват груди в сантиметрах (должен быть > 0)
- `waist_size` (float, optional): Обхват талии в сантиметрах (должен быть > 0)
- `hip_size` (float, optional): Обхват бедер в сантиметрах (должен быть > 0)
- `shoe_size` (float, optional): Размер обуви (EU стандарт, должен быть > 0)
- `clothing_size` (string, optional): Размер одежды (S, M, L, XL, и т.д.)
- `age` (int, optional): Возраст в годах (должен быть > 0 и < 150)
- `gender` (string, optional): Пол (male, female, other)
- `preferred_style` (string, optional): Предпочитаемый стиль одежды
- `body_image` (string, optional): Фото всего тела в формате base64
- `face_image` (string, optional): Фото лица в формате base64

**Ответ:**
- 201 Created: Профиль создан/обновлен успешно
- 400 Bad Request: Неверные данные

**Примечания:**
- Изображения должны быть в формате base64 с префиксом `data:image/xxx;base64,` или без него
- Изображения сохраняются на сервере, а в профиле хранится путь к файлу
- Если профиль уже существует, он будет обновлен

### 3. PUT /api/user/profile
Обновить профиль пользователя (алиас для POST /profile).

**Требования и параметры такие же, как у POST /api/user/profile**

### 4. DELETE /api/user/profile
Удалить профиль пользователя.

**Требования:**
- Авторизация: Да

**Ответ:**
- 204 No Content: Профиль удален успешно
- 404 Not Found: Профиль не найден

**Примечание:**
- Также удаляются все связанные изображения с файловой системы

### 5. GET /api/user/profile/completeness
Получить процент заполненности профиля.

**Требования:**
- Авторизация: Да

**Ответ:**
```json
{
  "completeness": 75.0,
  "total_fields": 12,
  "filled_fields": 9,
  "missing_fields": ["age", "preferred_style", "face_image"]
}
```

**Описание полей:**
- `completeness`: Процент заполненности профиля (0-100)
- `total_fields`: Общее количество полей в профиле
- `filled_fields`: Количество заполненных полей
- `missing_fields`: Список незаполненных полей

## Примеры использования (Frontend)

### React/TypeScript пример

```typescript
// API client
const API_BASE_URL = 'http://localhost:8000';

interface UserProfile {
  height?: number;
  weight?: number;
  chest_size?: number;
  waist_size?: number;
  hip_size?: number;
  shoe_size?: number;
  clothing_size?: string;
  age?: number;
  gender?: string;
  preferred_style?: string;
  body_image?: string;
  face_image?: string;
}

// Получить профиль
async function getUserProfile(token: string) {
  const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 404) {
    return null; // Профиль не создан
  }
  
  if (!response.ok) {
    throw new Error('Failed to fetch profile');
  }
  
  return await response.json();
}

// Создать/обновить профиль
async function updateUserProfile(token: string, profile: UserProfile) {
  const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(profile)
  });
  
  if (!response.ok) {
    throw new Error('Failed to update profile');
  }
  
  return await response.json();
}

// Конвертировать файл в base64
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Пример onboarding формы
async function handleOnboardingSubmit(formData: FormData, token: string) {
  const profile: UserProfile = {};
  
  // Базовые измерения
  const height = formData.get('height');
  if (height) profile.height = parseFloat(height as string);
  
  const weight = formData.get('weight');
  if (weight) profile.weight = parseFloat(weight as string);
  
  // Другие поля...
  
  // Изображения
  const bodyImageFile = formData.get('bodyImage') as File;
  if (bodyImageFile) {
    profile.body_image = await fileToBase64(bodyImageFile);
  }
  
  const faceImageFile = formData.get('faceImage') as File;
  if (faceImageFile) {
    profile.face_image = await fileToBase64(faceImageFile);
  }
  
  // Отправить на сервер
  await updateUserProfile(token, profile);
}

// Получить прогресс заполнения профиля
async function getProfileCompleteness(token: string) {
  const response = await fetch(`${API_BASE_URL}/api/user/profile/completeness`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch completeness');
  }
  
  return await response.json();
}
```

### Пример Vue.js компонента

```vue
<template>
  <div class="onboarding">
    <h1>Complete Your Profile</h1>
    <div class="progress">
      <div class="progress-bar" :style="{ width: `${completeness}%` }"></div>
      <span>{{ completeness }}% Complete</span>
    </div>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-section">
        <h2>Body Measurements</h2>
        <input v-model.number="profile.height" type="number" placeholder="Height (cm)" step="0.1" />
        <input v-model.number="profile.weight" type="number" placeholder="Weight (kg)" step="0.1" />
        <input v-model.number="profile.chest_size" type="number" placeholder="Chest (cm)" step="0.1" />
        <input v-model.number="profile.waist_size" type="number" placeholder="Waist (cm)" step="0.1" />
        <input v-model.number="profile.hip_size" type="number" placeholder="Hips (cm)" step="0.1" />
        <input v-model.number="profile.shoe_size" type="number" placeholder="Shoe Size (EU)" step="0.5" />
        <input v-model="profile.clothing_size" type="text" placeholder="Clothing Size (S/M/L/XL)" />
      </div>
      
      <div class="form-section">
        <h2>Personal Information</h2>
        <input v-model.number="profile.age" type="number" placeholder="Age" />
        <select v-model="profile.gender">
          <option value="">Select Gender</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
        <input v-model="profile.preferred_style" type="text" placeholder="Preferred Style" />
      </div>
      
      <div class="form-section">
        <h2>Photos</h2>
        <div class="image-upload">
          <label>Body Photo</label>
          <input type="file" @change="handleBodyImageChange" accept="image/*" />
          <img v-if="bodyImagePreview" :src="bodyImagePreview" alt="Body preview" />
        </div>
        
        <div class="image-upload">
          <label>Face Photo</label>
          <input type="file" @change="handleFaceImageChange" accept="image/*" />
          <img v-if="faceImagePreview" :src="faceImagePreview" alt="Face preview" />
        </div>
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? 'Saving...' : 'Save Profile' }}
      </button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      profile: {
        height: null,
        weight: null,
        chest_size: null,
        waist_size: null,
        hip_size: null,
        shoe_size: null,
        clothing_size: '',
        age: null,
        gender: '',
        preferred_style: ''
      },
      bodyImagePreview: null,
      faceImagePreview: null,
      loading: false,
      completeness: 0
    };
  },
  
  async mounted() {
    await this.loadProfile();
    await this.loadCompleteness();
  },
  
  methods: {
    async loadProfile() {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/user/profile', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          const data = await response.json();
          this.profile = { ...this.profile, ...data };
        }
      } catch (error) {
        console.log('No profile yet');
      }
    },
    
    async loadCompleteness() {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/user/profile/completeness', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        this.completeness = data.completeness;
      } catch (error) {
        console.error('Failed to load completeness', error);
      }
    },
    
    handleBodyImageChange(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.bodyImagePreview = e.target.result;
          this.profile.body_image = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    
    handleFaceImageChange(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.faceImagePreview = e.target.result;
          this.profile.face_image = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    
    async handleSubmit() {
      this.loading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/user/profile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(this.profile)
        });
        
        if (response.ok) {
          alert('Profile saved successfully!');
          await this.loadCompleteness();
        } else {
          alert('Failed to save profile');
        }
      } catch (error) {
        console.error('Error saving profile:', error);
        alert('Error saving profile');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

## Структура базы данных

```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    height REAL,
    weight REAL,
    chest_size REAL,
    waist_size REAL,
    hip_size REAL,
    shoe_size REAL,
    clothing_size TEXT,
    age INTEGER,
    gender TEXT,
    preferred_style TEXT,
    body_image_url TEXT,
    face_image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Важные замечания

1. **Авторизация**: Все endpoints требуют JWT токен в заголовке Authorization
2. **Опциональность**: Все поля профиля опциональны - пользователь может не заполнять то, что не хочет
3. **Изображения**: 
   - Изображения хранятся в `data/user_images/`
   - Формат имени файла: `user_{user_id}_{type}_{timestamp}.jpg`
   - Изображения автоматически удаляются при удалении профиля
4. **Безопасность**: Каждый пользователь может работать только со своим профилем
5. **Валидация**: 
   - Числовые значения должны быть > 0
   - Возраст должен быть от 0 до 150 лет
   - Base64 изображения должны быть валидными

## Тестирование API

### Используя curl

```bash
# Получить токен (сначала нужно зарегистрироваться/войти)
TOKEN="your_jwt_token_here"

# Получить профиль
curl -X GET http://localhost:8000/api/user/profile \
  -H "Authorization: Bearer $TOKEN"

# Создать/обновить профиль
curl -X POST http://localhost:8000/api/user/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "height": 175.5,
    "weight": 70.0,
    "chest_size": 95.0,
    "clothing_size": "M",
    "age": 25,
    "gender": "female"
  }'

# Получить процент заполненности
curl -X GET http://localhost:8000/api/user/profile/completeness \
  -H "Authorization: Bearer $TOKEN"

# Удалить профиль
curl -X DELETE http://localhost:8000/api/user/profile \
  -H "Authorization: Bearer $TOKEN"
```

### Используя Python requests

```python
import requests
import base64

API_BASE = "http://localhost:8000"
token = "your_jwt_token_here"
headers = {"Authorization": f"Bearer {token}"}

# Получить профиль
response = requests.get(f"{API_BASE}/api/user/profile", headers=headers)
if response.status_code == 200:
    profile = response.json()
    print(profile)
elif response.status_code == 404:
    print("Profile not found")

# Создать профиль с изображением
with open("body_photo.jpg", "rb") as f:
    body_image_b64 = base64.b64encode(f.read()).decode()

profile_data = {
    "height": 175.5,
    "weight": 70.0,
    "body_image": f"data:image/jpeg;base64,{body_image_b64}"
}

response = requests.post(
    f"{API_BASE}/api/user/profile",
    json=profile_data,
    headers={**headers, "Content-Type": "application/json"}
)

if response.status_code == 201:
    print("Profile created:", response.json())
```

