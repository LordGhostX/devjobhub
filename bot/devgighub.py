import json
from telegram.ext import Updater
from telegram.ext import CommandHandler

config = json.load(open("config.json"))
updater = Updater(
    token=config["token"], use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=config["start_message"])
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=config["menu_message"])


start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

updater.start_polling()
