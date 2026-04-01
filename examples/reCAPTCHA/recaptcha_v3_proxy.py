import os
import time
from seleniumbase import Driver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
from utilities.proxy_extension import proxies


# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v3"
apikey = os.getenv("APIKEY_2CAPTCHA")
proxy = {
    "type": "HTTPS",
    "uri": "username:password@ip:port",
}

script = """
function findRecaptchaData() {
  const results = [];

  // Collect the text of all scripts on the page.
  const scriptContents = Array.from(document.scripts)
    .map(script => script.innerHTML || '')
    .join('\\n');

  // Search for grecaptcha.execute calls and extract sitekey + action.
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
    scheme = proxy["type"].lower()
    auth, address = proxy["uri"].split("@")
    login, password = auth.split(":")
    ip, port = address.split(":")
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
    return proxies(scheme, username, password, ip, port)

def get_captcha_params(browser, script):
    """
    Executes the JavaScript to get reCAPTCHA v3 parameters from the page.

    Args:
        browser: The SeleniumBase driver instance.
        script (str): The JavaScript code to execute.

    Returns:
        tuple: The sitekey and action parameters.
    """
    WebDriverWait(browser, 30).until(
        lambda driver: driver.execute_script(
            "return Array.from(document.scripts).some(script => (script.innerHTML || '').includes('grecaptcha.execute'));"
        )
    )

    retries = 0
    while retries < 3:
        result = browser.execute_script(script)
        captcha_data = next(
            (
                item for item in result
                if item and item.get("sitekey") and item.get("action")
            ),
            None,
        )
        if captcha_data:
            sitekey = captcha_data["sitekey"]
            action = captcha_data["action"]
            print("Parameters sitekey and action received")
            return sitekey, action

        retries += 1
        time.sleep(1)

    raise TimeoutException("Timed out waiting for reCAPTCHA v3 parameters")

def solver_captcha(apikey, sitekey, url, action, proxy):
    """
    Solves the reCAPTCHA using the 2Captcha service.

    Args:
        apikey (str): The 2Captcha API key.
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
        action (str): The reCAPTCHA action value.
        proxy (dict): Dictionary containing the proxy settings.
    Returns:
        str: The solved captcha code.
    """
    solver = TwoCaptcha(apikey)
    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=url,
            action=action,
            version="V3",
            proxy=proxy,
        )
        print("Captcha solved")
        return result["code"]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(browser, token):
    """
    Sends the solved reCAPTCHA token to the page.

    Args:
        browser: The SeleniumBase driver instance.
        token (str): The solved captcha token.
    """
    browser.execute_script(f"window.verifyRecaptcha('{token}')")
    print("The token is sent")

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
    Runs the demo flow for solving reCAPTCHA v3 with a proxy using 2Captcha.

    Helper functions (`setup_proxy`, `get_captcha_params`, `solver_captcha`, etc.)
    are designed so they can be copied and reused independently.
    """
    if not apikey:
        raise RuntimeError("Set APIKEY_2CAPTCHA environment variable")

    proxy_extension_zip = setup_proxy(proxy)

    with Driver(
        browser="chrome",
        headless=False,
        extension_zip=proxy_extension_zip,
    ) as browser:
        browser.get(url)
        print("Started")

        sitekey, action = get_captcha_params(browser, script)
        token = solver_captcha(apikey, sitekey, url, action, proxy)

        if token:
            send_token(browser, token)
            click_check_button(browser, submit_button_captcha_locator)
            final_message(browser, success_message_locator)

            time.sleep(5)
            print("Finished")
        else:
            print("Failed to solve captcha")


if __name__ == "__main__":
    main()
