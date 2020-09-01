import json
import pymongo

config = json.load(open("config.json"))
client = pymongo.MongoClient(config["db"]["host"], config["db"]["port"])
db = client[config["db"]["db_name"]]

db.job_stack.delete_many({})

all_stack = [i["_id"]
             for i in db.user_stack.aggregate([{"$group": {"_id": "$stack"}}])]
for i in db.jobs.find({}):
    if i["info"].get("description") != None:
        description = i["info"]["description"]
    else:
        description = i["details"]["description"]
    if i["info"].get("tags") != None:
        tags = i["info"]["tags"]
    else:
        if i.get("details") != None:
            if i["details"].get("tags") != None:
                tags = i["details"]["tags"]
            else:
                tags = []
        else:
            tags = []
    job_url = i["href"]
    valid_stack = [i for i in all_stack if i in description.lower()
                   or i in tags]
    job_stack = [{"job_url": job_url, "stack": i}
                 for i in valid_stack if i != "all"]
    if job_stack != []:
        db.job_stack.insert_many(job_stack)
