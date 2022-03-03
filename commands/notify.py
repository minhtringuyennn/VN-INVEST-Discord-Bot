import os, discord, configparser, time, asyncio, threading, json
from datetime import datetime
from discord.ext import tasks
from discord.ext import commands

import stock_modules.fetch as fetch
import stock_modules.utils as utils

class NotifyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        read_config = configparser.ConfigParser()
        src_path = os.path.abspath(__file__+"/../../")
        config_path = os.path.join(src_path, "config", "config.ini")
        youtube_notify_path = os.path.join(src_path, "database\data", "youtube_notify.json")
        read_config.read(config_path)
        
        self.YOUTUBE_PATH = youtube_notify_path
        self.TIME_OUT = int(read_config.get("config", "YOUTUBE_TIME_OUT"))
        
    @commands.Cog.listener()
    async def on_ready(self):
        notifyThread = threading.Thread(target=self.call_get_youtube_livestream())
        notifyThread.setDaemon(True)
        notifyThread.start()
        
    def call_get_youtube_livestream(self):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.get_youtube_livestream(), loop)
                                
    async def get_youtube_livestream(self):
        while True:            
            json_data = None
            
            with open(str(self.YOUTUBE_PATH), "r") as f:
                json_data = json.load(f)
                    
            for youtube_channel_id in json_data:
                respond = fetch.fetchYoutubeVideoList(youtube_channel_id)
                
                if respond is None:
                    await asyncio.sleep(self.TIME_OUT)
                    continue
                
                latest_video_url = None
                latest_video_title = None
                for video in respond:
                    if json_data[youtube_channel_id]["live_only"] == "True":
                        if video["snippet"]["liveBroadcastContent"] == "live":
                            latest_video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                            latest_video_title = video["snippet"]["title"]
                            break
                    else:
                        latest_video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                        latest_video_title = video["snippet"]["title"]
                        break
                    
                print(latest_video_url)

                if not str(json_data[youtube_channel_id]["latest_video_url"]) == latest_video_url and latest_video_url is not None:
                    json_data[str(youtube_channel_id)]['latest_video_url'] = latest_video_url
                    with open(self.YOUTUBE_PATH, "w") as f:
                        json.dump(json_data, f)

                    discord_channel_id = json_data[youtube_channel_id]['notify_discord_channel']
                    tagged_id = json_data[youtube_channel_id]['tagged_id']
                    print(discord_channel_id)
                    discord_channel = self.bot.get_channel(int(discord_channel_id))
                    msg = f"{latest_video_title}\n{latest_video_url}\n<@!{tagged_id}>"
                    await discord_channel.send(msg)
            
            await asyncio.sleep(self.TIME_OUT)