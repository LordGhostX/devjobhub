import datetime
import time
import json
import pymongo
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

config = json.load(open("config.json"))
updater = Updater(
    token=config["token"], use_context=True)
dispatcher = updater.dispatcher
client = pymongo.MongoClient(config["db"]["host"], config["db"]["port"])
db = client[config["db"]["db_name"]]


def parse_stack(stack):
    stack = stack.strip().lower()
    accepted_chars = string.ascii_lowercase + string.digits + "-/+#. "
    return "".join([i for i in stack if i in accepted_chars])


def start(update, context):
    chat_id = update.effective_chat.id
    if not db.users.find_one({"chat_id": chat_id}):
        db.users.insert_one(
            {"chat_id": chat_id, "last_command": None, "active": True, "date": datetime.datetime.now()})
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["start"].format(update["message"]["chat"]["first_name"]))
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["menu"])
    db.users.update_one({"chat_id": chat_id}, {"$set": {"last_command": None}})
    time.sleep(0.035)


def menu(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["menu"])
    db.users.update_one({"chat_id": chat_id}, {"$set": {"last_command": None}})
    time.sleep(0.035)


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
    db.users.update_one({"chat_id": chat_id}, {"$set": {"last_command": None}})
    time.sleep(0.035)


def add_stack(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["add_stack"])
    last_command = "add_stack"
    db.users.update_one({"chat_id": chat_id}, {
                        "$set": {"last_command": last_command}})
    time.sleep(0.035)


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
    time.sleep(0.035)


def stats(update, context):
    chat_id = update.effective_chat.id
    total_users = db.users.count_documents({})
    total_jobs = db.jobs.count_documents({})
    total_stack = db.user_stack.count_documents({})
    stack_stats = ""
    for i in list(db.user_stack.aggregate([{"$group": {"_id": "$stack", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}])):
        stack_stats += "{} - {:.2f}%\n".format(i["_id"],
                                               i["count"] / total_stack * 100)
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["stats"].format(total_jobs, total_users, stack_stats, time.strftime("%d/%m/%Y %H:%M:%S UTC")))
    db.users.update_one({"chat_id": chat_id}, {"$set": {"last_command": None}})
    time.sleep(0.035)


def donate(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["donate"])
    db.users.update_one({"chat_id": chat_id}, {"$set": {"last_command": None}})
    time.sleep(0.035)


def echo(update, context):
    chat_id = update.effective_chat.id
    bot_user = db.users.find_one({"chat_id": chat_id})
    last_command = bot_user["last_command"] if bot_user != None else None
    if last_command == "add_stack":
        stack = [parse_stack(i)
                 for i in update.message.text.split(",") if i.strip() != ""]
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
    time.sleep(0.035)


start_handler = CommandHandler("start", start)
menu_handler = CommandHandler("menu", menu)
stats_handler = CommandHandler("stats", stats)
donate_handler = CommandHandler("donate", donate)
view_stack_handler = CommandHandler("view_stack", view_stack)
add_stack_handler = CommandHandler("add_stack", add_stack)
remove_stack_handler = CommandHandler("remove_stack", remove_stack)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(menu_handler)
dispatcher.add_handler(donate_handler)
dispatcher.add_handler(stats_handler)
dispatcher.add_handler(view_stack_handler)
dispatcher.add_handler(add_stack_handler)
dispatcher.add_handler(remove_stack_handler)
dispatcher.add_handler(echo_handler)

updater.start_polling()
