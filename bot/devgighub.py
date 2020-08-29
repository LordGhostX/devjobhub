import datetime
import json
import pymongo
from telegram.ext import Updater
from telegram.ext import CommandHandler

config = json.load(open("config.json"))
updater = Updater(
    token=config["token"], use_context=True)
dispatcher = updater.dispatcher
client = pymongo.MongoClient("localhost", 27017)
db = client.devjobhub


def start(update, context):
    chat_id = update.effective_chat.id
    if not db.users.find_one({"chat_id": chat_id}):
        db.users.insert_one(
            {"chat_id": chat_id, "date": datetime.datetime.now()})
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["start"])
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["menu"])


def view_stack(update, context):
    chat_id = update.effective_chat.id
    stack = list(db.user_stack.find({"chat_id": chat_id}))
    if stack == []:
        context.bot.send_message(
            chat_id=chat_id, text=config["messages"]["empty_stack"])
    else:
        stack_message = config["messages"]["stack"].format(", ".join(stack))
        context.bot.send_message(
            chat_id=chat_id, text=stack_message)


start_handler = CommandHandler("start", start)
view_stack_handler = CommandHandler("view_stack", view_stack)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(view_stack_handler)

updater.start_polling()
