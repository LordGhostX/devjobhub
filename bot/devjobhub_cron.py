import json
import time
import datetime
from multiprocessing import Pool
import pymongo
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import scraper

config = json.load(open("config.json"))
client = pymongo.MongoClient(config["db"]["host"], config["db"]["port"])
db = client[config["db"]["db_name"]]
bot = telegram.Bot(token=config["token"])


def send_job_listing(args):
    try:
        bot.send_message(args[0], args[1], parse_mode="HTML",
                         disable_web_page_preview="True", reply_markup=InlineKeyboardMarkup(args[2]))
    except Exception as e:
        if str(e) == "Forbidden: bot was blocked by the user":
            db.users.update_one({"chat_id": args[0]}, {
                                "$set": {"active": False}})


def send_job_to_users(description, tags, job_message, job_url):
    all_stack = [i["_id"]
                 for i in db.user_stack.aggregate([{"$group": {"_id": "$stack"}}])]
    valid_stack = list(set([i for i in all_stack if i in description.lower()
                            or i in tags] + ["all"]))
    db.jobs.update_one({"href": job_url}, {
                       "$set": {"stacks": valid_stack}})
    users = set([i["chat_id"]
                 for i in db.user_stack.find({"stack": {"$in": valid_stack}})])
    valid_users = db.users.find(
        {"active": True, "chat_id": {"$in": list(users)}})
    markup = [[InlineKeyboardButton("Apply", url=job_url)]]
    with Pool(5) as p:
        p.map(send_job_listing, [
              [i["chat_id"], job_message, markup] for i in valid_users])


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
                          ["tags"], job_message, job["info"]["href"])


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
                          ["tags"], job_message, job["info"]["href"])


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
                          ["tags"], job_message, job["info"]["href"])


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
                          ["tags"], job_message, job["info"]["href"])


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
                          ["tags"], job_message, job["info"]["href"])


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
                          job_message, job["info"]["href"])


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
                          [], job_message, job["info"]["href"])


def pythonorg():
    jobs = []
    for job in scraper.pythonorg_jobs():
        if not db.jobs.find_one({"href": job["href"]}):
            try:
                jobs.append({
                    "info": job,
                    "details": scraper.pythonorg_info(job["href"])
                })
            except:
                pass
    for job in jobs:
        db.jobs.insert_one(
            {**job, "href": job["info"]["href"], "date": datetime.datetime.now()})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["details"]["location"], "Not Specified", ", ".join(job["info"]["tags"]), "📅 <b>Date Posted:</b> {}\n".format(job["info"]["date_posted"]), job["info"]["href"])
        send_job_to_users(job["details"]["description"],
                          job["info"]["tags"], job_message, job["info"]["href"])


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
        print("Scraping pythonorg...")
        pythonorg()
        print("Taking a nap... Scraping took {} seconds".format(
            int(time.time() - start)))
        time.sleep(config["scrape_interval"] * 60)
