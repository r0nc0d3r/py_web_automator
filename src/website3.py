import requests

# Import selenium dependencies
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
from vars.website3 import *
import time
import traceback
# import pandas as pd
# from datetime import datetime
import os
import logging
from common.logger import *
import json

LOG_LEVEL = logging.INFO


def dump_cookie(driver, wait):
    # return if COOKIES_FILE exists
    if os.path.exists(COOKIES_FILE):
        logger.info("Cookies file exists")
        return

    logger.info("Dumping cookies")

    driver.get(f"{URL}/{LOGIN_ENDPOINT}")

    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_LINK_XPATH)))

    LOGIN_LINK = driver.find_element(By.XPATH, LOGIN_LINK_XPATH)

    LOGIN_LINK.click()

    wait.until(EC.visibility_of_element_located((By.XPATH, EMAIL_TXT_XPATH)))

    EMAIL_TXT = driver.find_element(By.XPATH, EMAIL_TXT_XPATH)

    EMAIL_TXT.send_keys(LOGIN_USEREMAIL)

    PASSWORD_TXT = driver.find_element(By.XPATH, PASSWORD_TXT_XPATH)

    PASSWORD_TXT.send_keys(LOGIN_PASSWORD)

    LOGIN_BTN = driver.find_element(By.XPATH, LOGIN_BTN_XPATH)

    LOGIN_BTN.click()

    wait.until(EC.visibility_of_element_located((By.XPATH, AUTH_MSG_XPATH)))

    # Get cookies
    cookies = driver.get_cookies()

    # Write cookies to file
    with open(COOKIES_FILE, "w") as f:
        f.write(json.dumps(cookies))

    logger.info("Dumped cookies")


def load_cookie(driver, wait):
    # return if COOKIES_FILE doesn't exists
    if not os.path.exists(COOKIES_FILE):
        logger.info("Cookies file doesn't exists")
        return

    logger.info("Loading cookies")

    driver.get(URL)

    # read cookies from COOKIES_FILE and add to driver
    with open(COOKIES_FILE, "r") as f:
        cookies = json.loads(f.read())
        for cookie in cookies:
            cookie["domain"] = DOMAIN

            try:
                driver.add_cookie(cookie)
            except Exception:
                logger.error(
                    "Error adding cookie"
                    + (
                        ": " + traceback.format_exc()
                        if LOG_LEVEL == logging.DEBUG
                        else ""
                    )
                )
                continue

    logger.info("Loaded cookies")


def get_week_count(driver, wait):
    logger.info("Loading week count page")

    driver.get(f"{URL}/{COURSE_ENDPOINT}")

    wait.until(EC.visibility_of_element_located((By.XPATH, WEEK_COUNT_XPATH)))

    WEEK_COUNT = len(driver.find_elements(By.XPATH, WEEK_COUNT_XPATH))

    logger.info(f"Week count: {WEEK_COUNT}")

    return int(WEEK_COUNT)


def get_week_title_and_path(driver, wait, week_num):
    logger.info(f"Loading week {week_num} page")

    driver.get(f"{URL}/{COURSE_WITHOUT_WEEK_ENDPOINT}{week_num}")

    wait.until(EC.visibility_of_element_located((By.XPATH, AUTH_MSG_XPATH)))

    wait.until(EC.visibility_of_element_located((By.XPATH, LECTURE_LINK_XPATH)))

    wait.until(EC.visibility_of_element_located((By.XPATH, WEEK_TITLE_XPATH)))

    week_title_elm = driver.find_elements(By.XPATH, WEEK_TITLE_XPATH)[1]
    week_title = week_title_elm.text
    week_title = week_title.replace("/", "-")
    week_title = week_title.replace(":", " -")
    week_dump_list_file_path = f"exports/lectures/{week_num}. {week_title}"
    return week_dump_list_file_path


