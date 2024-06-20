import asyncio
import logging
from datetime import datetime, timezone
import xlsxwriter
import pandas as pd
import io
import os

from aiogram import Bot, Dispatcher, types  # Importing necessary modules from aiogram
from aiogram.types import BufferedInputFile  # Importing BufferedInputFile for file handling
from aiogram.filters.command import Command  # Importing Command filter for handling commands

from dotenv import load_dotenv  # Importing load_dotenv to load environment variables
load_dotenv()  # Loading environment variables from .env file

from models import Vacancies  # Importing Vacancies model from models.py
from scrapper import get_db  # Importing get_db function from scrapper.py for database access

# Enable logging to not miss important messages
logging.basicConfig(level=logging.INFO)

# Creating a bot instance using the TELEGRAM_BOT_TOKEN from environment variables
bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])

# Creating a Dispatcher instance
dp = Dispatcher()


# Handler for the /start command
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")  # Responding to the /start command with "Hello!"


# Handler for the /get_today_statistics command
@dp.message(Command("get_today_statistics"))
async def send_today_statistics(message: types.Message):
    today_date_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')  # Get current UTC date and time

    # Retrieve data from the database for today's date
    db = next(get_db())  # Open a database session
    rows = db.query(Vacancies).filter(Vacancies.datetime.like(f"{today_date_utc[:10]}%")).all()  # Query for records

    if not rows:
        await message.answer("Haven't scraped anything yet, please wait an hour")  # Send a message if no data is found for today
        return

    # Create a DataFrame and Excel file
    df = pd.DataFrame([(r.datetime, r.vacancy_count, r.change) for r in rows],
                      columns=['datetime', 'vacancy_count', 'change'])  # Create DataFrame from queried rows
    output = io.BytesIO()  # Create an in-memory binary stream
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vacancies')  # Write DataFrame to Excel sheet
        worksheet = writer.sheets['Vacancies']  # Access the worksheet object
        for idx, col in enumerate(df):  # Iterate through columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # Calculate max length of column data
                len(str(series.name))  # Calculate length of column name/header
            )) + 1  # Add some extra space
            worksheet.set_column(idx, idx, max_len)  # Set column width
        writer._save()  # Save the Excel file
    output.seek(0)  # Reset the stream position to start

    # Send the Excel file as a document
    file = BufferedInputFile(file=output.read(), filename=f'vacancies_{today_date_utc[:10]}.xlsx')
    await message.reply_document(document=file)  # Send the file as a reply


# Main function to start the bot
async def main():
    await dp.start_polling(bot)  # Starting the polling loop for the bot


if __name__ == "__main__":
    asyncio.run(main())  # Running the asyncio event loop to start the bot
