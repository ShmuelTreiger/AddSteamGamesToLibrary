from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import credentials

steam_url = "https://www.steampowered.com"

# Open browser
driver = webdriver.Chrome()

# Navigate to Steam
driver.get(steam_url)

# Navigate to login page
e = driver.find_element(by=By.LINK_TEXT, value="login")
e.click()
driver.implicitly_wait(1)

# Login
e = driver.find_element(by=By.CLASS_NAME, value="_2eKVn6g5Yysx9JmutQe7WV")
e.send_keys(credentials.username)
e = driver.find_element(by=By.XPATH, value="//*[@id=\"responsive_page_template_content\"]/div[3]/div[1]/div/div/div/div[2]/div/form/div[2]/input")
e.send_keys(credentials.password)
e.send_keys(Keys.ENTER)

driver.implicitly_wait(3)

# Load url list
url_list = open("urls.txt", "r", encoding="utf8")
urls = url_list.readlines()

failed_urls = []
for i in range(len(urls)):
    # Search for title
    url = urls[i].strip()  # Remove trailing white space
    e = driver.find_element(by=By.XPATH, value="//*[@id=\"store_nav_search_term\"]")
    e.send_keys(url)
    driver.implicitly_wait(1)

    # Attempt to click on title
    try:
        e = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=url)
    except NoSuchElementException:
        failed_urls.append(url)
        continue
    e.click()
    driver.implicitly_wait(2)

results = open("results.txt", "w")
results.write("The following titles failed to be added to your account:\n")
for url in failed_urls:
    results.write(url + "\n")

driver.close()
