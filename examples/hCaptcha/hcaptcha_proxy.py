from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
from twocaptcha import TwoCaptcha
from utilities.proxy_extension import proxies


# CONFIGURATION

url = 'https://2captcha.com/demo/hcaptcha'
apikey = os.getenv('APIKEY_2CAPTCHA')
proxy = {'type': 'HTTP',
         'uri': 'username:password@ip:port'}


# LOCATORS

iframe_locator = "//div[@class='h-captcha']//iframe"
submit_button_captcha_locator = "//button[@type='submit']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(locator):
    """Waits for an element to be clickable and returns it"""
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
    scheme = proxy['type'].lower
    auth, address = proxy['uri'].split('@')
    login, password = auth.split(':')
    ip, port = address.split(':')
    return scheme, login, password, ip, port

def setup_proxy(proxy):
    """
    Sets up the proxy configuration for Chrome browser.

    Args:
        proxy (dict): Dictionary containing the proxy type and URI.

    Returns:
        Options: Configured Chrome options with proxy settings.
    """
    chrome_options = webdriver.ChromeOptions()
    scheme, username, password, ip, port = parse_proxy_uri(proxy)
    proxies_extension = proxies(scheme, username, password, ip, port)
    chrome_options.add_extension(proxies_extension)
    return chrome_options

def get_sitekey(locator):
    """Extracts the sitekey from the iframe's URL"""
    iframe_element = get_element(locator)
    url = iframe_element.get_attribute('src')
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.fragment)
    sitekey = params.get('sitekey', [None])[0]
    print(f"Sitekey received: {sitekey}")
    return sitekey

def solver_captcha(apikey, sitekey, url, proxy):
    """Solves the hCaptcha using the 2Captcha service"""
    solver = TwoCaptcha(apikey)
    try:
        result = solver.hcaptcha(sitekey=sitekey, url=url, proxy=proxy)
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(captcha_token):
    """Sends the captcha token to the hCaptcha iframe and response field"""
    script = f"""
        document.querySelector('iframe[src*=\\"hcaptcha\\"]').setAttribute('data-hcaptcha-response', '{captcha_token}');
        document.querySelector('[name="h-captcha-response"]').innerText = '{captcha_token}';
    """
    browser.execute_script(script)
    print("Token sent")

def click_check_button(locator):
    """Clicks the captcha check button"""
    get_element(locator).click()
    print("Pressed the Check button")

def final_message(locator):
    """Retrieves and prints the final success message"""
    message = get_element(locator).text
    print(message)


# MAIN LOGIC

# Configure Chrome options with proxy settings
chrome_options = setup_proxy(proxy)

# Automatically closes the browser after block execution completes
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as browser:
    # Go to the specified URL
    browser.get(url)
    print("Started")

    # Getting sitekey from iframe
    sitekey = get_sitekey(iframe_locator)
    # Solving the captcha and receiving a token
    token = solver_captcha(apikey, sitekey, url, proxy)

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


