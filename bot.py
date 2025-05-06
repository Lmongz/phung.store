import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from yt_dlp import YoutubeDL

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token from BotFather
BOT_TOKEN = "7650863098:AAHD9oruQSzcNL7Pxe51nufF6FJX_9zzE38"
# Replace with your group chat ID for logs
LOG_GROUP_ID = "-4668261975"

# Rate limiting (e.g., 5 downloads per user per hour)
USER_DOWNLOADS = {}

# Function to handle the /start command
async def start(update: Update, context):
    welcome_message = (
        "🎥 *Welcome to the Ultimate Video Downloader Bot!* 🎵\n\n"
        "Send me a link, and I'll download videos or audio for you from:\n"
        "- YouTube\n- TikTok\n- Instagram\n- Twitter\n- Facebook\n- And more!\n\n"
        "Use the buttons below to get started!"
    )
    keyboard = [
        [InlineKeyboardButton("Download Video", callback_data="video")],
        [InlineKeyboardButton("Download Audio", callback_data="audio")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

# Function to handle video links
async def download_video(update: Update, context):
    user_id = update.message.from_user.id
    url = update.message.text

    # Rate limiting
    if user_id in USER_DOWNLOADS and USER_DOWNLOADS[user_id] >= 5:
        await update.message.reply_text("❌ You've reached the download limit. Please try again later.")
        return

    # Send a stylish processing message
    await update.message.reply_text("*Processing your request...* 🛠️", parse_mode="Markdown")

    # Create buttons for video and audio options
    keyboard = [
        [InlineKeyboardButton("Download Video", callback_data=f"video_{url}")],
        [InlineKeyboardButton("Download Audio", callback_data=f"audio_{url}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

# Function to handle button callbacks
async def button_callback(update: Update, context):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    user_id = query.from_user.id

    await query.answer()

    # Check if the callback data is valid
    if "_" not in data:
        await query.edit_message_text("❌ Invalid option. Please try again.")
        return

    # Split the callback data into type and URL
    try:
        action, url = data.split("_", 1)
    except ValueError:
        await query.edit_message_text("❌ Invalid option. Please try again.")
        return

    if action == "video":
        await query.edit_message_text("*Downloading video...* 🎥\nProgress: 0%", parse_mode="Markdown")
        format_key = "bestvideo+bestaudio/best"
    elif action == "audio":
        await query.edit_message_text("*Downloading audio...* 🎵\nProgress: 0%", parse_mode="Markdown")
        format_key = "bestaudio"
    else:
        await query.edit_message_text("❌ Invalid option. Please try again.")
        return

    # Function to update download progress
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d['_percent_str']
            speed = d['_speed_str']
            # Use asyncio.run_coroutine_threadsafe to properly await the coroutine
            asyncio.run_coroutine_threadsafe(
                query.edit_message_text(f"*Downloading {action}...* 🛠️\nProgress: {percent}\nSpeed: {speed}", parse_mode="Markdown"),
                context.application.update_queue.loop
            )

    # Download the video/audio using yt-dlp
    try:
        ydl_opts = {
            'format': format_key,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'cookiefile': 'cookies.txt',  # Add cookies file for restricted platforms
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Send the downloaded file to the user
        with open(file_path, 'rb') as file:
            if action == "video":
                sent_message = await context.bot.send_video(chat_id=chat_id, video=file, caption="Here's your video! 🎥")
            elif action == "audio":
                sent_message = await context.bot.send_audio(chat_id=chat_id, audio=file, caption="Here's your audio! 🎵")

        # Log the download to the group
        log_message = (
            f"📥 *New Download* 📥\n\n"
            f"*User:* {update.effective_user.full_name} (@{update.effective_user.username})\n"
            f"*Link:* {url}\n"
            f"*Type:* {'Video' if action == 'video' else 'Audio'}"
        )
        await context.bot.send_message(chat_id=LOG_GROUP_ID, text=log_message, parse_mode="Markdown")

        # Update download count for rate limiting
        if user_id in USER_DOWNLOADS:
            USER_DOWNLOADS[user_id] += 1
        else:
            USER_DOWNLOADS[user_id] = 1

        # Delete the file after 5 seconds
        await asyncio.sleep(5)
        os.remove(file_path)
        await sent_message.reply_text("✅ The downloaded file has been deleted.")

    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        await query.edit_message_text("❌ Sorry, I couldn't download the file. Please check the link and try again.")

# Admin command to check bot stats
async def stats(update: Update, context):
    if update.message.from_user.id != ADMIN_ID:  # Replace with your admin user ID
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    total_downloads = sum(USER_DOWNLOADS.values())
    await update.message.reply_text(f"📊 *Bot Stats*\n\nTotal Downloads: {total_downloads}", parse_mode="Markdown")

# Main function to run the bot
def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler("stats", stats))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()