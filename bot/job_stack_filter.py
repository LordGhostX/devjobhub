import json
import pymongo

config = json.load(open("config.json"))
client = pymongo.MongoClient(config["db"]["host"], config["db"]["port"])
db = client[config["db"]["db_name"]]

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
    valid_stack = list(
        set([i for i in all_stack if i in description.lower() or i in tags] + ["all"]))
    db.jobs.update_one({"href": i["href"]}, {"$set": {"stacks": valid_stack}})
