# Реферальная система (API)  

Простая система для регистрации пользователей по номеру телефона и работы с реферальными кодами.  

## API Endpoints  

### 1. Авторизация по номеру телефона  
**Запрос:**  
`POST /api/auth/`  
**Тело запроса (JSON):**  
```json
{
    "phone_number": "+79991234567"
}
```
**Ответ:**  
```json
{
    "message": "Code sent"
}
```
*(Симуляция отправки SMS с кодом, задержка 1-2 сек.)*  

---  

### 2. Подтверждение кода  
**Запрос:**  
`POST /api/verify/`  
**Тело запроса (JSON):**  
```json
{
    "code": "1234"  // 4 цифры (любые, в текущей реализации)
}
```
**Ответ (успех):**  
```json
{
    "message": "Authenticated",
    "invite_code": "A1B2C3"  // 6-значный код пользователя
}
```
**Ошибки:**  
- `400` – неверный формат кода.  
- `404` – номер телефона не найден в сессии.  

---  

### 3. Профиль пользователя  
#### Получить профиль  
**Запрос:**  
`GET /api/profile/`  
**Ответ:**  
```json
{
    "phone_number": "+79991234567",
    "invite_code": "A1B2C3",
    "activated_invite_code": "XYZ789",  // если есть
    "referrals": ["+79997776655"]       // список рефералов
}
```

#### Активировать инвайт-код  
**Запрос:**  
`POST /api/profile/`  
**Заголовки запроса:**

Обязательно нужно в Headers добавить:
```
    X-CSRFToken: abc123...  # Значение из куки csrftoken 
```

**Тело запроса (JSON):**  
```json
{
    "invite_code": "XYZ789"  // чужой 6-значный код
}
```
**Ответ (успех):**  
```json
{
    "status": "Code successfully activated",
    "activated_invite_code": "XYZ789"
}
```
**Ошибки:**  
- `400` – нельзя активировать свой код или уже есть активный.  
- `404` – код не существует.  

### 4. Выход из системы (Logout)  

**Запрос:**  
`POST /api/logout/`  

**Заголовки запроса:**  
Обязательно нужно в Headers добавить:  
```
X-CSRFToken: abc123...  # Значение из куки csrftoken  
```  

**Ответ (успех):**  
```json
{
    "status": "success",
    "message": "Successfully logged out"
}
```  

**Ошибки:**  
- `403` – CSRF-токен неверный или отсутствует.  

---  

### Как получить CSRF-токен для Logout и `POST /api/profile`:  
1. После успешной авторизации (через `/api/verify/`), сервер устанавливает:  
   - Куки `csrftoken` (CSRF-токен)  
   - Куки `sessionid` (идентификатор сессии)  

2. Для выполнения Logout и `POST /api/profile`:  
   - Извлеките значение `csrftoken` из куков  
   - Добавьте его в заголовок `X-CSRFToken`  
   - Убедитесь, что куки `sessionid` передаются с запросом  

---  

## Как запустить  
1.  Убедитесь, что Docker и Docker Compose установлены.
2.  Создайте файл `.env` в корневой директории проекта (рядом с `docker-compose.yml`) со следующим содержимым (замените `ваш-секретный-ключ` на реальный ключ): 
   ```bash
   # Настройки PostgreSQL 
    POSTGRES_DB=<Имя базы данных>
    POSTGRES_USER=<Имя пользователя>
    POSTGRES_PASSWORD=<Пароль пользователя> 
    POSTGRES_PORT=<Внешний порт для вашей бд>

    # Django настройки
    SECRET_KEY=<ваш-секретный-ключ>
    DEBUG=True/False
    ALLOWED_HOSTS=*

    # DB настройки в Django
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=<Имя базы данных>
    DB_USER=<Имя пользователя>
    DB_PASSWORD=<Пароль пользователя>
    DB_HOST=db
    DB_PORT=<Порт базы данных>
   ```
Пример .env файла:
   ```bash
    POSTGRES_DB=referral_system
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=1521
    POSTGRES_PORT=5432

    SECRET_KEY='=r5g7e()tez3hw%kycl9@0u$)e@auf%1^$#962&ftm1-_kmf5m'
    DEBUG=True
    ALLOWED_HOSTS=*

    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=referral_system
    DB_USER=admin
    DB_PASSWORD=1521
    DB_HOST=db
    DB_PORT=5432
   ```
*(Убедитесь, что значения `POSTGRES_*` совпадают с `DB_*` для корректной работы).*

3.  Убедитесь, что файлы `Dockerfile` и `docker-compose.yml` находятся в корневой директории проекта и содержат исправленные настройки томов и сервисов, как показано выше.
4.  Запустите проект с помощью Docker Compose:
    ```bash
    docker-compose up --build
    ```
    Эта команда соберет образы, создаст и запустит контейнеры в фоновом режиме. Миграции будут применены автоматически.
5.  Приложение будет доступно по адресу `http://localhost:8000`.
6.  Для остановки контейнера используйте:
    ```bash
    docker-compose down
    ```