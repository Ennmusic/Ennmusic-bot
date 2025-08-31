import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioPiped
from config import Config
import yt_dlp

# Bot client
bot = Client(
    "MusicBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
)

# Assistant client
user = Client(
    "assistant",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION_STRING
)

# Voice call handler
pytgcalls = PyTgCalls(user)

# Store music queues
queues = {}

# YouTube search
def yt_search(query):
    opts = {"format": "bestaudio", "noplaylist": True, "quiet": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        return info["url"], info["title"]

# Play command
@bot.on_message(filters.command("play") & filters.group)
async def play(_, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply("❌ Please give me a song name or link.")
    query = " ".join(message.command[1:])
    m = await message.reply("🔎 Searching...")
    url, title = yt_search(query)

    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(url)

    await m.edit(f"🎶 Added **{title}** to queue.")

    if not pytgcalls.active_calls.get(chat_id):
        await pytgcalls.join_group_call(chat_id, AudioPiped(url))

# Skip command
@bot.on_message(filters.command("skip") & filters.group)
async def skip(_, message):
    chat_id = message.chat.id
    if chat_id in queues and queues[chat_id]:
        queues[chat_id].pop(0)
        if queues[chat_id]:
            url = queues[chat_id][0]
            await pytgcalls.change_stream(chat_id, AudioPiped(url))
            await message.reply("⏭ Skipped to next song.")
        else:
            await pytgcalls.leave_group_call(chat_id)
            await message.reply("✅ Queue finished, leaving VC.")
    else:
        await message.reply("❌ No songs in queue.")

# Stop command
@bot.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    chat_id = message.chat.id
    if chat_id in queues:
        queues.pop(chat_id)
    await pytgcalls.leave_group_call(chat_id)
    await message.reply("🛑 Stopped and cleared queue.")

# Pause command
@bot.on_message(filters.command("pause") & filters.group)
async def pause(_, message):
    await pytgcalls.pause_stream(message.chat.id)
    await message.reply("⏸ Paused.")

# Resume command
@bot.on_message(filters.command("resume") & filters.group)
async def resume(_, message):
    await pytgcalls.resume_stream(message.chat.id)
    await message.reply("▶️ Resumed.")

# Start bot
async def start():
    await bot.start()
    await user.start()
    await pytgcalls.start()
    print("✅ Bot is running...")
    await idle()
    await bot.stop()
    await user.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start())
