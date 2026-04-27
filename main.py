import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from openai import AsyncOpenAI

# 从环境变量读取配置
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# 初始化 DeepSeek 客户端
客户端 = AsyncOpenAI（  
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="我是你的 AI 助手，直接发消息给我就可以聊天啦！"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.effective_message.text
    response = await client.chat.completions.create(
        model="deepseek-chat",
messages= [{"role" : "user" , "content" : user_text }]  
    )
    reply = response.choices[0].message.content
    await context.bot.send_message(

chat_id= update.effective_chat.id ，
        text=reply
    )

if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)

    application.add_handler(start_handler)
    application.add_handler(message_handler)

    application.run_polling()
