import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from vars.website1 import *

URL = f"https://{DOMAIN}"

options = webdriver.ChromeOptions()

options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(options=options)

timeout = 2

wait = WebDriverWait(driver, timeout)

actions = ActionChains(driver)

driver.get(URL)

cookies = pickle.load(open("PICKLE_FILE", "rb"))

for cookie in cookies:
    cookie["domain"] = DOMAIN

    try:
        driver.add_cookie(cookie)
    except Exception as e:
        pass

file_path = f"{TECH}_mdl_list.txt"

dl_btn_id = "#__next > div.flex.flex-col.min-h-screen > div > div:nth-child(1) > div > div.relative.before\:float-left.after\:clear-both.after\:table.col-span-9 > div > div > div.cueplayer-react-controls-holder > div.cueplayer-react-control-bar > div.cueplayer-react-control-bar-right-part > button.flex.items-center.justify-center.w-10.h-10.text-white.border-none"

with open(file_path, "r") as file:
    for line in file:
        url = line.strip()
        driver.get(f"{url}")
        wait.until(EC.presence_of_element_located((By.XPATH, auth_welcome_xpath)))
        wait.until(EC.presence_of_element_located((By.XPATH, vids_xpath)))
        vid_links = driver.find_elements(By.XPATH, vids_xpath)
        for index, val in enumerate(vid_links):
            vid_links = wait.until(
                lambda driver: driver.find_elements(By.XPATH, vids_xpath)
            )
            actions.move_to_element(vid_links[index]).perform()
            href = vid_links[index].get_attribute("href")
            course_name = vid_links[index].text
            vid_links[index].click()  # 1
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, dl_btn_xpath)))
                time.sleep(timeout)
                wait.until(
                    lambda driver: driver.find_element(By.XPATH, dl_btn_xpath)
                ).click()
            except Exception as e:
                print("err", e)
                wait.until(EC.element_to_be_clickable((By.ID, dl_btn_id)))
                time.sleep(60)
                wait.until(lambda driver: driver.find_element(By.ID, dl_btn_id)).click()
            time.sleep(timeout)
            driver.back()


time.sleep(60)

driver.close()
