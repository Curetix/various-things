import argparse
import os
import sys
from time import sleep

from selenium import webdriver

from selenium.common import NoSuchElementException, JavascriptException
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

driver: webdriver = None
base_url = "https://shift.gearboxsoftware.com"

def login(email: str, password: str):
    print("Logging in...")
    driver.get("%s/home" % base_url)
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

    if driver.current_url.startswith("%s/home" % base_url):
        print(driver.find_element(By.CLASS_NAME, "alert").text)
        sys.exit(1)
    else:
        print("Logged in successfully!")


def redeem(code: str, skip: int = 0):
    game_titles = {
        "willow2": "Borderlands 2",
        "daffodil": "Tiny Tina's Wonderlands",
        "oak": "Borderlands 3",
        "mopane": "Borderlands: Game of the Year Edition",
        "cork": "Borderlands: The Pre-Sequel"
    }
    platforms = {
        "steam": "Steam",
        "epic": "Epic",
        "xboxlive": "Xbox",
        "psn": "PlayStation",
    }

    driver.get("%s/rewards" % base_url)
    redeems = skip

    while True:
        code_input = driver.find_element(By.NAME, "shift_code")
        code_submit = driver.find_element(By.ID, "shift_code_check")

        code_input.send_keys(code)
        code_submit.click()

        code_result = driver.find_element(By.ID, "code_results")
        code_redeem_forms = driver.find_elements(By.ID, "new_archway_code_redemption")
        result = code_result.text

        if "Please wait" in result or "Unexpected error occurred" in result:
            print(result)
            print("Error redeeming code, likely rate-limited. Waiting 60 seconds...")
            sleep(60)
            continue

        if "This is not a valid SHiFT code" in result or len(code_redeem_forms) == 0:
            print(result)
            break

        current_redeem_form = code_redeem_forms[redeems]
        try:
            game_title = current_redeem_form.find_element(By.NAME, "archway_code_redemption[title]").get_attribute("value")
            game_platform = current_redeem_form.find_element(By.NAME, "archway_code_redemption[service]").get_attribute("value")
            print("Redeeming code for %s on %s" % (game_titles.get(game_title, game_title), platforms.get(game_platform, game_platform)))
        except:
            print("Redeeming code for unknown game or platform")

        current_redeem_form.submit()

        # Wait for result text, it might not appear immediately
        sleep(3)

        # Get result text from alert box
        try:
            result = driver.find_element(By.CLASS_NAME, "alert").text
            print(result)
        except:
            print("Result unknown")

        redeems += 1
        if redeems == len(code_redeem_forms):
            break

    print("Redeemed code %s times" % redeems)


def add_options(options, headless=True):
    if headless:
        options.add_argument("--headless")
    options.add_argument("--lang=en-US")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GearBox SHiFT code redeemer")
    parser.add_argument("-e", "--email", help="SHiFT email, can also use the SHIFT_EMAIL environment variable")
    parser.add_argument("-p", "--password", help="SHiFT password, can also use the SHIFT_PASSWORD environment variable")
    parser.add_argument("-b", "--browser", help="Select browser to use: chrome (default), edge, firefox", default="chrome")
    parser.add_argument("-s", "--skip", help="Skip the specified number of redemptions", type=int, default=0)
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
    
    browser = args.browser
    options = None
    driver = None
    if browser == "chrome":
        options = ChromeOptions()
        add_options(options, not args.not_headless)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    elif browser == "edge":
        options = EdgeOptions()
        add_options(options, not args.not_headless)
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        add_options(options, not args.not_headless)
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    else:
        print("Invalid browser, options are: chrome, edge, firefox")
        sys.exit(1)
    
    driver.implicitly_wait(0.5)

    login(email, password)
    redeem(code, args.skip)

