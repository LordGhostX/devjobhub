import json
import time
import pymongo
import telegram
import scraper

config = json.load(open("config.json"))
client = pymongo.MongoClient(config["db"]["host"], config["db"]["port"])
db = client[config["db"]["db_name"]]
bot = telegram.Bot(token=config["token"])


def send_job_to_users(description, tags, job_message):
    all_stack = [i["_id"]
                 for i in db.user_stack.aggregate([{"$group": {"_id": "$stack"}}])]
    valid_stack = [i for i in all_stack if i in description.lower()
                   or i in tags]
    users = db.user_stack.find({"stack": {"$in": valid_stack}})
    for user in users:
        try:
            bot.send_message(user["chat_id"], job_message)
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
        db.jobs.insert_one({**job, "href": job["info"]["href"]})
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
        break
    for job in jobs:
        # db.jobs.insert_one({**job, "href": job["info"]["href"]})
        job_message = config["messages"]["job_message"].format(
            job["info"]["role"], job["info"]["company"], job["info"]["location"], job["info"]["job_type"], ", ".join(job["info"]["tags"]), "", job["info"]["href"])
        send_job_to_users(job["info"]["description"],
                          job["info"]["tags"], job_message)


if __name__ == "__main__":
    # weworkremotely()
    remoteok()
