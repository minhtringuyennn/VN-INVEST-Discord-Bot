<<<<<<< HEAD
# StockNotifer

## 1. Thông tin
Custom module sử dụng cho việc clone một hoặc nhiều giá cổ phiếu trong quá khứ, từ đó đánh giá, xác định các điểm vào hoặc ra bằng việc phân tích kĩ thuật.

Các mô hình mẫu sẽ được update dần. Đoạn Code chỉ phục vụ cho việc nghiên cứu và thử nghiệm. **Không đưa ra khuyến nghị mua hay bán cổ phiếu.**

Code có sử dụng API của VNDIRECT và code từ  [repo của phamdinhkhanh](https://github.com/phamdinhkhanh/vnquant). Xin chân thành cảm ơn.

## 2. Cài đặt
Sau khi clone thư mục về có thể chạy file main.py và nhập cổ phiếu cần xem.
```
git clone https://github.com/minhtringuyennn/StockNotifer.git
python main.py
```
=======
# StockNotifer

## 1. Thông tin
Bot phục vụ cho việc theo dõi, phân tích thị trường chứng khoán Việt Nam.

Các mô hình mẫu sẽ được update dần. Đoạn Code chỉ phục vụ cho việc nghiên cứu và thử nghiệm. **Không đưa ra khuyến nghị mua hay bán cổ phiếu.**

## 2. Cài đặt
Bot sử dụng pycord, vì thế nếu đang sử dụng discord.py, hãy chạy ```pip uninstall discord.py``` trước.
Cần **Python 3.8 trở lên** để chạy bot. Lưu ý phải sửa đổi file ```config.ini``` trước khi chạy.

```
git clone https://github.com/minhtringuyennn/StockNotifer.git
pip install -r requirements.txt
python3 bot_stock.py
```

## 3. Thêm tính năng cho bot
Các function xử lý được nằm trong `/stock_modules`.
Các commands Discord được nằm trong `/commands`


### Thêm tính năng:
1. Tạo file mới trong `/commands`
2. Thêm mẫu sau
```python
import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option #, SlashCommandGroup nếu muốn tạo nhóm commands
class CogName(commands.Cog): # Thay đổi 'CogName' với tên cog bạn muốn.
    def __init__(self, bot):
        self.bot = bot
    category = SlashCommandGroup('Category name', 'Chú thích')
    @slash_command( # Đổi sang @category.command( nếu phân nhóm commands.
        name='command name here',
        description='commnad description here',
    )
    async def commandname(self, ctx, option: Option(str, 'This is option', required=True)):
        embed = discord.Embed(
            title='hello',
            description=f'{option}',
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(CogName(bot))
```
3. Thêm đường dẫn vào `stock_bot.py` với dạng `cogs.commands.filename`
>>>>>>> b6132805818c3f49cacf84d3438012040128a34f
