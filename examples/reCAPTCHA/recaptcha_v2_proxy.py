import os
import time
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
from utilities.proxy_extension import proxies

# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v2"
apikey = os.getenv("APIKEY_2CAPTCHA")
proxy = {
    'type': 'HTTPS',
    'uri': 'username:password@ip:port',
}


# LOCATORS

sitekey_locator = "//div[@id='g-recaptcha']"
submit_button_captcha_locator = "//button[@data-action='demo_action']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(browser, locator):
    """
    Waits for an element to be clickable and returns it.

    This helper can be copied and reused in other projects that use SeleniumBase.
    """
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def parse_proxy_uri(proxy):
    """
    Parses the proxy URI to extract the scheme, login, password, IP, and port.

    Args:
        proxy (dict): Dictionary containing the proxy type and URI.
    Returns:
        tuple: A tuple containing scheme, login, password, IP, and port.
    """
    scheme = proxy['type'].lower()
    auth, address = proxy['uri'].split('@')
    login, password = auth.split(':')
    ip, port = address.split(':')
    return scheme, login, password, ip, port

def setup_proxy(proxy):
    """
    Builds a Chrome extension zip for authenticated proxy usage.

    Args:
        proxy (dict): Dictionary containing the proxy type and URI.

    Returns:
        str: Path to the generated proxy extension zip.
    """
    scheme, username, password, ip, port = parse_proxy_uri(proxy)
    proxies_extension = proxies(scheme, username, password, ip, port)
    return proxies_extension

def get_sitekey(browser, locator):
    """
    Extracts the sitekey from the specified element.

    Args:
        browser: The SeleniumBase driver instance.
        locator (str): The XPath locator of the element.
    Returns:
        str: The sitekey value.
    """
    sitekey_element = get_element(browser, locator)
    sitekey = sitekey_element.get_attribute('data-sitekey')
    print(f"Sitekey received: {sitekey}")
    return sitekey

def solver_captcha(apikey, sitekey, url, proxy):
    """
    Solves the reCaptcha using the 2Captcha service.

    Args:
        apikey (str): The 2Captcha API key.
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
        proxy (dict): Dictionary containing the proxy settings.
    Returns:
        str: The solved captcha code, or None if an error occurred.
    """
    solver = TwoCaptcha(apikey)
    try:
        result = solver.recaptcha(sitekey=sitekey, url=url, proxy=proxy)
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(browser, captcha_token):
    """
    Sends the captcha token to the reCaptcha response field.

    Args:
        browser: The SeleniumBase driver instance.
        captcha_token (str): The solved captcha token.
        """
    script = f"""
        document.querySelector('[id="g-recaptcha-response"]').innerText = '{captcha_token}';
    """
    browser.execute_script(script)
    print("Token sent")

def click_check_button(browser, locator):
    """
    Clicks the captcha check button.

    Args:
        browser: The SeleniumBase driver instance.
        locator (str): The XPath locator of the check button.
    """
    get_element(browser, locator).click()
    print("Pressed the Check button")

def final_message(browser, locator):
    """
    Retrieves and prints the final success message.

    Args:
        browser: The SeleniumBase driver instance.
        locator (str): The XPath locator of the success message.
    """
    message = get_element(browser, locator).text
    print(message)


def main():
    """
    Runs the full demo flow for solving reCaptcha v2 with a proxy using 2Captcha.

    Helper functions (`parse_proxy_uri`, `setup_proxy`, `get_sitekey`, `solver_captcha`,
    `send_token`, etc.) are designed so they can be copied and reused independently.
    """
    if not apikey:
        raise RuntimeError("Set APIKEY_2CAPTCHA environment variable")

    # Generate a Chrome extension that applies authenticated proxy settings
    proxy_extension_zip = setup_proxy(proxy)

    with Driver(
        browser="chrome",
        headless=False,
        extension_zip=proxy_extension_zip,
    ) as browser:
        # Go to the specified URL
        browser.get(url)
        print('Started')

        # Getting sitekey from the sitekey element
        sitekey = get_sitekey(browser, sitekey_locator)

        # Solving the captcha and receiving a token
        token = solver_captcha(apikey, sitekey, url, proxy)

        if token:
            # Sending solved captcha token
            send_token(browser, token)

            # Pressing the Check button
            click_check_button(browser, submit_button_captcha_locator)

            # Receiving and displaying a success message
            final_message(browser, success_message_locator)

            # Pause to observe the result before closing the browser
            time.sleep(5)
            print("Finished")
        else:
            print("Failed to solve captcha")


if __name__ == "__main__":
    main()
