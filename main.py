import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes  
from openai import AsyncOpenAI

# 读取密钥
TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEP_KEY = os.getenv("DEEPSEEK_API_KEY")

client = AsyncOpenAI(api_key=DEEP_KEY, base_url="https://api.deepseek.com")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("我准备好了！发消息给我吧！")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    resp = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":msg}]
    )
    await update.message.reply_text(resp.choices[0].message.content)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()
