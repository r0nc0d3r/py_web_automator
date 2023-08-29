import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from vars.website1 import *

options = webdriver.ChromeOptions()

options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 5000)

driver.get(
    f"https://app.{DOMAIN}/token/(TOKEN)"
)

wait.until(EC.presence_of_element_located((By.XPATH, auth_welcome_xpath)))

cookies = driver.get_cookies()

pickle.dump(cookies, open("PICKLE_FILE", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

driver.close()
