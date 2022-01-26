# Connect mongodb database and save data
import pymongo
import json
import stock_modules.stock as stock

class mongoDB():
    def __init__(self) -> None:
        self.__client = pymongo.MongoClient("mongodb://admin:Bachtam2001@127.0.0.1:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
        self.__db = self.__client['stocks']
        self.__price = self.__db.get_collection('realtime_price')

    def stockUpdate(self,stockNo,stockobj,overwrite=False):
        key = {'stockNo': stockNo}
        data = stockobj.__dict__
        if (overwrite):
            self.__price.update_one(key, {"$set" : data }, upsert=True)
        else:
            self.__price.update_one(key, {"$setOnInsert" : data}, upsert=True)

    def stockRead(self,stockNo):
        key = {'stockNo': stockNo}
        return self.__price.find_one(key)