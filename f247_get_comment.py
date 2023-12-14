from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
import time

# Configure Chrome options
chrome_options = ChromeOptions()
# Run Chrome in headless mode (no GUI)
# chrome_options.add_argument("--headless=new")

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Read post links from JSON file
with open("post_links.json", "r", encoding="utf-8") as json_file:
    post_links = json.load(json_file)

# Set up the Chrome web driver
driver = webdriver.Chrome(service=ChromeService("./chromedriver.exe"), options=chrome_options)
stock_error = []

def get_comment(url):
    print(url)
    driver = webdriver.Chrome(service=ChromeService("./chromedriver.exe"), options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    try:
        intro_post = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'title-wrapper')))
        searchs = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'post-stream')))
    except TimeoutException:
        print(f"Timeout: Unable to load elements for URL {url}. Skipping.")
        return

    general_post = {
        "user_post": intro_post.find_element(By.CLASS_NAME, "username").text,
        "post_title": intro_post.find_element(By.CLASS_NAME, "fancy-title").text.encode().decode('utf-8'),
        "content_post": intro_post.find_element(By.CLASS_NAME, 'cooked').text.encode().decode('utf-8'),
        "comments": [],
    }

    post = searchs.find_element(By.ID, f"post_1")
    data_post = {
        "user_post": post.find_element(By.CLASS_NAME, "username").text,
        "content_post": post.find_element(By.CLASS_NAME, 'cooked').text.encode().decode('utf-8')
    }

    current_i = 2

    while True:
        for _ in range(2, 20):
            try:
                comment = searchs.find_element(By.ID, f"post_{current_i}")
                comment_data = {
                    "user_comment": comment.find_element(By.CLASS_NAME, "username").text,
                    "content_comment": comment.find_element(By.CLASS_NAME, 'cooked').text.encode().decode('utf-8'),
                }

                general_post["comments"].append(comment_data)
                print("comment " + str(current_i))
                current_i += 1
            except NoSuchElementException:
                print(f"Element with ID 'post_{current_i}' not found. Skipping.")
                current_i += 1

        page_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_page_height = driver.execute_script("return document.body.scrollHeight")
        if new_page_height == page_height:
            break

    general_post["comments"].reverse()

    # Store data in a JSON file named after the post title
    json_filename = f"{general_post['post_title'].replace('/', '_').replace(' ', '_')}_data.json"
    with open("data_stock_f247.json", mode="w", encoding="utf-8") as json_file:
        json.dump([general_post], json_file, indent=2)

# Loop through post links and call get_comment function
for url in post_links:
    get_comment(url)

driver.quit()
