# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import sqlite3


class KakakuPipeline:
    _db = None

    @classmethod
    def get_database(cls):
        cls._db = sqlite3.connect(os.path.join(os.getcwd(), "./out/places_test.db"))

        cursor = cls._db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS places(\
                id INTEGER PRIMARY KEY AUTOINCREMENT, \
                name TEXT UNIQUE NOT NULL, \
                info TEXT NOT NULL, \
                address TEXT NOT NULL, \
                lat TEXT, \
                lng TEXT, \
                link TEXT NOT NULL \
            );"
        )
        return cls._db

    def process_item(self, item, spider):
        self.save_post(item)
        return item

    def save_post(self, item):
        if self.find_post(item["name"]):
            return

        db = self.get_database()
        db.execute(
            "INSERT INTO places (name, info, address, lat, lng, link) VALUES (?, ?, ?, ?, ?, ?)",
            (
                item["name"],
                item["info"],
                item["address"],
                "",
                "",
                item["link"],
            ),
        )
        db.commit()

    def find_post(self, name):
        db = self.get_database()
        cursor = db.execute("SELECT * FROM places WHERE name=?", (name,))
        return cursor.fetchone()
