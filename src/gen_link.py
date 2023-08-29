from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from vars.website1 import *

options = webdriver.ChromeOptions()

options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(options=options)

timeout = 10

wait = WebDriverWait(driver, timeout)

driver.get(f"https://{DOMAIN}")

WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, login_link_xpath))
)

driver.find_element(By.XPATH, login_link_xpath).click()

driver.find_element(By.ID, email_field_id).send_keys(EMAIL)

driver.find_element(By.XPATH, submit_btn_xpath).click()

try:
    element_present = EC.text_to_be_present_in_element(
        (By.XPATH, success_text_xpath), login_link_sent_msg
    )

    wait.until(element_present)

    print(f'Target text "{login_link_sent_msg}" is present!')

except TimeoutError:
    print(
        f'Target text "{login_link_sent_msg}" was not found within {timeout} seconds.'
    )


driver.close()
