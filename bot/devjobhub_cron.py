import json
import time
import datetime
import pymongo
import telegram
import scraper
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

config = json.load(open("config.json"))
client = pymongo.MongoClient(config["db"]["host"], config["db"]["port"])
db = client[config["db"]["db_name"]]
bot = telegram.Bot(token=config["token"])


def send_job_to_users(description, tags, job_message, job_url, job_role, markup=None):
    all_stack = [i["_id"]
                 for i in db.user_stack.aggregate([{"$group": {"_id": "$stack"}}])]
    valid_stack = [i for i in all_stack if i in description.lower()
                   or i in tags]
    job_stack = [{"job_url": job_url, "job_role": job_role, "stack": i, "date": datetime.datetime.now()}
                 for i in valid_stack if i != "all"]
    if job_stack != []:
        db.job_stack.insert_many(job_stack)
    users = set([i["chat_id"]
                 for i in db.user_stack.find({"stack": {"$in": valid_stack + ["all"]}})])
    valid_users = db.users.find(
        {"active": True, "chat_id": {"$in": list(users)}})
    for user in valid_users:
        try:
            markup = [[InlineKeyboardButton("Apply", url=job_url)]]
            bot.send_message(
                user["chat_id"], job_message, parse_mode="HTML", disable_web_page_preview="True", reply_markup=InlineKeyboardMarkup(markup))
        except Exception as e:
            if str(e) == "Forbidden: bot was blocked by the user":
                db.users.update_one({"chat_id": user["chat_id"]}, {
                                    "$set": {"active": False}})


def weworkremotely():
    jobs = []
    for job in scraper.weworkremotely_jobs():
        if not db.jobs.find_one({"href": job["href"]}):
            try:
                jobs.append({
                    "info": job,
                    "details": scraper.weworkremotely_info(job["href"])
                })
            except:
                pass
    for job in jobs:
        db.jobs.insert_one(
            {**job, "href": job["info"]["href"], "date": datetime.datetime.now()})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["info"]["location"], job["info"]["job_type"], ", ".join(job["details"]["tags"]), "", job["info"]["href"])
        send_job_to_users(job["details"]["description"], job["details"]
                          ["tags"], job_message, job["info"]["href"], job["info"]["role"])


def remoteok():
    jobs = []
    for job in scraper.remoteok_jobs():
        if not db.jobs.find_one({"href": job["href"]}):
            try:
                jobs.append({
                    "info": job,
                })
            except:
                pass
    for job in jobs:
        db.jobs.insert_one(
            {**job, "href": job["info"]["href"], "date": datetime.datetime.now()})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["info"]["location"], job["info"]["job_type"], ", ".join(job["info"]["tags"]), "", job["info"]["href"])
        send_job_to_users(job["info"]["description"], job["info"]
                          ["tags"], job_message, job["info"]["href"], job["info"]["role"])


def employremotely():
    jobs = []
    for job in scraper.employremotely_jobs():
        if not db.jobs.find_one({"href": job["href"]}):
            try:
                jobs.append({
                    "info": job,
                    "details": scraper.employremotely_info(job["href"])
                })
            except:
                pass
    for job in jobs:
        db.jobs.insert_one(
            {**job, "href": job["info"]["href"], "date": datetime.datetime.now()})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["info"]["location"], job["info"]["job_type"], ", ".join(job["details"]["tags"]), "⏰ <b>Deadline:</b> {}\n".format(job["details"]["deadline"]), job["info"]["href"])
        send_job_to_users(job["details"]["description"], job["details"]
                          ["tags"], job_message, job["info"]["href"], job["info"]["role"])


def remotive():
    jobs = []
    for job in scraper.remotive_jobs():
        if not db.jobs.find_one({"href": job["href"]}):
            try:
                jobs.append({
                    "info": job,
                    "details": scraper.remotive_info(job["href"])
                })
            except:
                pass
    for job in jobs:
        db.jobs.insert_one(
            {**job, "href": job["info"]["href"], "date": datetime.datetime.now()})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["info"]["location"], "Not Specified", ", ".join(job["details"]["tags"]), "", job["info"]["href"])
        send_job_to_users(job["details"]["description"], job["details"]
                          ["tags"], job_message, job["info"]["href"], job["info"]["role"])


def stackoverflow():
    jobs = []
    for job in scraper.stackoverflow_jobs():
        if not db.jobs.find_one({"href": job["href"]}):
            try:
                jobs.append({
                    "info": job,
                    "details": scraper.stackoverflow_info(job["href"])
                })
            except:
                pass
    for job in jobs:
        db.jobs.insert_one(
            {**job, "href": job["info"]["href"], "date": datetime.datetime.now()})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["info"]["location"], "Not Specified", ", ".join(job["details"]["tags"]), "", job["info"]["href"])
        send_job_to_users(job["details"]["description"], job["details"]
                          ["tags"], job_message, job["info"]["href"], job["info"]["role"])


def github():
    jobs = []
    for job in scraper.github_jobs():
        if not db.jobs.find_one({"href": job["href"]}):
            try:
                jobs.append({
                    "info": job,
                })
            except:
                pass
    for job in jobs:
        db.jobs.insert_one(
            {**job, "href": job["info"]["href"], "date": datetime.datetime.now()})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["info"]["location"], job["info"]["job_type"], "None", "", job["info"]["href"])
        send_job_to_users(job["info"]["description"], [],
                          job_message, job["info"]["href"], job["info"]["role"])


def remoteco():
    jobs = []
    for job in scraper.remoteco_jobs():
        if not db.jobs.find_one({"href": job["href"]}):
            try:
                jobs.append({
                    "info": job,
                    "details": scraper.remoteco_info(job["href"])
                })
            except:
                pass
    for job in jobs:
        db.jobs.insert_one(
            {**job, "href": job["info"]["href"], "date": datetime.datetime.now()})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["details"]["location"], "Not Specified", "None", "", job["info"]["href"])
        send_job_to_users(job["details"]["description"],
                          [], job_message, job["info"]["href"], job["info"]["role"])


if __name__ == "__main__":
    while True:
        start = time.time()
        print("Scraping weworkremotely...")
        weworkremotely()
        print("Scraping remoteok...")
        remoteok()
        print("Scraping employremotely...")
        employremotely()
        print("Scraping remotive...")
        remotive()
        print("Scraping stackoverflow jobs...")
        stackoverflow()
        print("Scraping github jobs...")
        github()
        print("Scraping remoteco...")
        remoteco()
        print("Taking a nap... Scraping took {} seconds".format(
            int(time.time() - start)))
        time.sleep(config["scrape_interval"] * 60)
