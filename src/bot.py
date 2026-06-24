import os
import logging
from typing import List, Optional
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AD_SERVER = os.environ.get("AD_SERVER")
AD_USER = os.environ.get("AD_USER")
AD_PASSWORD = os.environ.get("AD_PASSWORD")
AD_BASE_DN = os.environ.get("AD_BASE_DN")
AD_USE_SSL = os.environ.get("AD_USE_SSL", "false").lower() in ("1", "true", "yes")


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}")
    return value


def connect_ldap() -> Connection:
    server = Server(AD_SERVER, use_ssl=AD_USE_SSL, get_info=ALL)
    conn = Connection(server, user=AD_USER, password=AD_PASSWORD, authentication=NTLM, auto_bind=True)
    return conn


def search_disabled_users(conn: Connection) -> List[dict]:
    search_filter = "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))"
    conn.search(
        search_base=AD_BASE_DN,
        search_filter=search_filter,
        attributes=["sAMAccountName", "displayName", "userPrincipalName"],
    )
    return [
        {
            "username": entry.sAMAccountName.value if hasattr(entry, "sAMAccountName") else "",
            "display_name": entry.displayName.value if hasattr(entry, "displayName") else "",
            "upn": entry.userPrincipalName.value if hasattr(entry, "userPrincipalName") else "",
        }
        for entry in conn.entries
    ]


def enable_account(conn: Connection, username: str) -> bool:
    filter_by_name = f"(|(sAMAccountName={username})(userPrincipalName={username}))"
    conn.search(
        search_base=AD_BASE_DN,
        search_filter=f"(&(objectCategory=person)(objectClass=user){filter_by_name})",
        attributes=["distinguishedName", "userAccountControl"],
    )
    if not conn.entries:
        return False

    entry = conn.entries[0]
    dn = entry.distinguishedName.value
    uac = int(entry.userAccountControl.value)
    new_uac = uac & ~2
    conn.modify(dn, {"userAccountControl": [(conn.MODIFY_REPLACE, [str(new_uac)])]})
    return conn.result and conn.result.get("description") == "success"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для управления Active Directory.\n"
        "Используй /blocked, чтобы увидеть отключенные пользователи.\n"
        "Используй /unblock <username>, чтобы включить учетную запись.\n"
    )


async def blocked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = connect_ldap()
    except Exception as exc:
        logger.exception("Ошибка подключения к AD")
        await update.message.reply_text(f"Не удалось подключиться к AD: {exc}")
        return

    users = search_disabled_users(conn)
    if not users:
        await update.message.reply_text("Нет отключенных пользователей в Active Directory.")
        return

    lines = [f"{u['username']} — {u.get('display_name', 'нет имени')}" for u in users]
    await update.message.reply_text("Отключенные пользователи:\n" + "\n".join(lines))


async def unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Укажи имя пользователя: /unblock <username>")
        return

    username = args[0].lstrip("@")
    try:
        conn = connect_ldap()
    except Exception as exc:
        logger.exception("Ошибка подключения к AD")
        await update.message.reply_text(f"Не удалось подключиться к AD: {exc}")
        return

    success = enable_account(conn, username)
    if not success:
        await update.message.reply_text(f"Пользователь {username} не найден или не удалось изменить запись.")
        return

    await update.message.reply_text(f"Учетная запись {username} разблокирована в AD.")


def build_app(token: str):
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("blocked", blocked))
    app.add_handler(CommandHandler("unblock", unblock))
    return app


if __name__ == "__main__":
    token = os.environ.get("TG_BOT_TOKEN")
    if not token:
        raise RuntimeError("Поставь TG_BOT_TOKEN в окружении перед запуском")

    required = ["AD_SERVER", "AD_USER", "AD_PASSWORD", "AD_BASE_DN"]
    for name in required:
        if not os.environ.get(name):
            raise RuntimeError(f"Поставь переменную окружения {name}")

    app = build_app(token)
    app.run_polling()
