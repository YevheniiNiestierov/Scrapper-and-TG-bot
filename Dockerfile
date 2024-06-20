# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.12

# Set environment variables to optimize Python's behavior in Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Add Google Chrome repository and install stable version
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update -qqy --no-install-recommends \
    && apt-get install -qqy --no-install-recommends google-chrome-stable

# Install cron and other necessary packages
RUN apt-get update && apt-get install -y cron

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the working directory in the container
COPY . .

# Install Python dependencies from requirements.txt without caching to keep the image clean
RUN pip install --no-cache-dir -r requirements.txt

# Add cron job file to /etc/cron.d/ directory
COPY cronjobs /etc/cron.d/vacancy_scrapper

# Set permissions for the cron job file
RUN chmod 0644 /etc/cron.d/vacancy_scrapper

# Install the cron job
RUN crontab /etc/cron.d/vacancy_scrapper

# Create a log file for cron jobs
RUN touch /var/log/cron.log

# Run cron to execute scheduled tasks, run the bot, and tail the cron log to keep the container running
CMD cron && python3 -m bot.bot && tail -f /var/log/cron.log
