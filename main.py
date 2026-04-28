import os
import logging
import base64
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from collections import defaultdict

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = "你是一个幽默的内容创作助手，名字叫Jennie。你说话接地气，擅长梗黄科写短视频脚本和文案。请用中文回复。"

MAX_ROUNDS = 50
chat_history = defaultdict(list)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_history[user_id] = []
    await update.message.reply_text("我是Jennie！有什么短视频脚本或文案需要搞，尽管说！")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text or ""

    chat_history[user_id].append({"role": "user", "content": user_message})

    if len(chat_history[user_id]) > MAX_ROUNDS * 2:
        chat_history[user_id] = chat_history[user_id][-MAX_ROUNDS * 2:]

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history[user_id]
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=messages,
            max_tokens=1000
        )
        reply = response.choices[0].message.content
        chat_history[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("出错了，稍等一下再试试！")
        logging.error(f"Error: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    caption = update.message.caption or "请描述这张图片"

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    async with httpx.AsyncClient() as hclient:
        resp = await hclient.get(file.file_path)
        image_data = base64.b64encode(resp.content).decode("utf-8")

    user_content = [
        {"type": "text", "text": caption},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
    ]

    chat_history[user_id].append({"role": "user", "content": user_content})

    if len(chat_history[user_id]) > MAX_ROUNDS * 2:
        chat_history[user_id] = chat_history[user_id][-MAX_ROUNDS * 2:]

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history[user_id]
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=messages,
            max_tokens=1000
        )
        reply = response.choices[0].message.content
        chat_history[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("出错了，稍等一下再试试！")
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Jennie启动了！")
    app.run_polling()



