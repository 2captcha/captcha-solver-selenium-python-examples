from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import os
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/hcaptcha"
apikey = os.getenv('APIKEY_2CAPTCHA')


# LOCATORS

iframe_locator = "//div[@class='h-captcha']//iframe"
submit_button_captcha_locator = "//button[@type='submit']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(locator):
    """Waits for an element to be clickable and returns it"""
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def get_sitekey(locator):
    """
    Extracts the sitekey from the iframe's URL.

    Args:
        locator (str): The XPath locator of the iframe element.
    Returns:
        str: The sitekey value.
    """
    iframe_element = get_element(locator)
    url = iframe_element.get_attribute('src')
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.fragment)
    sitekey = params.get('sitekey', [None])[0]
    print(f"Sitekey received: {sitekey}")
    return sitekey

def solver_captcha(apikey, sitekey, url):
    """
    Solves the hCaptcha using the 2Captcha service.

    Args:
        apikey (str): The 2Captcha API key.
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
    Returns:
        str: The solved captcha code, or None if an error occurred.
    """
    solver = TwoCaptcha(apikey)
    try:
        result = solver.hcaptcha(sitekey=sitekey, url=url)
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(captcha_token):
    """
    Sends the captcha token to the hCaptcha iframe and response field.

    Args:
        captcha_token (str): The solved captcha token.
    """
    script = f"""
        document.querySelector('iframe[src*=\\"hcaptcha\\"]').setAttribute('data-hcaptcha-response', '{captcha_token}');
        document.querySelector('[name="h-captcha-response"]').innerText = '{captcha_token}';
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

# Automatically closes the browser after block execution completes
with webdriver.Chrome() as browser:
    # Go to the specified URL
    browser.get(url)
    print("Started")

    # Getting sitekey from iframe
    sitekey = get_sitekey(iframe_locator)
    # Solving the captcha and receiving a token
    token = solver_captcha(apikey, sitekey, url)

    if token:
        # Sending solved captcha token
        send_token(token)
        # Pressing the Check button
        click_check_button(submit_button_captcha_locator)
        # Receiving and displaying a success message
        final_message(success_message_locator)

        browser.implicitly_wait(5)
        print("Finished")
    else:
        print("Failed to solve captcha")


