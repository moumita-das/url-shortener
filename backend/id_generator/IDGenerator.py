import random

from pymongo.errors import BulkWriteError, DuplicateKeyError

from db.client import db_client
from settings import settings


start_counter_table = db_client[settings.mongodb_name]["id_window_start_counter"] 
used_ids_table = db_client[settings.mongodb_name]["used_ids"]
unused_ids_table = db_client[settings.mongodb_name]["unused_ids"]

BASE58_MAP = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

class IDGenerator:
    def __init__(self):
        pass

    def _int_to_base58(self, num):
        remainders = []
        while num > 0:
            num, remainder = divmod(num, 58)
            remainders.append(remainder)
        remainders = remainders[::-1]
        base58_str = "".join([BASE58_MAP[x] for x in remainders])
        return base58_str

    def _base58_to_int(self, base58_str):
        if base58_str.strip() == "":
            raise ValueError("Cannot be empty string")
        if len(base58_str) >=11:
            raise ValueError("Too long alias")
        if base58_str.startswith("1"):
            raise ValueError("Cannot start with 1")
        num = 0
        try:
            for char in base58_str:
                num = num * 58 + BASE58_MAP.index(char)
            return num
        except ValueError:
            raise ValueError("Invalid URL: please exclude characters like 0, O, I, l, etc.")

    def generate_new_ids(self):
        # Implement the logic to generate new unique IDs
        last_counter = start_counter_table.find_one(sort=[("_id", -1)])
        if last_counter is None:
            new_counter = 10**9 
        else:
            new_counter = last_counter["counter"] + settings.counter_window_length

        start_counter_table.insert_one({"counter": new_counter})
        potential_ids = [i for i in range(new_counter, new_counter + settings.counter_window_length)]
        try:
            unused_ids_table.insert_many([{"_id": i} for i in potential_ids], ordered=False)
        except BulkWriteError as bwe:
            errors = bwe.details.get('writeErrors', [])
            dupes = [err for err in errors if err.get('code') == 11000]
            if len(dupes) != len(errors):
                raise bwe
            print(f"Duplicate IDs found and skipped: {len(dupes)}")

    def fetch_unused_url(self):
        id_selected = None
        while id_selected is None:
            unused_ids = list(unused_ids_table.aggregate([
                {"$sample": {"size": 20}}
            ]))
            if len(unused_ids) < 20:
                self.generate_new_ids()
            if unused_ids:
                random_id = random.choice(unused_ids)
                id_selected = unused_ids_table.find_one_and_delete({"_id": random_id["_id"]})
                if id_selected:
                    id_selected = id_selected["_id"]
                    try:
                        used_ids_table.insert_one({"_id": id_selected})
                    except DuplicateKeyError:
                        id_selected = None
        

        base58_url = self._int_to_base58(id_selected)
        print(f"Generated new ID: {base58_url} from counter: {id_selected}")
        return base58_url

    def generate_id_for_custom_url(self, custom_url):
        try:
            id_int = self._base58_to_int(custom_url)
        except ValueError as e:
            print(f"Error: {e}")
            return None

        if used_ids_table.find_one({"_id": id_int}):
            print(f"Custom URL '{custom_url}' is already in use.")
            return None
        try:
            used_ids_table.insert_one({"_id": id_int})
        except DuplicateKeyError:
            return self.generate_id_for_custom_url(custom_url)
        unused_ids_table.delete_one({"_id": id_int})
        print(f"Custom URL '{custom_url}' has been successfully registered.")
        return custom_url

generator = IDGenerator()
