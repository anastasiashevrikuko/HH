import httpx
from bs4 import BeautifulSoup
import json
import os

HH_URL = 'https://hh.ru/vacancies/product_manager'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
}
SEEN_FILE = 'seen.json'
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def load_seen():
    try:
        with open(SEEN_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(seen), f)


def get_vacancies():
    with httpx.Client(http2=True, headers=HEADERS, timeout=10.0) as client:
        resp = client.get(HH_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.find_all('a', {'data-qa': 'serp-item__title'})
        return {item['href'] for item in items}


def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': text}
    httpx.post(url, data=data)


def main():
    seen = load_seen()
    current = get_vacancies()
    new = current - seen

    if new:
        for url in new:
            send_telegram_message(url)
    else:
        send_telegram_message("Новых вакансий нет")

    save_seen(current)


if __name__ == "__main__":
    main()