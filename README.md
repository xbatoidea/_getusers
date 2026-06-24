# Active Directory Telegram Bot

Это пример Telegram-бота для просмотра и разблокировки пользователей.

## Установка

1. Установи Python 3.11+
2. Создай виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Установи зависимости:
   ```bash
   pip install python-telegram-bot ldap3
   ```

## Настройка

1. Получи токен бота у @BotFather.
2. Установи переменные окружения:
   ```bash
   export TG_BOT_TOKEN="токен"
   export AD_SERVER="ldap://your.ad.server"
   export AD_USER="DOMAIN\\username"
   export AD_PASSWORD="password"
   export AD_BASE_DN="DC=example,DC=com"
   export AD_USE_SSL="false"
   ```

## Запуск

1. Создай виртуальное окружение и активируй его:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Установи переменные окружения:
   ```bash
   export TG_BOT_TOKEN="токен"
   export AD_SERVER="ldaps://public-hostname:636"
   export AD_USER="DOMAIN\\username"
   export AD_PASSWORD="password"
   export AD_BASE_DN="DC=example,DC=com"
   export AD_USE_SSL="true"
   ```
4. Запусти бота:
   ```bash
   python src/bot.py
   ```

## Деплой на Railway

1. Создай проект на Railway.
2. Подключи репозиторий `xbatoidea/_getusers`.
3. Добавь переменные окружения в Railway:
   - `TG_BOT_TOKEN`
   - `AD_SERVER`
   - `AD_USER`
   - `AD_PASSWORD`
   - `AD_BASE_DN`
   - `AD_USE_SSL`
4. Укажи `Procfile` в корне:
   ```text
   web: python src/bot.py
   ```
5. Запусти деплой.

## Команды

- `/start` — приветствие
- `/blocked` — список отключенных пользователей AD
- `/unblock <username>` — разблокировать пользователя в AD

## Примечания

- В `README.md` указаны переменные окружения для подключения к Active Directory.
- `data/blocked_users.json` не используется теперь, но оставлен как пример локального хранилища.
