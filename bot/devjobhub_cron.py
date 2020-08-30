import json
import time
import datetime
import pymongo
import telegram
import scraper

config = json.load(open("config.json"))
client = pymongo.MongoClient(config["db"]["host"], config["db"]["port"])
db = client[config["db"]["db_name"]]
bot = telegram.Bot(token=config["token"])
testing = False


def send_job_to_users(description, tags, job_message):
    if testing:
        return
    all_stack = [i["_id"]
                 for i in db.user_stack.aggregate([{"$group": {"_id": "$stack"}}])]
    valid_stack = [i for i in all_stack if i in description.lower()
                   or i in tags]
    users = set([i["chat_id"]
                 for i in db.user_stack.find({"stack": {"$in": valid_stack + ["all"]}})])
    for user in users:
        try:
            bot.send_message(user, job_message)
        except:
            pass
        time.sleep(0.035)


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
        send_job_to_users(job["details"]["description"],
                          job["details"]["tags"], job_message)


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
        send_job_to_users(job["info"]["description"],
                          job["info"]["tags"], job_message)


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
            job["info"]["role"], job["info"]["company"], job["info"]["location"], job["info"]["job_type"], ", ".join(job["details"]["tags"]), "⏰ Deadline: {}\n".format(job["details"]["deadline"]), job["info"]["href"])
        send_job_to_users(job["details"]["description"],
                          job["details"]["tags"], job_message)


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
        send_job_to_users(job["details"]["description"],
                          job["details"]["tags"], job_message)


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
        send_job_to_users(job["details"]["description"],
                          job["details"]["tags"], job_message)


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
        send_job_to_users(job["info"]["description"], [], job_message)


if __name__ == "__main__":
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
