# bot.py


import requests
import schedule
import time
import asyncio
from datetime import datetime
from telegram import Bot
from config import TELEGRAM_TOKEN, CHANNEL_ID, OPENAI_API_KEY
print("Переменные загружены")
print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN[:5], "...")
print("CHANNEL_ID:", CHANNEL_ID)
print("OPENAI_API_KEY:", OPENAI_API_KEY[:5], "...")

bot = Bot(token=TELEGRAM_TOKEN)

def get_ai_news():
    today = datetime.now().strftime("%d.%m.%Y")
    print(f"🔍 Запрашиваем новость на дату: {today}")

    prompt = (
        f"Сгенерируй одну свежую новость из мира науки и технологий (AI, изобретения, космос, медицина и т.п.) "
        f"за {today}. Сначала придумай короткий, интригующий заголовок (до 10 слов), используй эмодзи в начале и в конце, "
        f"выдели его жирным HTML-тегом <b>. Затем напиши саму новость: 4–9 предложений, каждое с новой строки, между абзацами используй эмодзи по теме. "
        f"Пиши эмоционально и захватывающе. После основного текста добавь строку: 'Источник: [реальная ссылка]'."
    )

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.encoding = 'utf-8'
        result = response.json()
        print("Ответ OpenAI:", result)
        text = result["choices"][0]["message"]["content"]
        text = text.replace("<h2>", "<b>").replace("</h2>", "</b>")
        return text
    except Exception as e:
        print(f"❌ Ошибка при получении новости: {e}")
        print(" ! Текст ответа OpenAI:", response.text)
        return None

def generate_dalle_image(prompt):
    print(f"🧠 Генерируем изображение по теме: {prompt}")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=json_data)
        result = response.json()
        return result["data"][0]["url"]
    except Exception as e:
        print(f"❌ Ошибка при генерации изображения: {e}")
        return None

async def post_news():
    news = get_ai_news()
    if not news:
        return

    first_line = news.splitlines()[0]
    query = " ".join(first_line.strip("⭐🔥🚀🌍🧬⚡🧠").split()[1:5])

    image_url = generate_dalle_image(query)

    try:
        if image_url:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=news, parse_mode="HTML")
            print("✅ Новость с изображением опубликована.")
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=news, parse_mode="HTML")
            print("✅ Новость без изображения опубликована.")
    except Exception as e:
        print(f"❌ Ошибка при публикации в Telegram: {e}")

def scheduled_post():
    asyncio.run(post_news())

schedule.every().day.at("08:00").do(scheduled_post)
schedule.every().day.at("17:00").do(scheduled_post)

print("Тест: запускаем постинг вручную...")
try:
    asyncio.run(post_news())
except Exception as e:
    print("Ошибка при запуске:", e)
print("ок Если ты видишь это сообщение - код дошел до конца.")

while True:
    schedule.run_pending()
    time.sleep(1)
