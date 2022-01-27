# Connect mongodb database and save data
import pymongo
import json
import stock_modules.stock as stock

class mongoDB():
    def __init__(self) -> None:
        self.__client = pymongo.MongoClient("mongodb://admin:Bachtam2001@127.0.0.1:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
        self.__db = self.__client['stocks']
        self.__rtprice = self.__db.get_collection('realtime_price')
        self.__hprice = self.__db.get_collection('history_price')

    def stockRealtimeUpdate(self, stockobj, overwrite=False, stockNo = None, code = None):
        if (stockNo != None and code != None):
            key = {'stockNo': stockNo,'code':code}
        elif (stockNo != None):
            key = {'stockNo': stockNo}
        elif (code != None):
            key = {'code':code}
        else:
            return
        data = stockobj.__dict__
        if (overwrite):
            self.__rtprice.update_one(key, {"$set" : data }, upsert=True)
        else:
            self.__rtprice.update_one(key, {"$setOnInsert" : data}, upsert=True)

    def stockUpdate(self, stockobj, overwrite=False, stockNo = None, code = None):
        if (stockNo != None and code != None):
            key = {'stockNo': stockNo,'code':code}
        elif (stockNo != None):
            key = {'stockNo': stockNo}
        elif (code != None):
            key = {'code':code}
        else:
            return
        data = stockobj.__dict__
        if (overwrite):
            self.__hprice.update_one(key, {"$set" : data }, upsert=True)
        else:
            self.__hprice.update_one(key, {"$setOnInsert" : data}, upsert=True)

    def stockRealtimeRead(self,stockNo = None, code = None):
        if (stockNo != None and code != None):
            key = {'stockNo': stockNo,'code':code}
        elif (stockNo != None):
            key = {'stockNo': stockNo}
        elif (code != None):
            key = {'code':code}
        else:
            return None
        return self.__rtprice.find_one(key)    

    def stockRead(self,stockNo = None, code = None):
        if (stockNo != None and code != None):
            key = {'stockNo': stockNo,'code':code}
        elif (stockNo != None):
            key = {'stockNo': stockNo}
        elif (code != None):
            key = {'code':code}
        else:
            return None
        return self.__hprice.find_one(key)