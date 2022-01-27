#!/usr/bin/python3

import configparser
import os, asyncio, pathlib, string

import discord
from discord.ext import commands

import commands.default as default
import commands.price as price
import stock_modules.websocket as wsprice
import stock_modules.database as db
import threading

class MyBot(commands.Bot):
    def read_config(self):
        read_config = configparser.ConfigParser()
        path = os.path.join(os.path.dirname(__file__), "config", "config.ini")
        read_config.read(path)
        self.__TOKEN = read_config.get("config", "TOKEN")
        self.__PREFIX = read_config.get("config", "COMMAND_PREFIX")
        
    def __init__(self):
        self.read_config()
        intents = discord.Intents().all()
        super().__init__(command_prefix=self.__PREFIX, intents=intents)
        super().remove_command('help')
    
    def run(self):
        super().run(self.__TOKEN, reconnect=True)

if __name__ == "__main__":
    Db = db.mongoDB()
    wsPrice = wsprice.websocketPrice(Db)
    wsThread = threading.Thread(target=wsPrice.run)
    wsThread.setDaemon(True)
    wsThread.start()
    BOT = MyBot()
    BOT.add_cog(default.DefaultCommands(BOT))
    BOT.add_cog(price.Price(BOT))
    BOT.run()