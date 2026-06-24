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

```bash
python src/bot.py
```

## Команды

- `/start` — приветствие
- `/blocked` — список заблокированных пользователей
- `/unblock <username>` — разблокировать пользователя
