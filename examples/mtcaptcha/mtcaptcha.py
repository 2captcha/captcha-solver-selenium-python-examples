from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/mtcaptcha"
apikey = os.getenv('APIKEY_2CAPTCHA')


# LOCATORS

css_locator_for_input_send_token = 'input[name="mtcaptcha-verifiedtoken"]'
submit_button_captcha_locator = "//button[@data-action='demo_action']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(locator):
    """Waits for an element to be clickable and returns it"""
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def get_sitekey():
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

def send_token(css_locator, captcha_token):
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

def click_check_button(locator):
    """
    Clicks the captcha check button.

    Args:
        locator (str): The XPath locator of the check button.
    """
    get_element(locator).click()
    print("Pressed the Check button")

def final_message(locator):
    """
    Retrieves and prints the final success message.

    Args:
        locator (str): The XPath locator of the success message.
    """
    message = get_element(locator).text
    print(message)



# MAIN LOGIC

with webdriver.Chrome() as browser:
    browser.get(url)
    print("Started")

    sitekey = get_sitekey()

    token = solver_captcha(apikey, sitekey, url)

    if token:

        send_token(css_locator_for_input_send_token, token)

        click_check_button(submit_button_captcha_locator)

        final_message(success_message_locator)

        print("Finished")
    else:
        print("Failed to solve captcha")



