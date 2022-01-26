import os, discord, configparser, time, asyncio
from datetime import datetime
from discord.ext import tasks
from discord.ext import commands

class DefaultCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        read_config = configparser.ConfigParser()
        path = os.path.join(os.path.abspath(__file__+"/../../"),"config", "config.ini")
        read_config.read(path)
        self.LogID = read_config.get("config", "LOG_CHANNEL")
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        channel = self.bot.get_channel(int(self.LogID))
        await channel.send(f'{ctx.message.author} run `{ctx.message.content}` in channel `{ctx.message.channel}` in server `{ctx.message.guild}`')
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Stock Bot is now ready!')
        print('Logged in as ---->', self.bot.user)
        print('ID:', self.bot.user.id)  

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