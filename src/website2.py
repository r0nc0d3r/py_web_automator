# import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from vars.website2 import *
import time
import logging
import traceback
import pandas as pd
from datetime import datetime
import os

LOG_LEVEL = logging.INFO

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Create a formatter for log messages
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a file handler
file_handler = logging.FileHandler("app.log", mode="w")
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)  # Set the desired console log level
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_dump_file_name(is_team):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d")
    match_name = MATCH_SLUG.replace("-", "_").lower()
    tour_name = TOUR_SLUG.replace("-", "_").lower()
    file_prefix = "team" if is_team else "squad"
    if not os.path.exists("exports"):
        os.makedirs("exports")
    file_path = os.path.join("exports", tour_name)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    return os.path.join(file_path, f"{file_prefix}_{formatted_time}_{match_name}.csv")


# future: optimize force_overwrite logic by skip processig if file exists
def dump_squad(drv, w8, force_overwrite):
    logger.debug("Dumping squad...")
    drv.get(f"https://www.{DOMAIN}{SQUAD_ENDPOINT}")
    # time.sleep(2)
    w8.until(EC.presence_of_element_located((By.XPATH, players_list_xpath)))
    logger.debug("Squad found...")
    columns = ["Name", "Type", "Team", "Link"]
    df = pd.DataFrame(columns=columns)
    list_df = []
    # time.sleep(1)
    teams = drv.find_elements(By.CSS_SELECTOR, team_name_selector)
    team_a = teams[0].text
    team_b = teams[1].text
    # list_xpath = bench_players_list_xpath if is_bench else players_list_xpath
    list_xpath = players_list_xpath
    player_links = drv.find_elements(By.XPATH, list_xpath)
    logger.debug("Iterating players...")
    for index, _ in enumerate(player_links):
        player_team = team_a if index % 2 == 0 else team_b
        player_links = w8.until(
            lambda driver: driver.find_elements(By.XPATH, list_xpath)
        )
        logger.debug("Getting player link")
        player_link = player_links[index].get_attribute("href")
        logger.debug("Getting player name...")
        player_name = player_links[index].find_element(By.XPATH, player_name_xpath).text
        logger.debug("Getting player type...")
        player_type = player_links[index].find_element(By.XPATH, player_type_xpath).text
        new_player = {
            "Name": player_name,
            "Type": player_type,
            "Team": player_team,
            "Link": player_link,
        }
        list_df.append(new_player)
        logger.info(new_player)
    len_list = len(list_df)
    logger.debug(("Length of list:", len_list))
    if len_list > 0:
        csv_file_name = get_dump_file_name(False)
        df = pd.DataFrame.from_dict(list_df)
        try:
            df.to_csv(csv_file_name, index=False, mode="w" if force_overwrite else "x")
        except FileExistsError:
            logger.debug("Squad file exists, skipping dump")


# future: optimize force_overwrite logic by skip processig if file exists
def dump_team(drv, w8, force_overwrite):
    logger.debug("Dumping team...")
    columns = ["Name"]
    df = pd.DataFrame(columns=columns)
    list_df = []
    # time.sleep(1)
    drv.get(f"https://www.{DOMAIN}{TEAM_ENDPOINT}")
    w8.until(EC.presence_of_element_located((By.CSS_SELECTOR, ground_selector)))
    logger.debug("Team found...")
    players = drv.find_elements(By.CSS_SELECTOR, player_selected_selector)
    logger.debug("Iterating players...")
    for player in players:
        if len(list_df) == 11:
            list_df.append({"Name": "-------"})
        drv.execute_script("arguments[0].scrollIntoView();", player)
        w8.until(EC.visibility_of(player))
        player_name = player.text
        if player_name == "C" or player_name == "VC":
            list_df[-1] = {"Name": list_df[-1]["Name"] + " (" + player_name + ")"}
        else:
            new_player = {"Name": player_name}
            list_df.append(new_player)

        logger.info(new_player)

    len_list = len(list_df)
    logger.debug(("Number of players:", len_list))
    if len_list > 0:
        csv_file_name = get_dump_file_name(True)
        df = pd.DataFrame.from_dict(list_df)
        try:
            df.to_csv(csv_file_name, index=False, mode="w" if force_overwrite else "x")
        except FileExistsError:
            logger.debug("Team file exists, skipping dump")


def main():
    options = webdriver.ChromeOptions()

    options.add_argument("--ignore-certificate-errors")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 5000)

    try:
        dump_squad(driver, wait, False)
    except Exception:
        logger.error(
            "Error dumping squad"
            + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
        )

    try:
        dump_team(driver, wait, False)
    except Exception:
        logger.error(
            "Error dumping team"
            + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
        )

    logger.debug("Initiating sleep...")

    # time.sleep(600)

    driver.close()


if __name__ == "__main__":
    LOG_LEVEL = logging.INFO
    logger.setLevel(LOG_LEVEL)
    file_handler.setLevel(LOG_LEVEL)
    console_handler.setLevel(LOG_LEVEL)
    main()
