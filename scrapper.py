import ssl
import logging
import undetected_chromedriver as uc

from datetime import datetime, timezone

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session
from webdriver_manager.chrome import ChromeDriverManager

from models import Vacancies  # Importing SQLAlchemy model
from database.database_config import SessionLocal, engine, Base  # Importing database configuration

logging.basicConfig(filename='/var/log/cron.log', level=logging.INFO)

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Target URL to scrape
target_url = 'https://robota.ua/ru/zapros/junior/ukraine'

# WebDriver optimized settings
options = uc.ChromeOptions()
options.add_argument('--no-sandbox') # Disable sandbox mode to avoid issues in Docker
options.add_argument('--disable-dev-shm-usage') # Disable /dev/shm usage to prevent shared memory issues, also for Docker
options.headless = True  # Run in headless mode

# Create database tables if not exists
Base.metadata.create_all(bind=engine)


# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to check if the page has loaded
def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'


# Function to scrape the number of vacancies
def scrap_vacancies_number():
    chrome_service = Service(ChromeDriverManager().install())
    driver = uc.Chrome(options=options, service=chrome_service)
    driver.get(target_url)  # Open the target page

    # Wait for the element with vacancies count
    wait = WebDriverWait(driver, 10)
    for attempt in range(10):
        logging.info(f'Attempt {attempt + 1}, ')
        if page_has_loaded(driver):
            logging.info('Page has loaded')
            break
    vacancies_element = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//main/section/div/div/lib-desktop-top-info/div/div/div')
    ))

    # Extract and process the number of vacancies
    vacancies_number_str = vacancies_element.text
    vacancies_number_int = int(''.join(filter(str.isdigit, vacancies_number_str)))

    # Close WebDriver
    driver.quit()

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    with next(get_db()) as db:
        change = get_previous_vacancy_count_from_db(db, vacancies_number_int)

        # Save vacancy record in the database
        db_vacancy_record = Vacancies(datetime=timestamp, vacancy_count=vacancies_number_int, change=change)
        db.add(db_vacancy_record)
        db.commit()
        logging.info(f'Record added to database, time {datetime.now(timezone.utc)}')


# Function to get the previous vacancy count from the database
def get_previous_vacancy_count_from_db(db: Session, current_vacancies_count: int) -> int:
    last_record = db.query(Vacancies).order_by(Vacancies.datetime.desc()).first()
    if last_record:
        return current_vacancies_count - last_record.vacancy_count
    else:
        return 0


# Main execution block
if __name__ == '__main__':
    scrap_vacancies_number()
