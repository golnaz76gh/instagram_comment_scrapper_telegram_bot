# Instagram Comment Scraper Bot

A Telegram bot for extracting comments from Instagram posts using Selenium and PostgreSQL as the database.

## Features

- Extract comments from Instagram posts
- Save comments to a PostgreSQL database
- Send comments to users on Telegram

## Prerequisites

- Python 3.7 or higher
- A Telegram account and bot token
- An Instagram account (for login)
- PostgreSQL for the database

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/golnaz76gh/instagram_comment_scrapper_telegram_bot.git
cd instagram-comment-scraper-bot
```

### 2. Install Dependencies

Create a virtual environment and install the dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure the `.env` File

The `.env` file should include the following environment variables:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
QUERY_HASH=your_instagram_query_hash
DATABASE_URL=postgresql://username:password@localhost/dbname
```

### 4. Run the Bot

To start the Telegram bot and create the necessary database tables, execute:

```bash
python telegram_bot.py
```

## Project Structure

- `telegram_bot.py`: Main script to run the Telegram bot.
- `comment_scrapper.py`: Class for extracting comments from Instagram posts.
- `db_setup.py`: Configures the database.
- `db.py`: Creates tables and saves comments to database.
- `models.py`: Database models for SQLAlchemy.
- `logging_config.py`: Logging configuration.
- `.env`: Environment configuration file.

## Usage

1. **Start the Bot**: Run the bot and send the `/start` command to receive a welcome message.
2. **Request Comments**: Send the URL of an Instagram post to the bot to get comments for that post.
3. **View Comments**: Comments will be sent to you as text messages.

## Troubleshooting

If you encounter any issues, please ensure:

- The `.env` file is properly configured.
- PostgreSQL is running and correctly configured.
- The Telegram bot token and Instagram login credentials are correct.

For further assistance, please refer to the [Telegram Bot API Documentation](https://core.telegram.org/bots/api) and the [Selenium Documentation](https://www.selenium.dev/documentation/).

## Contributing

If you would like to contribute to the project, please submit a Pull Request or reach out via the project Issues.