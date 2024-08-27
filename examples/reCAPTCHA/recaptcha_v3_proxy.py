from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import time
from twocaptcha import TwoCaptcha
from utilities.proxy_extension import proxies


# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v3"
apikey = os.getenv('APIKEY_2CAPTCHA')
proxy = {'type': 'HTTPS',
         'uri': 'username:password@ip:port'}

script = """
function findRecaptchaData() {
  const results = [];

  // Collecting the text of all scripts on the page
  const scriptContents = Array.from(document.scripts)
    .map(script => script.innerHTML || '')
    .join('\\n');

  // Regular expression to search for grecaptcha.execute call
  const executePattern = /grecaptcha\\.execute\\s*\\(\\s*['"]([^'"]+)['"]\\s*,\\s*\\{[^}]*?\\baction\\b\\s*:\\s*['"]([^'"]+)['"][^}]*?\\}/gi;

  let match;
  while ((match = executePattern.exec(scriptContents)) !== null) {
    results.push({
      sitekey: match[1],
      action: match[2]
    });
  }

  return results;
}

return findRecaptchaData();
"""


# LOCATORS

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

def get_captcha_params(script):
    """
    Executes the JavaScript to get reCaptcha parameters from the page.

    Args:
        script (str): The JavaScript code to execute.

    Returns:
        tuple: The sitekey and action parameters.
    """
    retries = 0
    while retries < 2:
        try:
            result = browser.execute_script(script)
            if not result or not result[0]:
                raise IndexError("No reCaptcha parameters found")
            sitekey = result[0]['sitekey']
            action = result[0]['action']
            print('Parameters sitekey and action received')
            return sitekey, action
        except (IndexError, KeyError, TypeError) as e:
            retries += 1
            time.sleep(1)  # Wait a bit before retrying

    print('No reCaptcha parameters found after retries')
    return None, None

def solver_captcha(apikey, sitekey, url, action, proxy):
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
        result = solver.recaptcha(sitekey=sitekey, url=url, action=action, version='V3', proxy=proxy)
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(token):
    """
    Sends the solved reCaptcha token to the page.

    Args:
        token (str): The solved captcha token.
    """
    script = f"window.verifyRecaptcha('{token}')"
    browser.execute_script(script)
    print('The token is sent')

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

chrome_options = setup_proxy(proxy)

with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as browser:
    browser.get(url)
    print("Started")

    # Get captcha parameters
    sitekey, action = get_captcha_params(script)

    # Solve the captcha
    token = solver_captcha(apikey, sitekey, url, action, proxy)

    if token:
        # Send the token
        send_token(token)

        # Click the check button
        click_check_button(submit_button_captcha_locator)

        # Get the final success message
        final_message(success_message_locator)

        browser.implicitly_wait(5)
        print("Finished")
    else:
        print("Failed to solve captcha")


