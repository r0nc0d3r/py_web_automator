from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

EMAIL = "email@goes.here"
DOMAIN = "DOMAIN"

options = webdriver.ChromeOptions()

options.add_experimental_option("excludeSwitches", ["enable-logging"])

options.add_experimental_option("detach", True)

options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(options=options)

timeout = 10

wait = WebDriverWait(driver, timeout)

driver.get(f"https://{DOMAIN}")

login_btn_xpath = '//*[@id="__next"]/div[3]/nav/div/div[2]/div[2]/a'

submit_btn_xpath = '//*[@id="__next"]/div[3]/div/div/div/div/form/div[2]/div/button'

WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, login_btn_xpath))
)

driver.find_element(By.XPATH, login_btn_xpath).click()

driver.find_element(By.ID, "email").send_keys(EMAIL)

driver.find_element(By.XPATH, submit_btn_xpath).click()

success_text_xpath = '//*[@id="__next"]/div[3]/div/div/div/div/div/h3'

target_text = "Please check your inbox for your sign in link."

try:
    element_present = EC.text_to_be_present_in_element(
        (By.XPATH, success_text_xpath), target_text
    )
    wait.until(element_present)
    print(f'Target text "{target_text}" is present!')
except TimeoutError:
    print(f'Target text "{target_text}" was not found within {timeout} seconds.')


driver.close()
