import discord, asyncio, requests, random, configparser, os, re
from discord.ext import commands
from discord.ui import Button, View
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
        if ctx.interaction.channel_id in constants.ALLOW_CHANNEL:
            self.__TIMEOUT = None
        else:
            read_config = configparser.ConfigParser()
            path = os.path.join(os.path.abspath(__file__+"/../../"),"config", "config.ini")
            read_config.read(path)
            self.__TIMEOUT = int(read_config.get("config", "TIME_OUT"))
            
        symbols_list = symbols.replace(' ','').split(",")

        # Check symbols contains list of stocks or not
        if not isinstance(symbols_list, list):
            symbols = [symbols_list]
        else:
            symbols = symbols_list
            
        for symbol in symbols:
            symbol = symbol.upper()
        
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
            if float(data['PriceCurrent']) >= float(data['PriceCeiling']) * (1.0 - constants.VARIANCE):
                print(float(data['PriceCeiling']) * (1.0 - constants.VARIANCE))
                mess = random.choice(constants.MESS_CE)
                embed = discord.Embed(color=constants.COLOR_CE)
            
            elif float(data['PriceCurrent']) <= float(data['PriceFloor']) * (1.0 + constants.VARIANCE):
                print(float(data['PriceFloor']) * (1.0 - constants.VARIANCE))
                mess = random.choice(constants.MESS_FL)
                embed = discord.Embed(color=constants.COLOR_FL)
            
            elif float(data['PriceCurrent']) > float(data['PriceBasic']):
                mess = random.choice(constants.MESS_UP)
                embed = discord.Embed(color=constants.COLOR_UP)
            
            elif float(data['PriceCurrent']) < float(data['PriceBasic']):
                mess = random.choice(constants.MESS_DOWN)
                embed = discord.Embed(color=constants.COLOR_DOWN)
            
            elif float(data['PriceCurrent']) == float(data['PriceBasic']):
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
    
    async def interval_searcher(ctx: discord.AutocompleteContext):
        return [interval for interval in constants.INTERVAL]        
    
    @slash_command(
        name='chart',
        description='Xem biểu đồ giá của cổ phiếu tại sàn Việt Nam.'
    )
    async def getStockChart(self, 
        ctx, 
        symbols: Option(str, "Nhập mã cổ phiếu"), 
        interval: Option(
            str,
            "Chọn các khoảng thời gian sau",
            autocomplete=discord.utils.basic_autocomplete(interval_searcher),
            default=constants.INTERVAL[0]),
        draw_ma: Option(bool, "Vẽ MA", default=True),
        draw_bb: Option(bool, "Vẽ BB", default=True),
        draw_vol: Option(bool, "Vẽ Volume", default=True),
        draw_rsi: Option(bool, "Vẽ RSI", default=True),
        draw_macd: Option(bool, "Vẽ MACD", default=True)
        ):
        symbols = await self.default_command(ctx, symbols)

        for symbol in symbols:
            await self.getEachChart(ctx, symbol.upper(), interval, draw_ma, draw_bb, draw_vol, draw_rsi, draw_macd)

    async def getEachChart(self, ctx, symbol, interval, draw_ma, draw_bb, draw_vol, draw_rsi, draw_macd):
        start_date = utils.get_last_year_date(delta=365*3)
        end_date = utils.get_today_date()
        len = 30
        
        loader = fetch.DataLoader(symbol, start_date, end_date)
        data = loader.fetchPrice()
        
        if interval == constants.INTERVAL[1]:
            data = utils.convertDailyToWeek(data)
        
        label = f"Biểu đồ của {symbol} trong {len} {interval.lower()} gần đây!"
        figure.drawFigure(data ,symbol, length=len, label=label,
                          drawMA=draw_ma, drawBB=draw_bb, drawVol=draw_vol, drawRSI=draw_rsi, drawMACD=draw_macd)
        
        figure.img.seek(0)
        await ctx.respond(f"{label}", delete_after=self.__TIMEOUT)
        await ctx.send(file=discord.File(figure.img, filename=f'{symbol}.png'), delete_after=self.__TIMEOUT)
        figure.img.seek(0)
        
    @slash_command(
        name='news',
        description='Xem tin tức mới nhất của cổ phiếu tại sàn Việt Nam.'
    )
    async def getStockNews(self, 
        ctx, 
        symbols: Option(str, "Nhập mã cổ phiếu", default="Tất cả"), 
        count: Option(
            int,
            "Số lượng bài báo",
            min_value=1, max_value=15, default=5),
        comment: Option(
            bool,
            "Lấy bình luận",
            default=False),
        ):
        symbols = await self.default_command(ctx, symbols)
            
        for symbol in symbols:
            if symbol == "Tấtcả":
                symbol = "ALL"
            
            count = max(count, 1)
            count = min(count, 15)
            
            await self.getEachNews(ctx, symbol.upper(), get_to=count, comment=comment)
            
    async def getEachNews(self, ctx, symbol, comment=False, get_from=0, get_to=5):
        async def get_embed(ctx=ctx, symbol=symbol, comment=comment, get_from=get_from, get_to=get_to):
            count = get_to - get_from
            data = fetch.fetchStockNews(symbol, offset = get_from, count=count, getComment=comment)
            print(f"Fetching news for {symbol}, {count} news, {'with' if comment else 'without'} comment")
            # print(data)
                
            if (data != None):                    
                embed = discord.Embed()
                embed.set_author(name=f'{count} {"bình luận" if comment else "tin tức"} mới nhất của {f"{symbol}" if symbol != "ALL" else "THỊ TRƯỜNG"}:')
                
                try:
                    idx = 0
                    for i in range(count):                        
                        symbols_info = ""
                        if len(data[idx]["taggedSymbols"]) != 0:
                            print(data[idx]["taggedSymbols"])
                            symbols_info = f"\n"
                            for get_tagged_symbol in data[idx]["taggedSymbols"]:
                                if symbols_info != f"\n": symbols_info += "; "
                                symbols_info = symbols_info + f"*{get_tagged_symbol['symbol']}: {utils.format_percent(get_tagged_symbol['percentChange'])}*"
                        
                        print(symbols_info)
                        print("-------------------------------------------------------")
                            
                        if not comment:
                            title = data[idx]["title"]
                            content = re.sub("\n|\r", "", data[idx]["description"])
                        else:
                            title = data[idx]["user"]["name"]
                            content = data[idx]["originalContent"]
                        
                        DIVIDER = "------------------------------------------------------"
                        URL = "https://fireant.vn/home/content/news/"
                        
                        embed.add_field(name=f'{DIVIDER}\n{title}', 
                                        value=f'{content}\n[Xem tại đây]({URL}{data[idx]["postID"]})\n{symbols_info}\nCập nhật lúc: {utils.get_current_time(data[idx]["date"])}\n', 
                                        inline = False)
                        idx = idx + 1
                    return embed
                except:
                    await ctx.respond(f"Không tìm thấy tin tức của ** {f'{symbol}' if symbol != 'ALL' else 'THỊ TRƯỜNG'}**", delete_after=self.__TIMEOUT)
                    return None
            else:
                mess = "Mã cổ phiếu không hợp lệ."
                await ctx.respond(mess, delete_after=self.__TIMEOUT)
                return None
        
        await ctx.respond(f"{'Bình luận' if comment else 'Tin tức'} của ** {f'{symbol}' if symbol != 'ALL' else 'THỊ TRƯỜNG'}** đến ngày {utils.get_today_date()}", delete_after=self.__TIMEOUT)                    
                
        buttonPrev = Button(label="Trước đó", style=discord.ButtonStyle.primary)
        buttonNext = Button(label="Tiếp theo", style=discord.ButtonStyle.primary)
        count = get_to - get_from
        
        # if get_from < count:
        #     buttonPrev.disabled = True
        # else:
        #     buttonPrev.disabled = False
            
        async def on_prev_click(interaction):
            nonlocal get_from
            nonlocal get_to

            if get_from >= get_to - get_from:
                get_from = get_from - count
                get_to = get_to - count
                
                print("back")
                embed = await get_embed(ctx, symbol, comment, get_from, get_to)
                if embed != None:
                    await interaction.response.edit_message(embed=embed)
                
        async def on_next_click(interaction):
            nonlocal get_from
            nonlocal  get_to
            get_from = get_from + count
            get_to = get_to + count
            print("next")
            embed = await get_embed(ctx, symbol, comment, get_from, get_to)
            if embed != None:
                await interaction.response.edit_message(embed=embed)
            
        buttonPrev.callback = on_prev_click
        buttonNext.callback = on_next_click
        
        view = View()
        view.add_item(buttonPrev)
        view.add_item(buttonNext)
        
        embed = await get_embed(ctx, symbol, comment, get_from, get_to)
        if embed != None:
            await ctx.send(embed=embed, delete_after=self.__TIMEOUT, view=view)    