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
from PIL import Image
from io import BytesIO

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

    # logger.info("auth message located")

    wait.until(EC.presence_of_element_located((By.XPATH, LECTURE_LINK_XPATH)))

    # logger.info("lecture link located")

    wait.until(EC.visibility_of_element_located((By.XPATH, WEEK_TITLE_XPATH)))

    # logger.info("week title located")

    week_title_elm = driver.find_elements(By.XPATH, WEEK_TITLE_XPATH)[1]
    week_title = week_title_elm.text
    week_title = week_title.replace("/", "-")
    week_title = week_title.replace(":", " -")
    week_dump_list_file_path = (
        f"exports/courses/{COURSE_TITLE}/{week_num}. {week_title}"
    )
    return week_dump_list_file_path


def dump_week_intro(driver, wait, week_dump_list_file_path, week_num):
    supplement_dump_path = f"{week_dump_list_file_path}/Supplements"
    if not os.path.exists(supplement_dump_path):
        os.makedirs(supplement_dump_path)
    week_intro_dump_path = f"{supplement_dump_path}/0. Intro.md"
    if not os.path.exists(f"{week_intro_dump_path}"):
        intro_section = driver.find_element(By.CSS_SELECTOR, WEEK_INTRO_SELECTOR)
        intro_section.find_element(By.XPATH, WEEK_INTRO_BUTTON_XPATH).click()
        wait.until(
            EC.visibility_of_element_located((By.XPATH, WEEK_INTRO_OBJECTIVE_XPATH))
        )
        intro_text = intro_section.text
        with open(f"{week_intro_dump_path}", "x") as f:
            f.write(intro_text)
            # f.write(objective_text)
        logger.info(f"Week {week_num} intro dumped")


def supplement_dl(driver, wait, week_num):
    logger.info("Loading supplement page")

    week_dump_list_file_path = get_week_title_and_path(driver, wait, week_num)

    supplement_dump_path = f"{week_dump_list_file_path}_supplement.json"

    if os.path.exists(f"{supplement_dump_path}"):
        logger.info(f"Week Supplement {week_num} already dumped")
        return

    SUPPLEMENT_LINK_ELMS = driver.find_elements(By.XPATH, LECTURE_LINK_XPATH)

    logger.info(f"Len of SUPPLEMENT_LINKS elements: {len(SUPPLEMENT_LINK_ELMS)}")
    SUPPLEMENT_LINKS = [
        {
            "text": link.find_element(By.XPATH, LECTURE_NAME_XPATH).text,
            "href": link.get_attribute("href"),
        }
        for link in SUPPLEMENT_LINK_ELMS
        if "/supplement/" in link.get_attribute("href")
    ]
    logger.info(f"Len of SUPPLEMENT_LINKS href: {len(SUPPLEMENT_LINKS)}")
    with open(f"{supplement_dump_path}", "w") as f:
        json.dump(SUPPLEMENT_LINKS, f)


def download_supplements(driver, wait, week_num):
    logger.info("Downloading supplements...")
    week_dump_list_file_path = get_week_title_and_path(driver, wait, week_num)
    supplement_dir_path = f"{week_dump_list_file_path}/Supplements"
    # if path exists
    if os.path.exists(supplement_dir_path):
        files_in_directory = os.listdir(supplement_dir_path)
        if len(files_in_directory) > 1:
            logger.info(f"Supplement for {week_dump_list_file_path} already downloaded")
            return
    supplement_dumped_file = f"{week_dump_list_file_path}_supplement.json"
    with open(supplement_dumped_file, "r") as file:
        sp_dl_links = json.load(file)
    file_index = 0
    for link in sp_dl_links:
        try:
            file_index += 1

            supplement_content = ""
            logger.info(
                f"Opening supplement link{f': {link}' if LOG_LEVEL == logging.DEBUG else ''}"
            )
            driver.get(link["href"])
            time.sleep(0.2)
            wait.until(
                EC.visibility_of_element_located((By.XPATH, SUPPLEMENT_CONTENT_XPATH))
            )
            wait.until(
                EC.visibility_of_element_located((By.XPATH, SUPPLEMENT_TITLE_XPATH))
            )
            if not os.path.exists(supplement_dir_path):
                os.makedirs(supplement_dir_path)
            file_name = link["text"]
            if file_name.strip() == "":
                supplement_title_elm = driver.find_element(
                    By.XPATH, SUPPLEMENT_TITLE_XPATH
                )
                file_name = supplement_title_elm.text
            file_name = file_name.replace("/", "-")
            file_name = file_name.replace(":", " -")
            supplement_dump_path = f"{supplement_dir_path}/{file_index}. {file_name}.md"
            supplement_content_elm = driver.find_element(
                By.XPATH, SUPPLEMENT_CONTENT_XPATH
            )

            supplement_content = supplement_content_elm.text
            with open(
                supplement_dump_path,
                "x",
            ) as f:
                f.write(supplement_content)
            logger.info(f"Saved supplement page")
        except Exception:
            logger.error(
                "Error opening supplement"
                + (
                    ": " + traceback.format_exc()
                    if TESTING_MODE or LOG_LEVEL == logging.DEBUG
                    else ""
                )
            )
            continue


