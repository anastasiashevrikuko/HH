import json
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import os

HH_URL = 'https://hh.ru/vacancies/product_manager'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
SEEN_FILE = 'seen.json'

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
bot = Bot(token=TELEGRAM_TOKEN)

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
    resp = requests.get(HH_URL, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = soup.find_all('a', {'data-qa': 'serp-item__title'})
    return [(item.text.strip(), item['href']) for item in items]

def send_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print("Ошибка отправки:", e)

def main():
    seen = load_seen()
    vacancies = get_vacancies()
    new = []
    for title, link in vacancies:
        if link not in seen:
            seen.add(link)
            new.append(f"{title}\n{link}")
    if new:
        for msg in new:
            send_message(msg)
        save_seen(seen)
    else:
        send_message("Новых вакансий нет, проверил hh.ru")

if __name__ == '__main__':
    main()