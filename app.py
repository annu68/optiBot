import os
from flask import Flask, request
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_msg = data["message"]["text"]

        try:
            # Claude via OpenRouter API
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "anthropic/claude-3-sonnet",
                "messages": [
                    {"role": "system", "content": "You are a helpful optical networking assistant."},
                    {"role": "user", "content": user_msg}
                ]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            reply = response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            reply = f"Error: {str(e)}"

        send_telegram_message(chat_id, reply)

    return "ok"


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


if __name__ == "__main__":
    app.run(debug=True)
