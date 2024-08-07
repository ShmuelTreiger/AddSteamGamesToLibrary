import logging
from configparser import ConfigParser

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import credentials

steam_url = "https://www.steampowered.com"

username = credentials.username
if not username:
    raise Exception("You must write your username into credentials.py.")

password = credentials.password
if not password:
    raise Exception("You must write your password into credentials.py.")

config = ConfigParser()
config.read("config.ini")

implicit_wait_time = config.getint(section="General", option="implicit_wait_time")

# Initiate logging to standard out if setting in config.ini is true
log_to_std_out = config.getboolean(section="General", option="log_to_std_out")
if log_to_std_out:
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().setLevel(logging.INFO)

# Load games list
games_list = open("games.txt", "r", encoding="utf8")
games = games_list.readlines()

# Open browser
driver = webdriver.Chrome()

# Navigate to Steam
driver.get(steam_url)

# Navigate to login page
e = driver.find_element(by=By.LINK_TEXT, value="login")
e.click()
driver.implicitly_wait(implicit_wait_time)

# Login
e = driver.find_element(by=By.CLASS_NAME, value="_2GBWeup5cttgbTw8FM3tfx")
e.send_keys(username)
e = driver.find_element(
    by=By.XPATH,
    value='//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/div/form/div[2]/input',
)
e.send_keys(password)
e.send_keys(Keys.ENTER)

# TODO: Check for successful login

successful_games = []
games_already_in_library = []
games_cost_money = []
games_not_found = []
failed_games = []
early_access_games = []
game_demos = []
games_not_reached = []
i = 0
while i < len(games):
    driver.implicitly_wait(implicit_wait_time)

    # Search for title
    game = games[i].strip()  # Remove trailing white space
    logging.info(f"Attempting to add '{game}' to your Steam library.")
    e = driver.find_element(by=By.XPATH, value='//*[@id="store_nav_search_term"]')
    e.clear()
    e.send_keys(game)
    driver.implicitly_wait(implicit_wait_time)

    # Attempt to click on title
    try:
        e = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=game)
    except NoSuchElementException:
        logging.info(f"'{game}' not found.")
        games_not_found.append(game)
        i += 1
        e.clear()
        continue
    e.click()
    driver.implicitly_wait(implicit_wait_time)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    all_text = soup.get_text()

    # Check if game already in library
    message = f"{game} is already in your Steam library"
    if all_text.find(message) >= 0:
        logging.info(f"'{game}' already in your Steam Library.")
        games_already_in_library.append(game)
        i += 1
        continue

    # Check if game costs money
    if all_text.lower().find(f"buy {game.lower()}") >= 0:
        logging.info(f"'{game}' costs money.")
        games_cost_money.append(game)
        i += 1
        continue

    # Skip early access games if option is true
    skip_early_access_games = config.getboolean(section="General", option="skip_early_access_games")
    if skip_early_access_games:
        if all_text.find("Early Access Game") >= 0:
            logging.info(f"'{game}' is an early access game.")
            early_access_games.append(game)
            i += 1
            continue

    # Skip game demos if option is true
    skip_game_demos = config.getboolean(section="General", option="skip_game_demos")
    if skip_game_demos:
        if all_text.find(f"Download {game} Demo") >= 0:
            logging.info(f"'{game}' is a demo.")
            game_demos.append(game)
            i += 1
            continue

    # Click to add game to library
    try:
        e = driver.find_element(by=By.XPATH, value='//*[@id="game_area_purchase"]/div/div[2]/div/div[3]/span')
    except NoSuchElementException:
        logging.info(f"'{game}' failed to be added to your account.")
        failed_games.append(game)
        i += 1
        continue
    e.click()
    driver.implicitly_wait(implicit_wait_time)

    # Check for success message
    try:
        e = driver.find_element(by=By.CLASS_NAME, value="newmodal_content")
    except NoSuchElementException:
        logging.info(
            f"For an unknown reason, confirmation popup not found after attempting to add '{game}' to your library."
        )
        failed_games.append(game)
        i += 1
        continue
    message = e.get_attribute("innerHTML")
    message_lower = message.lower()
    failure_message = "There was a problem adding this product to your account.  Please try again later.".lower()
    if message_lower.find(failure_message) >= 0:
        logging.info(
            f"Failure message found after attempting to add '{game}'. You have likely surpassed Steam's rate limiting. Exiting program. Please wait and try again."
        )
        games_not_reached.append(game)
        i += 1
        break

    expected_message = "has been added to your account.  It is now available in your Steam Library.".lower()
    if message_lower.find(expected_message) < 0:
        logging.info(f"Unknown message found after attempting to add '{game}' to your account.")
        logging.info(f"Message found instead: {message}")
        failed_games.append(game)
        i += 1
        break

    # Click OK to exit success popup
    try:
        e = driver.find_element(by=By.CLASS_NAME, value="btn_grey_steamui")
    except NoSuchElementException:
        logging.info(f"'{game}' failed to be added to your account for an unknown reason.")
        failed_games.append(game)
        i += 1
        break
    e.click()
    driver.implicitly_wait(implicit_wait_time)

    successful_games.append(game)
    logging.info(f"{game} was successfully added to your account.")
    i += 1

driver.close()

# Create list of games that weren't reached
while i < len(games):
    game = games[i].strip()  # Remove trailing white space
    games_not_reached.append(game)
    i += 1

# Print results to 'results.txt' file
results = open("results.txt", "w", encoding="utf8")
if successful_games:
    results.write("The following titles were successfully added to your library:\n")
    for game in successful_games:
        results.write(game + "\n")
    results.write("\n")

if games_already_in_library:
    results.write("The following titles are already in your library:\n")
    for game in games_already_in_library:
        results.write(game + "\n")
    results.write("\n")

if games_cost_money:
    results.write("The following titles are not free.\n")
    results.write("It is possible that there are two games with the same title, so it may be worth double checking:\n")
    for game in games_cost_money:
        results.write(game + "\n")
    results.write("\n")

if games_not_found:
    results.write("The following titles were not found on steam.\n")
    results.write("This may be an error, so it may be worth double checking:\n")
    for game in games_not_found:
        results.write(game + "\n")
    results.write("\n")

if failed_games:
    results.write("The following titles failed to be added to your library for unknown reasons.\n")
    results.write("It is probably worth double checking these titles:\n")
    for game in failed_games:
        results.write(game + "\n")
    results.write("\n")

if early_access_games:
    results.write("The following early access games were skipped.\n")
    results.write("To add them to your account, change the setting in config.ini:\n")
    for game in early_access_games:
        results.write(game + "\n")
    results.write("\n")

if game_demos:
    results.write("The following game demos were skipped.\n")
    results.write("To add them to your account, change the setting in config.ini:\n")
    for game in game_demos:
        results.write(game + "\n")
    results.write("\n")

if games_not_reached:
    results.write("The following titles were not attempted to add to your account.\n")
    results.write("You have likely reached the maximum number of titles Steam will allow you to add for now.\n")
    results.write("Try again later:\n")
    for game in games_not_reached:
        results.write(game + "\n")
