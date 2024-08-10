import os
import pickle
import json
import logging
from time import sleep
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from db_setup import SessionLocal
from db import save_comments_to_db
from logging_config import setup_logging

# Set up logging
setup_logging()

class InstagramCommentScraper:
    def __init__(self):
        """Initialize environment variables and the browser."""
        load_dotenv()
        
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.query_hash = os.getenv('QUERY_HASH')
        self.main_url = "https://www.instagram.com/"
        self.cookies_file = 'cookies.pkl'
        
        self.browser = self._initialize_browser()
        self._load_cookies()
        self.db = SessionLocal()

    def _initialize_browser(self):
        """Initialize the Chrome browser in headless mode."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        
        logging.info('Browser initialized in headless mode.')
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )

    def _load_cookies(self):
        """Load cookies from file if available, otherwise log in."""
        if os.path.exists(self.cookies_file):
            self.browser.get(self.main_url)
            with open(self.cookies_file, 'rb') as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.browser.add_cookie(cookie)
            self.browser.refresh()
            logging.info('Cookies loaded successfully.')
        else:
            self.sign_in()

    def save_cookies(self):
        """Save cookies to a file."""
        with open(self.cookies_file, 'wb') as file:
            pickle.dump(self.browser.get_cookies(), file)
        logging.info('Cookies saved successfully.')

    def sign_in(self):
        """Log in to Instagram."""
        self.browser.get(f"{self.main_url}accounts/login/")
        
        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(self.username)
        
        password_entry = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_entry.send_keys(self.password, Keys.ENTER)
        
        sleep(10)

        self.save_cookies()
        logging.info('Logged in to Instagram.')

    def get_comments(self, shortcode, number_of_comments):
        """Fetch comments from a post using its shortcode."""
        logging.info(f'Fetching comments for shortcode: {shortcode}')
        comment_url = self._build_comment_url(shortcode, number_of_comments)
        comment_data = self._fetch_comment_data(comment_url)
        extracted_data = self._extract_comment_data(comment_data)
        if extracted_data:
            logging.info(f'Successfully fetched comments for shortcode: {shortcode}')
            save_comments_to_db(shortcode, extracted_data)
            return extracted_data
        logging.error(f'Failed to fetch comments for shortcode: {shortcode}')
        return None

    def _build_comment_url(self, shortcode, number_of_comments):
        """Build the URL to fetch comments."""
        comment_url_variables = {"shortcode": shortcode, "first": number_of_comments}
        comment_url_variables_json = json.dumps(comment_url_variables)
        return 'view-source:https://www.instagram.com/graphql/query/?query_hash={}&variables={}'.format(self.query_hash, comment_url_variables_json)

    def _fetch_comment_data(self, comment_url):
        """Fetch the comment data from the URL."""
        self.browser.get(comment_url)
        sleep(3)  # Allow time for page to load
        logging.info('Fetched page source for comments.')
        return self.browser.page_source

    def _extract_comment_data(self, comment_data):
        """Extract comment data from the page source."""
        try:
            soup = bs(comment_data, 'html.parser')
            comment_json = soup.find('td', class_='line-content').text.strip()
            return json.loads(comment_json)
        except Exception as e:
            logging.error(f"Error extracting comment data: {e}")
            return None

    def close_browser(self):
        """Close the browser."""
        self.browser.quit()
        logging.info('Browser closed.')

    @staticmethod
    def extract_shortcode_from_url(url):
        """Extract the shortcode from an Instagram URL."""
        try:
            return url.split('/')[4]
        except IndexError:
            logging.error("Invalid Instagram URL.")
            return None