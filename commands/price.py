import discord, asyncio, requests, random, configparser, os
from discord.ext import commands
from discord.commands import slash_command, Option
from PIL import Image, ImageDraw, ImageFont
import logging
import stock_modules.fetch as fetch
import stock_modules.utils as utils
import stock_modules.figure as figure
import stock_modules.indicate as indicate
import commands.constants as constants

class Price(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def default_command(self, ctx, symbols):
        # print(ctx.interaction.channel_id)
        
        if ctx.interaction.channel_id in constants.ALLOW_CHANNEL:
            self.__TIMEOUT = None
        else:
            read_config = configparser.ConfigParser()
            path = os.path.join(os.path.abspath(__file__+"/../../"),"config", "config.ini")
            read_config.read(path)
            self.__TIMEOUT = int(read_config.get("config", "TIME_OUT"))
            
        # symbols = str(symbols)
        symbols_list = symbols.replace(' ','').split(",")

        # Check symbols contains list of stocks or not
        if not isinstance(symbols_list, list):
            symbols = [symbols_list]
        else:
            symbols = symbols_list
        
        return symbols
    
    @discord.slash_command(
        name='price',
        description='Kiểm tra giá cổ phiếu tại sàn Việt Nam.'
    )
    async def getStockPrice(self, ctx, *, symbols):
        symbols = await self.default_command(ctx, symbols)
        
        for symbol in symbols:
            await self.getEachStockPrice(ctx, symbol)
        
    async def getEachStockPrice(self, ctx, symbol):
        data = fetch.fetchCurrentPrice(symbol.upper())

        if (data != None):
            mess = ""
            
            changePrice = float(data['PriceCurrent']) - float(data['PriceBasic'])

            changeRate = (float(changePrice) / float(data['PriceBasic'])) * 100.0
            changeRate = round(changeRate, 2)
            
            # Currently for HOSE market only
            if changeRate >= 6.9:
                mess = random.choice(constants.MESS_CE)
                embed = discord.Embed(color=constants.COLOR_CE)
            elif changeRate <= -6.9:
                mess = random.choice(constants.MESS_FL)
                embed = discord.Embed(color=constants.COLOR_FL)
            elif changeRate > 0.0:
                mess = random.choice(constants.MESS_UP)
                embed = discord.Embed(color=constants.COLOR_UP)
            elif changeRate < 0.0:
                mess = random.choice(constants.MESS_DOWN)
                embed = discord.Embed(color=constants.COLOR_DOWN)
            elif changeRate == 0.0:
                mess = random.choice(constants.MESS_TC)
                embed = discord.Embed(color=constants.COLOR_TC)
                
            price_str = str(data["PriceCurrent"])
            mess = mess.replace("#code#",symbol.upper()).replace("#price#", price_str)
            
            embed.set_author(name=f'Giá {symbol.upper()} tại {utils.get_current_time(data["Date"])}:')
            embed.add_field(name='Giá: ', value=f'{utils.format_value(data["PriceCurrent"])}', inline=True)
            embed.add_field(name='% thay đổi: ', value=f'{utils.format_percent(changeRate)}', inline=True)
            embed.add_field(name='Giá thay đổi: ', value=f'{utils.format_value(changePrice)}', inline=True)
            
            embed.add_field(name='KL Mua: ', value=f'{utils.format_value(data["TotalActiveBuyVolume"])}', inline=True)
            embed.add_field(name='KL Bán: ', value=f'{utils.format_value(data["TotalActiveSellVolume"])}', inline=True)
            embed.add_field(name='KLGD: ', value=f'{utils.format_value(data["TotalVolume"])}', inline=True)
            
            embed.add_field(name='KLKN Mua: ', value=f'{utils.format_value(data["BuyForeignQuantity"])}', inline=True)
            embed.add_field(name='KLKN Bán: ', value=f'{utils.format_value(data["SellForeignQuantity"])}', inline=True)        
        
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            await ctx.send(embed=embed, delete_after=self.__TIMEOUT)
        else:
            mess = "Mã cổ phiếu không hợp lệ."
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            
    @discord.slash_command(
        name='briefstats',
        description='Kiểm tra thông tin cơ bản của cổ phiếu tại sàn Việt Nam.'
    )
    async def getStockBrief(self, ctx, *, symbols):
        symbols = await self.default_command(ctx, symbols)

        for symbol in symbols:
            await self.getEachStockBrief(ctx, symbol)

    async def getEachStockBrief(self, ctx, symbol):
        data = fetch.fetchFianancialInfo(symbol.upper())
        # logging.info(data)
        if (data != None):
            embed = discord.Embed(title=f'Thông tin cơ bản của {symbol.upper()}')
            
            embed.add_field(name='P/E: ', value=f'{utils.format_value(data["DilutedPE"], basic = False)}', inline=True)
            embed.add_field(name='P/B: ', value=f'{utils.format_value(data["PB"], basic = False)}', inline=True)
            embed.add_field(name='P/S: ', value=f'{utils.format_value(data["PS"], basic = False)}', inline=True)
            embed.add_field(name='EPS: ', value=f'{utils.format_value(data["DilutedEPS"], basic = False)}', inline=True)
            
            embed.add_field(name='Thanh toán nhanh: ', value=f'{utils.format_value(data["QuickRatio"], basic=False)}', inline=True)
            embed.add_field(name='Thanh toán hiện hành: ', value=f'{utils.format_value(data["ProfitGrowth_MRQ"], basic=False)}', inline=True)
            embed.add_field(name='Tổng nợ / VCSH: ', value=f'{utils.format_value(data["TotalDebtOverEquity"], basic=False)}', inline=True)
            embed.add_field(name='Tổng nợ / Tổng tài sản: ', value=f'{utils.format_value(data["TotalDebtOverAssets"], basic=False)}', inline=True)
            
            embed.add_field(name='Vòng quay tổng tài sản: ', value=f'{utils.format_value(data["TotalAssetsTurnover"], basic=False)}', inline=True)
            embed.add_field(name='Vòng quay hàng tồn kho: ', value=f'{utils.format_value(data["InventoryTurnover"], basic=False)}', inline=True)
            embed.add_field(name='Vòng quay các khoản phải thu: ', value=f'{utils.format_value(data["ReceivablesTurnover"], basic=False)}', inline=True)
            
            embed.add_field(name='Tỷ lệ lãi gộp: ', value=f'{utils.format_percent(data["GrossMargin"], multiply = 100)}', inline=True)
            embed.add_field(name='Tỷ lệ lãi từ HĐKD: ', value=f'{utils.format_percent(data["OperatingMargin"], multiply = 100)}', inline=True)
            embed.add_field(name='Tỷ lệ EBIT: ', value=f'{utils.format_percent(data["EBITMargin"], multiply = 100)}', inline=True)
            embed.add_field(name='Tỷ lệ lãi ròng: ', value=f'{utils.format_percent(data["NetProfitMargin"], multiply = 100)}', inline=True)
            
            embed.add_field(name='ROA: ', value=f'{utils.format_percent(data["ROA"], multiply = 100)}', inline=True)
            embed.add_field(name='ROE: ', value=f'{utils.format_percent(data["ROE"], multiply = 100)}', inline=True)
            embed.add_field(name='ROIC: ', value=f'{utils.format_percent(data["ROIC"], multiply = 100)}', inline=True)
            
            await ctx.respond(f"Thông tin của doanh nghiệp: {symbol.upper()} đến ngày {utils.get_today_date()}", delete_after=self.__TIMEOUT)
            await ctx.send(embed=embed, delete_after=self.__TIMEOUT)
        else:
            mess = "Mã cổ phiếu không hợp lệ."
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
            
    @slash_command(
        name='chart',
        description='Xem biểu đồ giá của cổ phiếu tại sàn Việt Nam.'
    )
    async def getStockChart(self, ctx, *, symbols):
        symbols = await self.default_command(ctx, symbols)

        for symbol in symbols:
            await self.getEachChart(ctx, symbol)

    async def getEachChart(self, ctx, symbol):
        len = 30
        symbol = symbol.strip().upper()
        start_date = utils.get_last_year_date()
        end_date = utils.get_today_date()
        loader = fetch.DataLoader(symbol, start_date, end_date)
        data = loader.fetchPrice()
        figure.drawFigure(data ,symbol, length=len)
        figure.img.seek(0)
        await ctx.respond(f"Biểu đồ của {symbol} trong {len} ngày gần đây!", delete_after=self.__TIMEOUT)
        await ctx.send(file=discord.File(figure.img, filename=f'{symbol}.png'), delete_after=self.__TIMEOUT)
        figure.img.seek(0)
        
    @slash_command(
        name='news',
        description='Xem tin tức mới nhất của cổ phiếu tại sàn Việt Nam.'
    )
    async def getStockNews(self, ctx, *, symbols):
        symbols = await self.default_command(ctx, symbols)
            
        for symbol in symbols:
            await self.getEachNews(ctx, symbol.upper())
            
    async def getEachNews(self, ctx, symbol, count = 5):
        data = fetch.fetchStockNews(symbol)
        
        if (data != None):
            embed = discord.Embed()
            embed.set_author(name=f'05 tin mới nhất của {symbol}:')
            
            idx = 0
            for i in range(count):
                logging.info(data[idx])
                embed.add_field(name=f'{data[idx]["Title"]}', value=f'[Xem tại đây]({data[idx]["NewsUrl"]}) \n Cập nhật lúc: {utils.get_current_time(data[idx]["Date"])}', inline = False)
                idx = idx + 1
                
            await ctx.respond(f"Tin tức của doanh nghiệp: {symbol.upper()} đến ngày {utils.get_today_date()}", delete_after=self.__TIMEOUT)
            await ctx.send(embed=embed, delete_after=self.__TIMEOUT)
        else:
            mess = "Mã cổ phiếu không hợp lệ."
            await ctx.respond(mess, delete_after=self.__TIMEOUT)
        