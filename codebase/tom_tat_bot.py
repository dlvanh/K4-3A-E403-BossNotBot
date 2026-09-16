import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
from openai import AsyncOpenAI
import os
import sys

# Console Windows mặc định dùng cp1252, không encode được tiếng Việt có dấu
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

# Khởi tạo bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

from dotenv import load_dotenv

# Nạp OPENAI_API_KEY từ file .env (copy .env.example thành .env và dán key vào)
load_dotenv()

# Khởi tạo OpenAI client (async để không chặn event loop của bot)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = "gpt-4o-mini"

# Lưu trữ các tin nhắn để tóm tắt
MESSAGE_LIMIT = 50  # Số lượng tin nhắn tối đa để lấy

# File lưu danh sách kênh đã đăng ký làm nguồn thông báo, để bot "nhớ" qua các lần khởi động lại
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_config.json")

class TomTatBot:
    def __init__(self):
        self.conversation_history = {}
        # {guild_id (str): [channel_id, ...]}
        self.announcement_channels = self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f).get("announcement_channels", {})
            except Exception as e:
                print(f"Lỗi đọc config: {e}")
        return {}

    def _save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"announcement_channels": self.announcement_channels}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu config: {e}")

    def add_announcement_channel(self, guild_id, channel_id):
        """Đăng ký 1 kênh làm nguồn thông báo. Trả về False nếu đã đăng ký từ trước."""
        key = str(guild_id)
        channels = self.announcement_channels.setdefault(key, [])
        if channel_id in channels:
            return False
        channels.append(channel_id)
        self._save_config()
        return True

    def remove_announcement_channel(self, guild_id, channel_id):
        """Bỏ đăng ký 1 kênh khỏi nguồn thông báo. Trả về False nếu chưa từng đăng ký."""
        key = str(guild_id)
        channels = self.announcement_channels.get(key, [])
        if channel_id not in channels:
            return False
        channels.remove(channel_id)
        self._save_config()
        return True

    def get_registered_announcement_channels(self, guild):
        """Trả về danh sách discord.TextChannel đã đăng ký cho guild này (bỏ qua kênh đã bị xoá/mất quyền)."""
        ids = self.announcement_channels.get(str(guild.id), [])
        return [ch for cid in ids if (ch := guild.get_channel(cid)) is not None]

    async def get_recent_messages(self, channel, hours=4):
        """Lấy tin nhắn gần đây từ một channel"""
        try:
            messages = []
            time_threshold = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(hours=hours)
            
            async for msg in channel.history(limit=MESSAGE_LIMIT, after=time_threshold, oldest_first=False):
                if not msg.author.bot and msg.content.strip():
                    messages.append({
                        'author': msg.author.name,
                        'content': msg.content,
                        'time': msg.created_at.strftime('%H:%M'),
                        'jump_url': msg.jump_url,
                    })
            
            return list(reversed(messages))
        except Exception as e:
            print(f"Lỗi khi lấy tin nhắn: {e}")
            return []
    
    async def get_channel_announcements(self, guild, hours=24):
        """Lấy các thông báo từ các kênh đã đăng ký (ưu tiên); nếu guild chưa
        đăng ký kênh nào thì suy đoán theo tên kênh (có dấu hoặc không dấu)."""
        announcements = []
        time_threshold = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(hours=hours)

        target_channels = self.get_registered_announcement_channels(guild)
        if not target_channels:
            # Chưa ai đăng ký kênh nào bằng /tom-tat-them-kenh-thong-bao: suy đoán theo tên
            keywords = ('thông-báo', 'thong-bao', 'announce')
            target_channels = [
                ch for ch in guild.text_channels
                if any(k in ch.name.lower() for k in keywords)
            ]

        try:
            for channel in target_channels:
                async for msg in channel.history(limit=20, after=time_threshold, oldest_first=False):
                    if not msg.author.bot and msg.content.strip():
                        announcements.append({
                            'channel': channel.name,
                            'author': msg.author.name,
                            'content': msg.content,
                            'time': msg.created_at.strftime('%H:%M'),
                            'jump_url': msg.jump_url,
                        })
        except Exception as e:
            print(f"Lỗi khi lấy thông báo: {e}")

        return announcements
    
    async def summarize_with_ai(self, messages_text, mode="notice"):
        """Sử dụng OpenAI để tóm tắt tin nhắn"""
        prompts = {
            "notice": """Dựa vào các thông báo sau, hãy tóm tắt lại những điều quan trọng nhất (tối đa 5 điểm):
- Sắp xếp theo độ ưu tiên (việc gấp nhất trước)
- Rút gọn vào 1-2 dòng cho mỗi điểm
- Bao gồm deadline nếu có

Thông báo:
""",
            "chat": """Dựa vào đoạn trò chuyện sau, hãy tóm tắt các chủ đề chính được bàn luận:
- Liệt kê 3-5 chủ đề chính
- Ghi lại vấn đề/câu hỏi chưa có lời giải
- Rút gọn mỗi chủ đề vào 2-3 dòng

Trò chuyện:
""",
            "all": """Tóm tắt toàn bộ hoạt động của server (thông báo + trò chuyện):
- Phần 1: Thông báo quan trọng (deadline, thay đổi)
- Phần 2: Các chủ đề chính đang bàn luận
- Phần 3: Những vấn đề chưa được giải quyết

Dữ liệu:
"""
        }
        
        prompt = prompts.get(mode, prompts["notice"]) + messages_text

        try:
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Lỗi khi tóm tắt: {str(e)}"
    
    def format_sources_field(self, items, max_items=10, max_chars=900):
        """Dựng nội dung field liệt kê tin nhắn nguồn (kèm link nhảy tới tin gốc)
        để người xem đối chiếu với bản tóm tắt AI. Trả về None nếu không có gì."""
        if not items:
            return None
        lines = []
        used_chars = 0
        for it in items:
            content = it.get('content', '').replace('\n', ' ').strip()
            if len(content) > 80:
                content = content[:77] + "..."
            line = f"[{it.get('time', '')}] **{it.get('author', '?')}**: {content}"
            if it.get('jump_url'):
                line += f" — [xem]({it['jump_url']})"
            if len(lines) >= max_items or used_chars + len(line) + 1 > max_chars:
                break
            lines.append(line)
            used_chars += len(line) + 1
        remaining = len(items) - len(lines)
        text = "\n".join(lines)
        if remaining > 0:
            text += f"\n_...và {remaining} tin khác_"
        return text

    def format_summary(self, summary_text, title, source_fields=None):
        """Định dạng tóm tắt thành embed, kèm (tuỳ chọn) các field liệt kê tin nhắn nguồn.
        source_fields: list[(tên_field, nội_dung)]"""
        # Discord giới hạn 4096 ký tự/description và 6000 ký tự/embed, chừa chỗ cho các field nguồn
        max_desc = 3500 if source_fields else 4096
        if len(summary_text) > max_desc:
            summary_text = summary_text[:max_desc - 3] + "..."
        embed = discord.Embed(
            title=title,
            description=summary_text,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        for name, value in (source_fields or []):
            if value:
                embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(text="Bot Tom Tat")
        return embed

# Tạo instance của bot
tom_tat = TomTatBot()

@bot.event
async def on_ready():
    print(f'{bot.user} đã kết nối!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="/tom-tat-*"))

@bot.command(name='tom-tat-them-kenh-thong-bao', description='Đăng ký kênh này (hoặc kênh chỉ định) làm nguồn thông báo')
async def tom_tat_them_kenh_thong_bao(ctx, kênh: discord.TextChannel = None):
    """Đăng ký 1 kênh làm nguồn cho /tom-tat-thong-bao, nhớ đến khi bị xoá bằng /tom-tat-xoa-kenh-thong-bao"""
    if kênh is None:
        kênh = ctx.channel

    added = tom_tat.add_announcement_channel(ctx.guild.id, kênh.id)
    if added:
        await ctx.send(f"✅ Đã đăng ký {kênh.mention} làm kênh thông báo. Từ giờ `/tom-tat-thong-bao` sẽ luôn đọc kênh này, kể cả sau khi khởi động lại bot — đến khi bạn bỏ đăng ký bằng `/tom-tat-xoa-kenh-thong-bao`.")
    else:
        await ctx.send(f"{kênh.mention} đã được đăng ký từ trước rồi.")

@bot.command(name='tom-tat-xoa-kenh-thong-bao', description='Bỏ đăng ký kênh này (hoặc kênh chỉ định) khỏi nguồn thông báo')
async def tom_tat_xoa_kenh_thong_bao(ctx, kênh: discord.TextChannel = None):
    """Bỏ đăng ký 1 kênh khỏi nguồn thông báo"""
    if kênh is None:
        kênh = ctx.channel

    removed = tom_tat.remove_announcement_channel(ctx.guild.id, kênh.id)
    if removed:
        await ctx.send(f"🚫 Đã bỏ {kênh.mention} khỏi danh sách kênh thông báo.")
    else:
        await ctx.send(f"{kênh.mention} chưa được đăng ký trước đó.")

@bot.command(name='tom-tat-ds-kenh-thong-bao', description='Xem danh sách kênh thông báo đã đăng ký')
async def tom_tat_ds_kenh_thong_bao(ctx):
    """Liệt kê các kênh đã đăng ký làm nguồn thông báo cho server này"""
    channels = tom_tat.get_registered_announcement_channels(ctx.guild)
    if not channels:
        await ctx.send(
            "Chưa có kênh thông báo nào được đăng ký cho server này.\n"
            "Dùng `/tom-tat-them-kenh-thong-bao` ngay trong kênh cần thêm (hoặc chỉ định `#kênh`).\n"
            "Hiện tại `/tom-tat-thong-bao` đang tạm suy đoán theo tên kênh chứa \"thông-báo\"/\"announce\"."
        )
        return
    mentions = "\n".join(f"- {ch.mention}" for ch in channels)
    await ctx.send(f"📋 Kênh thông báo đã đăng ký:\n{mentions}")

@bot.command(name='tom-tat-thong-bao', description='Tóm tắt các thông báo của ngày')
async def tom_tat_thong_bao(ctx):
    """Tóm tắt thông báo"""
    await ctx.defer()
    
    try:
        # Gửi thông báo đang xử lý
        processing_embed = discord.Embed(
            title="🔄 Đang tóm tắt thông báo",
            description="Đang kết nối các kênh thông báo...",
            color=discord.Color.yellow()
        )
        processing_msg = await ctx.send(embed=processing_embed)
        
        # Lấy thông báo
        announcements = await tom_tat.get_channel_announcements(ctx.guild, hours=24)
        
        if not announcements:
            await ctx.send("Không tìm thấy thông báo nào trong 24 giờ qua.")
            return
        
        # Định dạng tin nhắn để gửi tới AI
        messages_text = "\n".join([
            f"[{a['time']}] {a['channel']}: {a['author']}\n{a['content']}"
            for a in announcements
        ])
        
        # Cập nhật: đang lọc
        processing_embed.description = "Đang lọc và phân loại thông báo..."
        await processing_msg.edit(embed=processing_embed)
        
        # Tóm tắt
        summary = await tom_tat.summarize_with_ai(messages_text, mode="notice")
        
        # Cập nhật: đang tạo báo cáo
        processing_embed.description = "Đang tạo báo cáo..."
        await processing_msg.edit(embed=processing_embed)
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
        # Gửi kết quả (kèm tin nhắn nguồn để đối chiếu)
        sources = tom_tat.format_sources_field(announcements)
        summary_embed = tom_tat.format_summary(
            summary,
            f"📋 Thông báo hôm nay - {datetime.now().strftime('%a, %d/%m')}",
            source_fields=[("📨 Tin nhắn nguồn", sources)]
        )
        await ctx.send(embed=summary_embed)
        
    except Exception as e:
        await ctx.send(f"❌ Lỗi: {str(e)}")

@bot.command(name='tom-tat-tro-chuyen', description='Tóm tắt trò chuyện của một kênh')
async def tom_tat_tro_chuyen(ctx, kênh: discord.TextChannel = None):
    """Tóm tắt trò chuyện trong kênh"""
    if kênh is None:
        kênh = ctx.channel
    
    await ctx.defer()
    
    try:
        # Kiểm tra quyền
        if not kênh.permissions_for(ctx.me).read_messages:
            await ctx.send(f"Bot không có quyền đọc kênh {kênh.mention}")
            return
        
        # Gửi thông báo đang xử lý
        processing_embed = discord.Embed(
            title=f"🔄 Đang tóm tắt #{kênh.name}",
            description=f"Đang đọc 4 giờ tin nhắn gần nhất...",
            color=discord.Color.yellow()
        )
        processing_msg = await ctx.send(embed=processing_embed)
        
        # Lấy tin nhắn
        messages = await tom_tat.get_recent_messages(kênh, hours=4)
        
        if not messages:
            await ctx.send(f"Không tìm thấy tin nhắn nào trong #{kênh.name} trong 4 giờ qua.")
            return
        
        # Định dạng tin nhắn
        messages_text = "\n".join([
            f"[{m['time']}] {m['author']}: {m['content']}"
            for m in messages
        ])
        
        # Cập nhật: đang nhóm chủ đề
        processing_embed.description = "Đang nhóm theo chủ đề..."
        await processing_msg.edit(embed=processing_embed)
        
        # Tóm tắt
        summary = await tom_tat.summarize_with_ai(messages_text, mode="chat")
        
        # Cập nhật: đang tạo báo cáo
        processing_embed.description = "Đang tạo báo cáo..."
        await processing_msg.edit(embed=processing_embed)
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
        # Gửi kết quả (kèm tin nhắn nguồn để đối chiếu)
        sources = tom_tat.format_sources_field(messages)
        summary_embed = tom_tat.format_summary(
            summary,
            f"💬 Trò chuyện #{kênh.name} - 4 giờ gần nhất",
            source_fields=[("📨 Tin nhắn nguồn", sources)]
        )
        await ctx.send(embed=summary_embed)
        
    except Exception as e:
        await ctx.send(f"❌ Lỗi: {str(e)}")

@bot.command(name='tom-tat-chung', description='Tóm tắt toàn bộ (thông báo + trò chuyện)')
async def tom_tat_chung(ctx):
    """Tóm tắt toàn bộ server"""
    await ctx.defer()
    
    try:
        # Gửi thông báo đang xử lý
        processing_embed = discord.Embed(
            title="🔄 Đang tóm tắt toàn bộ",
            description="Đang kết nối thông báo + kênh trò chuyện...",
            color=discord.Color.yellow()
        )
        processing_msg = await ctx.send(embed=processing_embed)
        
        # Lấy thông báo
        announcements = await tom_tat.get_channel_announcements(ctx.guild, hours=24)
        
        # Lấy tin nhắn từ kênh chung (nếu có)
        general_channel = None
        for channel in ctx.guild.text_channels:
            if 'chung' in channel.name.lower() or 'general' in channel.name.lower():
                general_channel = channel
                break
        
        messages = []
        if general_channel:
            messages = await tom_tat.get_recent_messages(general_channel, hours=4)
        
        # Cập nhật: đang lọc
        processing_embed.description = "Đang lọc và phân loại dữ liệu..."
        await processing_msg.edit(embed=processing_embed)
        
        # Định dạng dữ liệu
        combined_text = "=== THÔNG BÁO ===\n"
        combined_text += "\n".join([
            f"[{a['time']}] {a['channel']}: {a['author']}\n{a['content']}"
            for a in announcements
        ])
        
        if messages:
            combined_text += "\n\n=== TRÌNH CHUYỆN ===\n"
            combined_text += "\n".join([
                f"[{m['time']}] {m['author']}: {m['content']}"
                for m in messages
            ])
        
        # Tóm tắt
        summary = await tom_tat.summarize_with_ai(combined_text, mode="all")
        
        # Cập nhật: đang tạo báo cáo
        processing_embed.description = "Đang gộp thành bản tin..."
        await processing_msg.edit(embed=processing_embed)
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
        # Gửi kết quả (kèm tin nhắn nguồn để đối chiếu)
        summary_embed = tom_tat.format_summary(
            summary,
            f"📰 Bản tin chung - {datetime.now().strftime('%a, %d/%m')}",
            source_fields=[
                ("📢 Nguồn thông báo", tom_tat.format_sources_field(announcements, max_items=6, max_chars=500)),
                ("💬 Nguồn trò chuyện", tom_tat.format_sources_field(messages, max_items=6, max_chars=500)),
            ]
        )
        await ctx.send(embed=summary_embed)
        
    except Exception as e:
        await ctx.send(f"❌ Lỗi: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    """Xử lý lỗi command"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command không tồn tại. Dùng `/tom-tat-*` để bắt đầu.")
    else:
        await ctx.send(f"❌ Lỗi: {str(error)}")

def run_bot(token):
    """Chạy bot với token"""
    bot.run(token)

if __name__ == "__main__":
    # Lấy token từ biến môi trường hoặc input
    import os
    TOKEN = os.getenv('DISCORD_TOKEN') or input("Nhập Discord Bot Token: ")
    run_bot(TOKEN)
