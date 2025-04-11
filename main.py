import os
import requests
from flask import Flask, request
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
MP_TOKEN = os.getenv("MP_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

app_bot = Application.builder().token(TOKEN).build()
app_web = Flask(__name__)

# /start
async def start(update, context):
    await update.message.reply_text("🚀 Olá! Estou funcionando com Webhook na Render!")

# /pagamento <valor> <titulo>
async def pagamento(update, context):
    try:
        valor = float(context.args[0])
        titulo = " ".join(context.args[1:]) or "Pagamento Personalizado"
    except:
        await update.message.reply_text("❌ Use: /pagamento 19.90 Nome do Produto")
        return

    body = {
        "items": [{
            "title": titulo,
            "quantity": 1,
            "unit_price": valor,
            "currency_id": "BRL"
        }],
        "back_urls": {
            "success": "https://t.me/" + context.bot.username,
            "failure": "https://t.me/" + context.bot.username
        },
        "auto_return": "approved"
    }

    headers = {
        "Authorization": f"Bearer {MP_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.mercadopago.com/checkout/preferences", json=body, headers=headers)
    link = response.json()["init_point"]
    await update.message.reply_text(f"💰 Clique para pagar: {link}")

@app_web.route("/")
def home():
    return "✅ Bot ativo na Render!"

@app_web.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    app_bot.update_queue.put(update)
    return "ok"

async def configurar_webhook():
    await app_bot.bot.set_webhook(f"https://bot-vendas-telegram-2.onrender.com/{TOKEN}")
    print("✅ Webhook configurado com sucesso!")

if __name__ == "__main__":
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("pagamento", pagamento))
    import asyncio
    asyncio.run(configurar_webhook())
    app_web.run(host="0.0.0.0", port=PORT)
