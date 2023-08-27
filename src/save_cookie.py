import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

DOMAIN = "DOMAIN"

options = webdriver.ChromeOptions()

options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 5000)

driver.get(
    f"https://app.{DOMAIN}/token/(TOKEN)"
)

auth_welcome_xpath = '//*[@id="__next"]/div[3]/nav/div/div[2]/a[2]/img'

wait.until(EC.presence_of_element_located((By.XPATH, auth_welcome_xpath)))

cookies = driver.get_cookies()

pickle.dump(cookies, open("PICKLE_FILE", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

driver.close()
