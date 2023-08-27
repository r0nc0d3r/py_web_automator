import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

TECH = "angular"

DOMAIN = "DOMAIN"

URL = f"https://{DOMAIN}"

PAGE = 2

options = webdriver.ChromeOptions()

options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(options=options)

timeout = 3

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

driver.get(f"{URL}/q/{TECH}?access_state=pro&type=playlist&page={PAGE}")

auth_welcome_xpath = '//*[@id="__next"]/div[3]/nav/div/div[2]/a[2]/img'

wait.until(EC.presence_of_element_located((By.XPATH, auth_welcome_xpath)))

time.sleep(2)

links_xpath = '//*[@id="__next"]/div[3]/div/div/div/div[2]/div/div/main/div[4]/a'

dl_link_xpath = '//*[@id="__next"]/div[3]/div/div/div/div[1]/header/div[4]/a[1]'

dl_link_2_xpath = '//*[@id="__next"]/div[3]/div/div/div/div[1]/header/div[5]/a[1]'

dl_button_xpath = '//*[@id="__next"]/div[3]/div/div/div/div[1]/header/div[4]/button[2]'

home_page_xpath = '//*[@id="__next"]/div[3]/div/header/div/div[3]/div/a'

wait.until(EC.presence_of_element_located((By.XPATH, links_xpath)))

course_links = driver.find_elements(By.XPATH, links_xpath)

textsave = open(f"{TECH}_dl_list_{PAGE}.txt", "w")

manualsave = open(f"{TECH}_mdl_list_{PAGE}.txt", "w")

for index, val in enumerate(course_links):
    course_links = wait.until(
        lambda driver: driver.find_elements(By.XPATH, links_xpath)
    )
    actions.move_to_element(course_links[index]).perform()
    href = course_links[index].get_attribute("href")
    course_name = course_links[index].text
    course_links[index].click()
    try:
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, dl_link_2_xpath)))
        course_dl_link = wait.until(
            lambda driver: driver.find_element(By.XPATH, dl_link_2_xpath).get_attribute(
                "href"
            )
        )
        textsave.write(course_dl_link + "\n")
    except Exception as e:
        try:
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.XPATH, dl_link_xpath)))
            course_dl_link = wait.until(
                lambda driver: driver.find_element(
                    By.XPATH, dl_link_xpath
                ).get_attribute("href")
            )
            textsave.write(course_dl_link + "\n")
        except Exception as e:
            try:
                time.sleep(1)
                wait.until(EC.element_to_be_clickable((By.XPATH, dl_button_xpath)))
                course_dl_link = wait.until(
                    lambda driver: driver.find_element(By.XPATH, dl_button_xpath).text
                )
                print("err", e)
                manualsave.write(f"{href}" + "\n")
            except Exception as e:
                time.sleep(1)
                wait.until(EC.element_to_be_clickable((By.XPATH, home_page_xpath)))
                wait.until(
                    lambda driver: driver.find_element(By.XPATH, home_page_xpath).text
                )
                print("err", e)
    driver.back()

driver.close()
