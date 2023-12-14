from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time

# Read stock data from JSON file
with open("list_stocks.json", "r") as file:
    stocks_data = json.load(file)

# Create an empty list to store post links
post_links = []

# Configure Chrome options
chrome_options = ChromeOptions()
# Run Chrome in headless mode (no GUI)  
chrome_options.add_argument("--headless=new")

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

def f247():
    for symbol in stocks_data:
        print(symbol)
        driver = webdriver.Chrome(service=ChromeService("./chromedriver.exe"), options=chrome_options)
        url = f"https://f247.com/tag/{symbol}"
        driver.get(url)
        time.sleep(2)
        max_scroll_iterations = 10

        scroll_iterations = 0
        wait = WebDriverWait(driver, 10)
        try:
            searchs = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
        except TimeoutException:
            print("Timeout: 't-body' element not found. Exiting function.")
            continue

        while True:
            scroll_iterations += 1
            page_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_page_height = driver.execute_script("return document.body.scrollHeight")
            if new_page_height == page_height or scroll_iterations > max_scroll_iterations:
                break

        post_child = searchs.find_elements(By.CLASS_NAME, "raw-topic-link")
        for link in post_child:
            href = link.get_attribute("href")
            print(href)
            # Append the link to the list
            post_links.append(href)
            # Write the list of links to a JSON file
            with open("post_links.json", "w", encoding="utf-8") as json_file:
                json.dump(post_links, json_file, indent=2)

        driver.close()

# Call the function
f247()