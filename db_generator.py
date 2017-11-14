import random
import re

from pymongo import MongoClient


names = ("client_phone", "client_mail", "client_name",
         "worker_phone", "worker_mail", "worker_name",
         "purchase_information", "purchase_date",
         "company_open_date", "company_close_date",
         "company_phone", "company_name")


def generate_db(db_size=50, max_temp_size=12):
    """ Generate db with size db_size and random sized templates
        with max size max_temp_size """
    # Max temp size shouldn't be more then 12!!!

    client = MongoClient("mongodb://mongo:27017")
    db = client.test
    for i in range(db_size):
        temp_size = int(random.random() * max_temp_size) + 1
        template = {"name": "Form template " + str(i + 1)}
        choices = random.sample(names, temp_size)
        for choice in choices:
            key = choice
            value = None
            if re.match(".*_phone", key):
                value = 'phone'
            elif re.match(".*_mail", key):
                value = 'email'
            elif re.match(".*_date", key):
                value = 'date'
            elif re.match(".*_information", key) or re.match(".*_name", key):
                value = 'text'
            template[key] = value
        db.inventory.insert_one(template)
    client.close()
