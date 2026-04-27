import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from openai import AsyncOpenAI

# 读取环境变量
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# AI 客户端
client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# 启动命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="我是你的AI助手，直接发消息给我吧！"
    )

# 聊天消息处理
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.effective_message.text
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": user_msg}]
    )
    reply = response.choices[0].message.content
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

# 启动机器人
if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling()
