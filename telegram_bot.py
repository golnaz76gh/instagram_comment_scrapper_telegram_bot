import os
import re
from dotenv import load_dotenv
import logging
import telebot
from comment_scrapper import InstagramCommentScraper
from db import create_tables
from logging_config import setup_logging

# Set up logging
setup_logging()

# Load environment variables from the .env file
load_dotenv()

# Initialize the Telegram bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def clean_markdown(text):
    """Clean text to ensure it's properly formatted for Markdown."""
    # Escape characters that could cause issues
    text = re.sub(r'[_*`\[\]()]', lambda x: '\\' + x.group(0), text)
    return text

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 *Welcome to Instagram Comment Scraper Bot!*\n\n"
        "Send me an Instagram post URL to get comments.\n"
        "For a list of available commands, type /help."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "✨ *Welcome to Instagram Comment Scraper Bot!*\n\n"
        "Here are the commands you can use:\n\n"
        "* /start* - Start the bot and receive a welcome message.\n"
        "* /help* - Display this help message.\n\n"
        "To get comments from an Instagram post, send the post URL directly to the bot.\n"
        "I will fetch and return the comments for you!"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def fetch_comments(message):
    """Fetch comments from an Instagram post based on the provided URL."""
    url = message.text.strip()
    scraper = InstagramCommentScraper()

    try:
        shortcode = scraper.extract_shortcode_from_url(url)
        
        if not shortcode:
            bot.reply_to(message, "❌ Invalid Instagram URL. Please try again.")
            return

        bot.reply_to(message, "🔄 Fetching comments, please wait...")
        
        comments_data = scraper.get_comments(shortcode, 5000)
        
        if comments_data:
            comments = [
                f"💬 {clean_markdown(edge['node']['text'])}" for edge in comments_data["data"]["shortcode_media"]["edge_media_to_comment"]["edges"]
            ]
            comments_text = "\n".join(comments)
            if len(comments_text) > 4096:
                for x in range(0, len(comments_text), 4096):
                    bot.send_message(message.chat.id, clean_markdown(comments_text[x:x+4096]), parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, clean_markdown(comments_text), parse_mode='Markdown')
        else:
            bot.reply_to(message, "⚠️ Failed to fetch comments. Please try again later.")
        
    except Exception as e:
        logging.error(f"Error in fetch_comments: {e}")
        bot.reply_to(message, "❌ An error occurred while fetching comments. Please try again later.")
    finally:
        scraper.close_browser()

if __name__ == "__main__":
    create_tables()
    bot.infinity_polling()