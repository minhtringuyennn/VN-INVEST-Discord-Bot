import os, discord, configparser, time, asyncio, threading, json, xmltodict
from datetime import datetime
from discord.ext import tasks
from discord.ext import commands
from discord.enums import ChannelType

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
        asyncio.run_coroutine_threadsafe(self.get_youtube_feed(), loop)
        
    async def get_youtube_feed(self, max_results = 5):
        while True:   
            json_data = None
            
            print("fetching youtube feed...")
            
            with open(str(self.YOUTUBE_PATH), "r") as f:
                json_data = json.load(f)
            
            for youtube_channel_id in json_data:
                latest_url = None
                latest_title = None
                
                video_list = fetch.fetchYoutubePlaylist(youtube_channel_id, max_results=max_results)
                pairs = video_list.items()
                
                pairs_iterator = iter(pairs)
                latest_pair = next(pairs_iterator)
                
                latest_title, latest_url = latest_pair
                
                header_msg = "🎬 NEW VIDEO UPLOADS"
                
                if json_data[youtube_channel_id]["live_only"] == "True":
                    header_msg = "🔴 STREAMING NOW"
                    link = fetch.fetchYoutubeLivestream(youtube_channel_id)
                    if link:
                        print(link)
                        for i in range(0, max_results - 1):
                            if link != latest_url:
                                latest_pair = next(pairs_iterator)
                                latest_title, latest_url = latest_pair
                            else:
                                break
                            
                if latest_url and latest_url != str(json_data[youtube_channel_id]["latest_url"]) and latest_url not in json_data[youtube_channel_id]["posted_video_url"]:
                    json_data[str(youtube_channel_id)]['latest_url'] = latest_url
                    json_data[str(youtube_channel_id)]['posted_video_url'].append(latest_url)
                    if len(json_data[str(youtube_channel_id)]['posted_video_url']) >= max_results:
                        json_data[str(youtube_channel_id)]['posted_video_url'].pop(0)
                        
                    with open(self.YOUTUBE_PATH, "w") as f:
                        json.dump(json_data, f)
                    
                    for discord_channel_id in json_data[youtube_channel_id]['notify_discord_channel']:
                        tagged_msg = ""
                        for tagged_id in json_data[youtube_channel_id]['tagged_id']:
                            tagged_msg += f'<@{tagged_id}> '
                        discord_channel = self.bot.get_channel(int(discord_channel_id))
                        msg = f"{header_msg} {tagged_msg}\n{latest_title.upper()}\n\n{latest_url}"
                        
                        print(msg)
                        await discord_channel.send(msg)
                        try:
                            print("sending message...")
                            await discord_channel.create_thread(name=latest_title, type=ChannelType.public_thread, auto_archive_duration=1440)
                        except Exception as e: 
                            print("cant create thread")
                            print(e)
            await asyncio.sleep(self.TIME_OUT)