def course_dl(driver, wait, week_num):
    logger.info("Loading course page")

    week_dump_list_file_path = get_week_title_and_path(driver, wait, week_num)

    dump_week_intro(driver, wait, week_dump_list_file_path, week_num)

    if os.path.exists(f"{week_dump_list_file_path}.json"):
        logger.info(f"Week {week_num} already dumped")
        return

    LECTURE_LINK_ELMS = driver.find_elements(By.XPATH, LECTURE_LINK_XPATH)

    logger.info(f"Len of LECTURE_LINKS elements: {len(LECTURE_LINK_ELMS)}")

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
            time.sleep(0.2)
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
    # if path exists
    if os.path.exists(week_dump_list_file_path):
        logger.info(f"Lectures for {week_dump_list_file_path} already downloaded")
        return
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
            if not os.path.exists(f"exports/courses/{COURSE_TITLE}"):
                os.makedirs(f"exports/courses/{COURSE_TITLE}")
            if not os.path.exists(week_dump_list_file_path):
                os.makedirs(week_dump_list_file_path)
            lecture_dump_path = f"{week_dump_list_file_path}/Lectures"
            if not os.path.exists(lecture_dump_path):
                os.makedirs(lecture_dump_path)
            file_name = link["text"]
            file_name = file_name.replace("/", "-")
            file_name = file_name.replace(":", " -")
            file_extension = (
                link["href"][-3:] if "fileExtension" in link["href"] else "mp4"
            )
            if file_extension == "mp4":
                file_index += 1
            # open link using request and save to exports lectures folder
            with open(
                f"{lecture_dump_path}/{file_index}. {file_name}.{file_extension}",
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


def download_quiz(driver, wait, endpoint):
    quiz_file_path = "exports/quiz.md"
    if os.path.exists(quiz_file_path):
        logger.info(f"Quiz already downloaded")
        return
    logger.info("Downloading quiz...")
    quiz_url = f"{URL}{endpoint}"
    driver.get(quiz_url)
    wait.until(EC.visibility_of_element_located((By.XPATH, FEEDBACK_QUESTIONS_XPATH)))

    questions = driver.find_elements(By.XPATH, FEEDBACK_QUESTIONS_XPATH)
    questions_text = ""
    for i, question in enumerate(questions):
        driver.execute_script("arguments[0].scrollIntoView();", question)
        question_text = question.text
        questions_text += ("" if i == 0 else "\n") + question_text

    logger.debug(f"Quiz text: {questions_text}")

    with open(quiz_file_path, "w") as file:
        file.write(questions_text)

    logger.info("Downloaded quiz...")


def downloadQuizImages(driver, wait):
    screenshot_path = "exports/quiz.png"
    if os.path.exists(screenshot_path):
        logger.info(f"Quiz already downloaded")
        return
    logger.info("Downloading quiz...")
    quiz_url = f"{URL}{QUIZ_ENDPOINT}"
    driver.get(quiz_url)
    wait.until(EC.visibility_of_element_located((By.XPATH, FEEDBACK_QUESTIONS_XPATH)))

    questions = driver.find_elements(By.XPATH, FEEDBACK_QUESTIONS_XPATH)

    # Initialize a list to store the screenshots
    screenshots = []
    old_height = 0
    # Capture screenshots of each div element
    for div_element in questions:
        driver.execute_script("arguments[0].scrollIntoView();", div_element)
        # Get the position and size of the div element
        location = div_element.location
        size = div_element.size

        # Take a screenshot of the entire page
        screenshot = driver.get_screenshot_as_png()

        # Convert the screenshot to an Image object
        screenshot = Image.open(BytesIO(screenshot))

        # Crop the screenshot to include only the div element
        height = size["height"]
        left = location["x"]
        top = location["y"]
        right = location["x"] + size["width"]
        bottom = location["y"] + height
        cropped_screenshot = screenshot.crop(
            (left, top - old_height, right, bottom - old_height)
        )
        # old_height = height
        # Append the cropped screenshot to the list
        screenshots.append(cropped_screenshot)

    # Save or process the screenshots as needed
    for i, screenshot in enumerate(screenshots):
        ss_file_path = f"exports/screens/quiz_{i+1}.png"
        # if ss_file_path exists
        if os.path.exists(ss_file_path):
            continue
        screenshot.save(ss_file_path)

    logger.info("Downloaded quiz")


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
        if QUIZ_MODE:
            # download_quiz(_driver, _wait, QUIZ_ENDPOINT) # for quiz
            download_quiz(_driver, _wait, EXAM_ENDPOINT)  # for exam
            _driver.quit()
            return
    except Exception:
        logger.error(
            "Error downloading quiz"
            + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
        )
        _driver.quit()
        return
    try:
        if LECTURE_MODE:
            WEEK_COUNT = get_week_count(_driver, _wait)
            set_autoplay_off(_driver, _wait)
            for i in range(WEEK_COUNT):
                if i == 1 and TESTING_MODE:
                    _driver.quit()
                    return
                logger.info(f"Week {i + 1}")
                try:
                    supplement_dl(_driver, _wait, i + 1)
                    course_dl(_driver, _wait, i + 1)
                    download_lectures(_driver, _wait, i + 1)
                    download_supplements(_driver, _wait, i + 1)
                except Exception:
                    logger.error(
                        "Error downloading course"
                        + (
                            ": " + traceback.format_exc()
                            if TESTING_MODE or LOG_LEVEL == logging.DEBUG
                            else ""
                        )
                    )
                    _driver.quit()
                    return
        else:
            _driver.quit()
            return
    except Exception:
        logger.error(
            "Error getting week"
            + (": " + traceback.format_exc() if LOG_LEVEL == logging.DEBUG else "")
        )

    _driver.quit()


if __name__ == "__main__":
    LOG_LEVEL = logging.INFO
    logger.setLevel(LOG_LEVEL)
    init_file_logger(__file__, LOG_LEVEL)
    console_handler.setLevel(LOG_LEVEL)
    main()
