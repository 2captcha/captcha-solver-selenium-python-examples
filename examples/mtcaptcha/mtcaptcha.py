import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/mtcaptcha"
apikey = os.getenv('APIKEY_2CAPTCHA')


# LOCATORS

css_locator_for_input_send_token = 'input[name="mtcaptcha-verifiedtoken"]'
submit_button_captcha_locator = "//button[@data-action='demo_action']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(browser, locator):
    """
    Waits for an element to be clickable and returns it.

    This helper can be copied and reused in other projects that use Selenium.
    """
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def get_sitekey(browser):
    """
    Retrieves the MTCaptcha sitekey from the webpage using JavaScript.

    Returns:
        str: The sitekey for MTCaptcha.
    """
    time.sleep(3)  # Adding a delay to ensure the sitekey is loaded
    sitekey = browser.execute_script("""
        return window.mtcaptchaConfig.sitekey || window.mtcaptcha.getConfiguration().sitekey;
        """)

    print("Sitekey received")
    return sitekey

def solver_captcha(apikey, sitekey, url):
    """
    Solves the MTCaptcha using the 2Captcha service.

    Args:
        apikey (str): The 2Captcha API key.
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
    Returns:
        str: The solved captcha code.
    """
    solver = TwoCaptcha(apikey)
    try:
        result = solver.mtcaptcha(sitekey=sitekey, url=url)
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(browser, css_locator, captcha_token):
    """
    Sends the captcha token to the MTCaptcha response field.

    Args:
        css_locator (str): The CSS locator for the input field.
        captcha_token (str): The solved captcha token.
    """
    script = f"""
        var element = document.querySelector('{css_locator}');
        if (element) {{
            element.value = "{captcha_token}";
        }}
    """
    browser.execute_script(script)
    print("Token sent")

def click_check_button(browser, locator):
    """
    Clicks the captcha check button.

    Args:
        locator (str): The XPath locator of the check button.
    """
    get_element(browser, locator).click()
    print("Pressed the Check button")

def final_message(browser, locator):
    """
    Retrieves and prints the final success message.

    Args:
        locator (str): The XPath locator of the success message.
    """
    message = get_element(browser, locator).text
    print(message)


def main():
    """
    Runs the demo flow for solving MTCaptcha using 2Captcha.

    Helper functions (`get_sitekey`, `solver_captcha`, `send_token`, etc.)
    are designed so they can be copied and reused independently.
    """
    apikey = os.getenv("APIKEY_2CAPTCHA")
    if not apikey:
        raise RuntimeError("Set APIKEY_2CAPTCHA environment variable")

    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as browser:
        browser.get(url)
        print("Started")

        sitekey = get_sitekey(browser)

        token = solver_captcha(apikey, sitekey, url)

        if token:
            send_token(browser, css_locator_for_input_send_token, token)
            click_check_button(browser, submit_button_captcha_locator)
            final_message(browser, success_message_locator)
            time.sleep(5)
            print("Finished")
        else:
            print("Failed to solve captcha")


if __name__ == "__main__":
    main()

