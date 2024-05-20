from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import credentials

steam_url = "https://www.steampowered.com"
implicit_wait_time = 2

# Open browser
driver = webdriver.Chrome()

# Navigate to Steam
driver.get(steam_url)

# Navigate to login page
e = driver.find_element(by=By.LINK_TEXT, value="login")
e.click()
driver.implicitly_wait(implicit_wait_time)

# Login
e = driver.find_element(by=By.CLASS_NAME, value="_2eKVn6g5Yysx9JmutQe7WV")
e.send_keys(credentials.username)
e = driver.find_element(
    by=By.XPATH,
    value='//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/div/form/div[2]/input',
)
e.send_keys(credentials.password)
e.send_keys(Keys.ENTER)

# Load games list
games_list = open("games.txt", "r", encoding="utf8")
games = games_list.readlines()

successful_games = []
failed_games = []
games_not_reached = []
i = 0
while i < len(games):
    driver.implicitly_wait(implicit_wait_time)

    # Search for title
    game = games[i].strip()  # Remove trailing white space
    e = driver.find_element(by=By.XPATH, value='//*[@id="store_nav_search_term"]')
    e.send_keys(game)
    driver.implicitly_wait(implicit_wait_time)

    # Attempt to click on title
    try:
        e = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=game)
    except NoSuchElementException:
        failed_games.append(game)
        continue
    e.click()
    driver.implicitly_wait(implicit_wait_time)

    # Click to add game to library
    try:
        e = driver.find_element(by=By.XPATH, value='//*[@id="game_area_purchase"]/div/div[2]/div/div[3]/span')
    except NoSuchElementException:
        failed_games.append(game)
        continue
    e.click()

    # Check for confirmed success message
    expected_message = f"{game} has been added to your account.  It is now available in your Steam Library.".lower()
    try:
        e = driver.find_element(by=By.CLASS_NAME, value="newmodal_content")
    except NoSuchElementException:
        games_not_reached.append(game)
        break
    message = e.get_attribute("innerHTML")
    if message.lower().find(expected_message) < 0:
        games_not_reached.append(game)
        break

    # Click OK to exit success popup
    try:
        e = driver.find_element(by=By.CLASS_NAME, value="btn_grey_steamui")
    except NoSuchElementException:
        failed_games.append(game)
        break
    e.click()

    successful_games.append(game)
    i += 1

# Create list of games that weren't reached
while i < len(games):
    game = games[i].strip()  # Remove trailing white space
    games_not_reached.append(game)
    i += 1

results = open("results.txt", "w")
if successful_games:
    results.write("The following titles were successfully added to your library:\n")
    for game in successful_games:
        results.write(game + "\n")

if failed_games:
    results.write(
        "The following titles failed to be added to your library.\nIt is likely they were either not free or not found:\n"
    )
    for game in failed_games:
        results.write(game + "\n")
    results.write("\n")

if games_not_reached:
    results.write(
        "The following titles were not attempted.\nYou have likely reached the maximum number of titles Steam will allow you to add for now.\nTry again later:\n"
    )
    for game in successful_games:
        results.write(game + "\n")

driver.close()
