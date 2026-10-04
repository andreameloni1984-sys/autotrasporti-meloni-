import os
import requests
from database import get_unnotified, mark_notified

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def send_message(text):
    if not TOKEN or not CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            json={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True},
            timeout=20
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def send_unnotified():
    rows = get_unnotified()

    if not rows:
        return 0

    sent_ids = []

    for row in rows:
        (
            item_id,
            title,
            url,
            source,
            categories,
            score,
            deadline,
            status,
            benefit
        ) = row

        message = (
            f"🚛 AUTOTRASPORTI MELONI\n\n"
            f"{title}\n"
            f"Fonte: {source}\n"
            f"Score: {score}\n"
            f"Stato: {status}\n"
            f"Link: {url}"
        )

        if send_message(message):
            sent_ids.append(item_id)

    mark_notified(sent_ids)
    return len(sent_ids)
