import datetime
import json
import pymongo
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

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


def menu(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["menu"])


def view_stack(update, context):
    chat_id = update.effective_chat.id
    stack = list(db.user_stack.find({"chat_id": chat_id}))
    if stack == []:
        context.bot.send_message(
            chat_id=chat_id, text=config["messages"]["empty_stack"])
    else:
        stack = [i["stack"] for i in stack]
        stack_message = config["messages"]["stack"].format(
            ", ".join(stack))
        context.bot.send_message(
            chat_id=chat_id, text=stack_message)
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["menu"])


def add_stack(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["add_stack"])
    last_command = "add_stack"
    db.users.update_one({"chat_id": chat_id}, {
                        "$set": {"last_command": last_command}})
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["menu"])


def remove_stack(update, context):
    chat_id = update.effective_chat.id
    stack = list(db.user_stack.find({"chat_id": chat_id}))
    if stack == []:
        context.bot.send_message(
            chat_id=chat_id, text=config["messages"]["empty_stack"])
    else:
        stack = [i["stack"] for i in stack]
        stack_message = config["messages"]["remove_stack"].format(
            ", ".join(stack))
        context.bot.send_message(
            chat_id=chat_id, text=stack_message)
        last_command = "remove_stack"
        db.users.update_one({"chat_id": chat_id}, {
                            "$set": {"last_command": last_command}})
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["menu"])


def echo(update, context):
    chat_id = update.effective_chat.id
    last_command = db.users.find_one({"chat_id": chat_id}).get("last_command")
    if last_command == "add_stack":
        stack = [i.strip().lower() for i in update.message.text.split(",")]
        for i in stack:
            db.user_stack.delete_many({"chat_id": chat_id, "stack": i})
        db.user_stack.insert_many(
            [{"chat_id": chat_id, "stack": i} for i in stack])
        context.bot.send_message(
            chat_id=chat_id, text=config["messages"]["updated_stack"])
    elif last_command == "remove_stack":
        stack = [i.strip().lower() for i in update.message.text.split(",")]
        for i in stack:
            db.user_stack.delete_many({"chat_id": chat_id, "stack": i})
        context.bot.send_message(
            chat_id=chat_id, text=config["messages"]["updated_stack"])
    else:
        context.bot.send_message(
            chat_id=chat_id, text=config["messages"]["unknown"])
    db.users.update_one({"chat_id": chat_id}, {"$set": {"last_command": None}})


start_handler = CommandHandler("start", start)
menu_handler = CommandHandler("menu", menu)
view_stack_handler = CommandHandler("view_stack", view_stack)
add_stack_handler = CommandHandler("add_stack", add_stack)
remove_stack_handler = CommandHandler("remove_stack", remove_stack)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(menu_handler)
dispatcher.add_handler(view_stack_handler)
dispatcher.add_handler(add_stack_handler)
dispatcher.add_handler(remove_stack_handler)
dispatcher.add_handler(echo_handler)

updater.start_polling()
