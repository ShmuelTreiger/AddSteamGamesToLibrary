from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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

for i in range(len(urls)):
    url = urls[i]
    e = driver.find_element(by=By.XPATH, value="//*[@id=\"store_nav_search_term\"]")
    e.send_keys(url)
    driver.implicitly_wait(2)

driver.close()
