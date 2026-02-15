# Telegram Channel Admin Bot

Automated bot for managing a Telegram channel with features for collecting content from email, generating AI-powered posts, and publishing them on schedule.


## Features

- 📧 **Automatic content collection** from email messages
- 🤖 **AI-powered post generation** using Google Gemini API
- 📅 **Smart scheduling** of publications for the week ahead
- ⏰ **Human-like behavior simulation** during publication (random delays)
- 🎯 **Flexible configuration** via environment variables
- 🔄 **Automated execution** every 30 minutes via GitHub Actions

## How It Works

The bot operates in three main cycles:

### 1. Content Accumulation
Twice daily (morning and evening), the bot:
- Checks email for new materials
- Extracts article links from emails
- Resolves redirect URLs using Playwright
- Generates article summaries via Gemini API
- Compiles final posts with intro phrases
- Stores posts in PostgreSQL database

### 2. Publication Scheduling
Once a week (Friday by default), the bot:
- Calculates how many posts to publish in the upcoming week
- Randomly distributes publication times within the daily window (7:00-22:00)
- Ensures even distribution across days
- Saves the schedule to database

### 3. Post Publication
Every 30 minutes, the bot:
- Checks if any posts are scheduled for publication
- Applies random delay (0-25 minutes) to simulate human behavior
- Publishes the post to Telegram channel
- Updates publication status in database

## Tech Stack

- **Python 3.12**
- **PostgreSQL** (Supabase)
- **Google Gemini API** for content generation
- **Playwright** for URL redirect resolution
- **python-telegram-bot** for Telegram API integration
- **GitHub Actions** for automated execution

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure environment variables

Create a `.env` file with the following required variables:

```env
# Email settings
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_app_password

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Database (PostgreSQL)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel

# Optional settings (defaults will be used if not specified)
LOG_LEVEL=DEBUG
TZ=Europe/Minsk
MORNING_CHECK_HOUR=10
MORNING_CHECK_MINUTE=15
EVENING_CHECK_HOUR=19
EVENING_CHECK_MINUTE=45
EMAIL_CHECK_DELTA_MINUTES=30
SCHEDULE_CREATION_WEEKDAY=5
PUB_WINDOW_START_HOUR=7
PUB_WINDOW_START_MINUTE=0
PUB_WINDOW_END_HOUR=22
PUB_WINDOW_END_MINUTE=0
TIME_PERIODS_IN_SECS=[[0, 600], [600, 1200], [1200, 1500]]
PROBABILITIES=[70, 25, 5]
```

### 4. Initialize database

```bash
python -m db_tables_initializer.init_db_tables
```

### 5. Run locally

```bash
python main.py
```

## Deployment on GitHub Actions

### Setup Secrets

Go to `Settings` → `Secrets and variables` → `Actions` → **Secrets** tab and add:

- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `GEMINI_API_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

### Setup Variables (optional)

In the **Variables** tab, you can add any of the following to fine-tune bot behavior without code commits:

- `LOG_LEVEL` - logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `TZ` - timezone
- `MORNING_CHECK_HOUR`, `MORNING_CHECK_MINUTE` - morning email check time
- `EVENING_CHECK_HOUR`, `EVENING_CHECK_MINUTE` - evening email check time
- `EMAIL_CHECK_DELTA_MINUTES` - email check window
- `SCHEDULE_CREATION_WEEKDAY` - day of week for schedule creation (1=Mon, 7=Sun)
- `PUB_WINDOW_START_HOUR`, `PUB_WINDOW_START_MINUTE` - publication window start
- `PUB_WINDOW_END_HOUR`, `PUB_WINDOW_END_MINUTE` - publication window end
- `TIME_PERIODS_IN_SECS` - delay intervals before publication (JSON)
- `PROBABILITIES` - probabilities for each interval (JSON)

If not specified, default values from `config.py` will be used.

### Running the workflow

After configuring secrets and variables:

1. The bot will run automatically every 30 minutes
2. You can trigger manually: `Actions` → `Telegram Bot Runner` → `Run workflow`

## Project Structure

```
├── db_connector/          # Database connection management
├── db_tables_initializer/ # Database schema initialization
├── email_reader/          # Email reading and parsing
├── post_compiler/         # Post compilation with intro phrases
├── post_storage/          # Database operations for posts
├── processes/             # Main bot processes (accumulation, scheduling, publication)
├── scheduler/             # Publication scheduling logic
├── summarizer/            # Article summarization via Gemini
├── telegram_poster/       # Telegram channel posting
├── utils/                 # Utilities (logging configuration)
├── .github/workflows/     # GitHub Actions workflows
├── config.py              # Configuration management
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

## Logs

### In GitHub Actions

Logs are available in the GitHub interface:
1. `Actions` → select a workflow run
2. Open job `run-bot`
3. Expand step `Run bot`

On failure, logs are automatically saved as artifacts for 7 days.

### Locally

All logs are output to stdout in JSON format.

## Local Development with Docker

```bash
# Build image
docker build -t telegram-bot:local .

# Run
docker-compose up
```

## Requirements

- Python 3.12+
- PostgreSQL database
- Google Gemini API key
- Telegram bot token
- Email account with app password (for Gmail)

## License

MIT

## Author

Viacheslav Masalovich