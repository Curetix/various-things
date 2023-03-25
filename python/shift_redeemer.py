import argparse
import os
import sys

from selenium import webdriver
from selenium.common import NoSuchElementException, JavascriptException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver: webdriver.Chrome = None


def login(email: str, password: str):
    print("Logging in...")
    driver.get("https://shift.gearbox.com/home")
    try:
        driver.execute_script("acceptCookieBanner();")
    except JavascriptException:
        driver.add_cookie({
            "name": "accepted_cookie_banner",
            "value": "1",
            "domain": "shift.gearboxsoftware.com",
            "path": "/"
        })

    email_input = driver.find_element(By.NAME, "user[email]")
    password_input = driver.find_element(By.NAME, "user[password]")
    submit_button = driver.find_element(By.NAME, "commit")

    email_input.clear()
    email_input.send_keys(email)
    password_input.clear()
    password_input.send_keys(password)
    submit_button.click()

    if driver.current_url.startswith("https://shift.gearbox.com/home"):
        print(driver.find_element(By.CLASS_NAME, "alert").text)
        sys.exit(1)
    else:
        print("Logged in successfully!")


def redeem(code: str):
    game_titles = {
        "willow2": "Borderlands 2",
        "daffodil": "Tiny Tina's Wonderlands",
        "oak": "Borderlands 3",
    }
    platforms = {
        "steam": "Steam",
        "epic": "Epic",
        "xboxlive": "Xbox",
        "psn": "PlayStation",
    }

    driver.get("https://shift.gearboxsoftware.com/rewards")
    redeems = 0

    while True:
        code_input = driver.find_element(By.NAME, "shift_code")
        code_submit = driver.find_element(By.ID, "shift_code_check")

        code_input.send_keys(code)
        code_submit.click()

        code_result = driver.find_element(By.ID, "code_results")
        code_redeem_forms = driver.find_elements(By.ID, "new_archway_code_redemption")

        if code_result.text.find("This is not a valid SHiFT code") > -1 or len(code_redeem_forms) == 0:
            print(code_result.text)
            break

        current_redeem_form = code_redeem_forms[redeems]
        try:
            game_title = current_redeem_form.find_element(By.NAME, "archway_code_redemption[title]").get_attribute("value")
            game_platform = current_redeem_form.find_element(By.NAME, "archway_code_redemption[service]").get_attribute("value")
            print("Redeeming code for %s on %s" % (game_titles.get(game_title, game_title), platforms.get(game_platform, game_platform)))
        except Exception:
            print("Redeeming code")

        current_redeem_form.submit()

        print(driver.find_element(By.CLASS_NAME, "alert").text)

        redeems += 1
        if redeems == len(code_redeem_forms):
            break

    print("Redeemed code %s times" % redeems)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GearBox SHiFT code redeemer")
    parser.add_argument("-e", "--email", help="SHiFT email, can also use the SHIFT_EMAIL environment variable")
    parser.add_argument("-p", "--password", help="SHiFT password, can also use the SHIFT_PASSWORD environment variable")
    parser.add_argument("--not-headless", help="Do not run in headless mode", action="store_true", default=False)
    parser.add_argument("code", help="SHiFT code to redeem")
    args = parser.parse_args()

    email = args.email or os.environ.get("SHIFT_EMAIL")
    if not email:
        print("SHiFT email not provided!")
        sys.exit(1)

    password = args.password or os.environ.get("SHIFT_PASSWORD")
    if not password:
        print("SHiFT password not provided!")
        sys.exit(1)

    code = args.code
    if not code:
        print("SHiFT code not provided!")
        sys.exit(1)

    options = Options()
    if not args.not_headless:
        options.add_argument("--headless")
    options.add_argument("--lang=en-US")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(0.5)

    login(email, password)
    redeem(code)

