# Scrapper-and-TG-bot-Test-Task

This repository contains scripts and configurations for a web scraper and a Telegram bot that work together to monitor and report scrapped (at the beginning of every hour) number of junior job vacancies. The web scraper retrieves data from a specific webpage (robota.ua website) and stores it in a database, while the Telegram bot provides a user interface to access and visualize this data.

# Installation Instructions

Before running the project, ensure you have the following installed:

- Docker
- Python 3.12 or higher

### Setup Instructions

1. **Clone the Repository:**

    ```
    git clone <repository_url>
    ```
    ```
    cd <repository_name>
    ```


2. **Environment Setup:**

    Create a `.env` file in the root directory with the following environment variable:

    ```plaintext
    TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
    ```

3. **Build Docker Image:**

    Build the Docker image using the `docker build` command:

    ```bash
    docker-compose build
    ```

4. **Run Docker Compose:**

    Use Docker Compose to start the services defined in `docker-compose.yml`:

    ```bash
    docker-compose up -d
    ```

5. **Verify Installation:**

    Check the logs to ensure everything is running correctly:

    ```bash
    docker-compose logs -f
    ```

# Running the Project

Once the installation is complete and Docker containers are running, the project automatically starts scraping job vacancies (at the beginning of every hour) and serving Telegram bot commands.

### Web Scraper (`scrapper.py`)

The `scrapper.py` script scrapes job vacancies from a specified URL using Selenium and ChromeDriver, storing the data in an SQLite database using SQLAlchemy. It runs every hour through a cron job configured in the Docker image.

### Telegram Bot (`bot.py`)

The Telegram bot @VacanciesCheckerBot (`bot.py`) provides interaction with users via commands. It retrieves today's job vacancy statistics from the database and sends the data as an Excel file upon receiving the `/get_today_statistics` command.

## Accessing Logs

Logs for both the web scraper and the Telegram bot are stored in the `log` directory within the project. You can access these logs to monitor activities and debug any issues.

## Project Structure

- **README.md**: Project documentation
- **scrapper.py**: Web scraping script

- **bot/**
  - **bot.py**: Telegram bot implementation
- **cronjobs/**: Cron job configuration file
- **database/**
  - **database_config.py**: Database configuration file
- **logs/**: Directory for log files
- **models.py**: SQLAlchemy database models
- **schemas.py**: Pydantic schemas for data validation
- **Dockerfile**: Docker configuration file
- **docker-compose.yml**: Docker Compose configuration file
- **requirements.txt**: Python dependencies



