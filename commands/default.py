import os, discord, configparser, time, asyncio, threading
from datetime import datetime
from discord.ext import tasks
from discord.ext import commands

import stock_modules.fetch as fetch

class DefaultCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        read_config = configparser.ConfigParser()
        path = os.path.join(os.path.abspath(__file__+"/../../"),"config", "config.ini")
        read_config.read(path)
        self.LogID = read_config.get("config", "LOG_CHANNEL")
        self.TIME_OUT = int(read_config.get("config", "TIME_OUT"))
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        channel = self.bot.get_channel(int(self.LogID))
        await channel.send(f'{ctx.message.author} run `{ctx.message.content}` in channel `{ctx.message.channel}` in server `{ctx.message.guild}`')
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Stock Bot is now ready!')
        print('Logged in as ---->', self.bot.user)
        print('ID:', self.bot.user.id)
        activityThread = threading.Thread(target=self.call_set_activity())
        activityThread.setDaemon(True)
        activityThread.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Lệnh không hợp lệ")
            return
        channel = self.bot.get_channel(int(self.LogID))
        await channel.send(f'command `{ctx.message.content}` at channel `{ctx.message.channel}` in server `{ctx.message.guild}` error: `{error}')

    @commands.command(pass_context=True)
    async def help(self, ctx): 
        embed = discord.Embed(
            color=discord.Color.red()
        )
        embed.set_author(name='Thông tin nhanh:')
        embed.add_field(name='Về bot',
                        value='Thuộc team dev SH Investing. Sử dụng slash command để thực hiện các lệnh của bot.\n\n',
                        inline=True)
        
        await ctx.send(embed=embed)
    
    def call_set_activity(self):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.set_activity(), loop)
                                
    async def set_activity(self):
        while True:
            get_vnindex = fetch.fetchVNINDEX()
            print(get_vnindex)
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"VNINDEX at {get_vnindex}"
                    )
                )
            await asyncio.sleep(self.TIME_OUT)