def course_dl(driver, wait, week_num):
    logger.info("Loading course page")

    week_dump_list_file_path = get_week_title_and_path(driver, wait, week_num)

    # return from function if week_dump_list_file_path exists
    if os.path.exists(f"{week_dump_list_file_path}.json"):
        logger.info(f"Week {week_num} already dumped")
        return

    # find elements with LECTURE_LINK_XPATH and get its href in list
    LECTURE_LINK_ELMS = driver.find_elements(By.XPATH, LECTURE_LINK_XPATH)

    logger.info(f"Len of LECTURE_LINKS elements: {len(LECTURE_LINK_ELMS)}")

    # get links href
    LECTURE_LINKS = [
        {
            "text": link.find_element(By.XPATH, LECTURE_NAME_XPATH).text,
            "href": link.get_attribute("href"),
        }
        for link in LECTURE_LINK_ELMS
        if "/lecture/" in link.get_attribute("href")
    ]

    logger.info(f"Len of LECTURE_LINKS href: {len(LECTURE_LINKS)}")

    dl_links = []

    # loop over LECTURE_LINKS and run driver.get with each value
    for link in LECTURE_LINKS:
        try:
            logger.info(
                f"Opening lecture for downloading{f': {link}' if LOG_LEVEL == logging.DEBUG else ''}"
            )
            driver.get(link["href"])
            time.sleep(1)
            wait.until(
                EC.visibility_of_element_located((By.XPATH, LECTURE_DL_BTN_XPATH))
            )
            LECTURE_DL_BTN = driver.find_element(By.XPATH, LECTURE_DL_BTN_XPATH)
            logger.info(f"Found download button")
            driver.execute_script("arguments[0].scrollIntoView();", LECTURE_DL_BTN)
            LECTURE_DL_BTN.find_element(By.XPATH, "..").click()
            logger.info(f"Clicked on download button")

            wait.until(
                EC.visibility_of_element_located((By.XPATH, LECTURE_DL_LINK_XPATH))
            )
            logger.info(f"Found download link")

            DL_LINK_ELMS = driver.find_elements(By.XPATH, LECTURE_DL_LINK_XPATH)
            # filter DL_LINK_ELMS with only links that contains text '(720p)'
            DL_LINKS = [
                link.get_attribute("href")
                for link in DL_LINK_ELMS
                if "(720p)" in link.text
            ]
            logger.info(f"Len of DL_LINKS href: {len(DL_LINKS)}")
            # append to dl_links only first value
            dl_links.append({"text": link["text"], "href": DL_LINKS[0]})

            DL_SUB_ELMS = driver.find_elements(By.XPATH, LECTURE_DL_SUB_XPATH)
            DL_SUB_LINKS = [link.get_attribute("href") for link in DL_SUB_ELMS]
            logger.info(f"Len of DL_SUB_LINKS href: {len(DL_SUB_LINKS)}")
            # dl_links.append(DL_SUB_LINKS)
            dl_links.append({"text": link["text"], "href": DL_SUB_LINKS[0]})
            dl_links.append({"text": link["text"], "href": DL_SUB_LINKS[1]})
            logger.info(f"Download links added")

        except Exception:
            logger.error(
                "Error opening lecture"
                + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
            )
            continue
    # save dl_links list of dictionary to txt file to load it later
    # Serialize the list to JSON and write it to the file
    with open(f"{week_dump_list_file_path}.json", "w") as file:
        json.dump(dl_links, file)


def download_lectures(driver, wait, week_num):
    logger.info("Downloading lectures...")
    week_dump_list_file_path = get_week_title_and_path(driver, wait, week_num)
    with open(f"{week_dump_list_file_path}.json", "r") as file:
        dl_links = json.load(file)
    file_index = 0
    for link in dl_links:
        try:
            logger.info(
                f"Opening download link{f': {link}' if LOG_LEVEL == logging.DEBUG else ''}"
            )
            if not os.path.exists("exports"):
                os.makedirs("exports")
            if not os.path.exists("exports/lectures"):
                os.makedirs("exports/lectures")
            if not os.path.exists(week_dump_list_file_path):
                os.makedirs(week_dump_list_file_path)
            file_name = link["text"]
            file_name = file_name.replace("/", "-")
            file_name = file_name.replace(":", " -")
            file_extension = (
                link["href"][-3:] if "fileExtension" in link["href"] else "mp4"
            )
            if file_extension == "mp4":
                file_index += 1
            # open link using request and save to exports/lectures folder
            with open(
                f"{week_dump_list_file_path}/{file_index}. {file_name}.{file_extension}",
                "xb",
            ) as f:
                f.write(requests.get(link["href"]).content)
            logger.info(f"Saved download link")
        except Exception:
            logger.error(
                "Error opening download link"
                + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
            )
            continue
    logger.info("Downloaded course page")


def set_autoplay_off(driver, wait):
    logger.info("Setting local storage")

    driver.get(f"{URL}/{COURSE_ENDPOINT}")

    wait.until(EC.visibility_of_element_located((By.XPATH, WEEK_COUNT_XPATH)))
    driver.execute_script(SET_LOCAL_STORAGE)
    driver.refresh()
    logger.info("Local storage set")


def main():
    options = webdriver.ChromeOptions()

    options.add_argument("--ignore-certificate-errors")

    _driver = webdriver.Chrome(options=options)

    _wait = WebDriverWait(_driver, 5000)

    try:
        dump_cookie(_driver, _wait)
    except Exception:
        logger.error(
            "Error dumping cookie"
            + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
        )

    try:
        load_cookie(_driver, _wait)
    except Exception:
        logger.error(
            "Error loading cookie"
            + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
        )
    try:
        WEEK_COUNT = get_week_count(_driver, _wait)
        set_autoplay_off(_driver, _wait)
        logger.info("Week count: " + str(WEEK_COUNT))
        for i in range(WEEK_COUNT):
            logger.info(f"Week {i + 1}")
            try:
                course_dl(_driver, _wait, i + 1)
                download_lectures(_driver, _wait, i + 1)
            except Exception:
                logger.error(
                    "Error downloading course"
                    + (
                        ": " + traceback.format_exc()
                        if LOG_LEVEL == logging.INFO
                        else ""
                    )
                )
    except Exception:
        logger.error(
            "Error getting week"
            + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
        )


if __name__ == "__main__":
    LOG_LEVEL = logging.INFO
    logger.setLevel(LOG_LEVEL)
    init_file_logger(__file__, LOG_LEVEL)
    console_handler.setLevel(LOG_LEVEL)
    main()