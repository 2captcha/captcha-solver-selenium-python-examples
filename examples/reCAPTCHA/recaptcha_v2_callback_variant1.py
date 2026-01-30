import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from twocaptcha import TwoCaptcha

# Description: 
# The value of the `sitekey` parameter is extracted from the page code automaticly. 
# The value of the callback function “verifyDemoRecaptcha()” is specified manually.
# The name of the “verifyDemoRecaptcha()” function may be different when bypassing captcha on another page.
# You need to fugure out the name of the callback function yourself and specify it in the code.

# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v2-callback"
apikey = os.getenv('APIKEY_2CAPTCHA')


# LOCATORS

sitekey_locator = "//div[@id='g-recaptcha']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(browser, locator):
    """
    Waits for an element to be clickable and returns it.

    This helper can be copied and reused in other projects that use Selenium.
    """
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def get_sitekey(browser, locator):
    """
    Extracts the sitekey from the specified element.

    Args:
        browser (webdriver): The Selenium WebDriver instance.
        locator (str): The XPath locator of the element.
    Returns:
        str: The sitekey value.
    """
    sitekey_element = get_element(browser, locator)
    sitekey = sitekey_element.get_attribute('data-sitekey')
    print(f"Sitekey received: {sitekey}")
    return sitekey

def solver_captcha(apikey, sitekey, url):
    """
    Solves the reCaptcha using the 2Captcha service.

    Args:
        apikey (str): The 2Captcha API key.
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
    Returns:
        str: The solved captcha code.
    """
    solver = TwoCaptcha(apikey)
    try:
        result = solver.recaptcha(sitekey=sitekey, url=url)
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(browser, token):
    # verifyDemoRecaptcha() it is JavaScript callback function on page with captcha.
    # callback function executing for apply token.
    script = f"verifyDemoRecaptcha('{token}');"
    browser.execute_script(script)
    print("The token is sent to the callback function")

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
    Runs the demo flow for solving reCaptcha v2 with a callback using 2Captcha.

    Helper functions (`get_sitekey`, `solver_captcha`, `send_token`, etc.)
    are designed so they can be copied and reused independently.
    """
    apikey = os.getenv("APIKEY_2CAPTCHA")
    if not apikey:
        raise RuntimeError("Set APIKEY_2CAPTCHA environment variable")

    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as browser:
        # Go to the specified URL
        browser.get(url)
        print('Started')

        # Getting sitekey from the sitekey element
        sitekey = get_sitekey(browser, sitekey_locator)

        # Solving the captcha and receiving a token
        token = solver_captcha(apikey, sitekey, url)

        if token:
            # Sending solved captcha token to callback
            send_token(browser, token)

            # Receiving and displaying a success message
            final_message(browser, success_message_locator)

            # Explicit pause to observe the result
            time.sleep(5)
            print("Finished")
        else:
            print("Failed to solve captcha")


if __name__ == "__main__":
    main()
