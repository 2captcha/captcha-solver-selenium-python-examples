from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import time
from twocaptcha import TwoCaptcha
from utilities.proxy_extension import proxies

# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v2-callback"
apikey = os.getenv('APIKEY_2CAPTCHA')
proxy = {'type': 'HTTPS',
         'uri': 'username:password@ip:port'}

solver = TwoCaptcha(apikey)

# JavaScript script to find reCAPTCHA clients and extract sitekey and callback function
script = """
    function findRecaptchaClients() {
  // eslint-disable-next-line camelcase
  if (typeof (___grecaptcha_cfg) !== 'undefined') {
    // eslint-disable-next-line camelcase, no-undef
    return Object.entries(___grecaptcha_cfg.clients).map(([cid, client]) => {
      const data = { id: cid, version: cid >= 10000 ? 'V3' : 'V2' };
      const objects = Object.entries(client).filter(([_, value]) => value && typeof value === 'object');

      objects.forEach(([toplevelKey, toplevel]) => {
        const found = Object.entries(toplevel).find(([_, value]) => (
          value && typeof value === 'object' && 'sitekey' in value && 'size' in value
        ));

        if (typeof toplevel === 'object' && toplevel instanceof HTMLElement && toplevel['tagName'] === 'DIV'){
            data.pageurl = toplevel.baseURI;
        }

        if (found) {
          const [sublevelKey, sublevel] = found;

          data.sitekey = sublevel.sitekey;
          const callbackKey = data.version === 'V2' ? 'callback' : 'promise-callback';
          const callback = sublevel[callbackKey];
          if (!callback) {
            data.callback = null;
            data.function = null;
          } else {
            data.function = callback;
            const keys = [cid, toplevelKey, sublevelKey, callbackKey].map((key) => `['${key}']`).join('');
            data.callback = `___grecaptcha_cfg.clients${keys}`;
          }
        }
      });
      return data;
    });
  }
  return [];
}
return findRecaptchaClients()
"""

# LOCATORS

success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_present_element(locator):
    """Waits for an element to be present and returns it"""
    return WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, locator)))


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
    Executes the given JavaScript script to extract the captcha callback function name and sitekey.

    Args:
        script (str): The JavaScript script to execute.
    Returns:
        tuple: A tuple containing the callback function name and the sitekey.
    """
    retries = 0
    while retries < 2:
        try:
            result = browser.execute_script(script)
            if not result or not result[0]:
                raise IndexError("Callback name is empty or null")
            callback_function_name = result[0]['function']
            sitekey = result[0]['sitekey']
            print("Got the callback function name and site key")
            return callback_function_name, sitekey
        except (IndexError, KeyError, TypeError):
            retries += 1
            time.sleep(1)  # Wait a bit before retrying

def solver_captcha(sitekey, url, proxy):
    """
    Solves the reCaptcha using the 2Captcha service.

    Args:
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
        proxy (dict): Dictionary containing the proxy settings.
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.recaptcha(sitekey=sitekey, url=url, proxy=proxy)
        print(f"Captcha solved")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token_callback(callback_function, token):
    """
    Executes the callback function with the given token.

    Args:
        callback_function (str): The name of the callback function.
        token (str): The solved captcha token.
    """
    script = f"{callback_function}('{token}')"
    browser.execute_script(script)
    print("The token is sent to the callback function")

def final_message_and_report(locator, id):
    """
    Retrieves and prints the final success message and sends a report to 2Captcha.

    Submitting answer reports is not necessary to solve the captcha. But it can help you reduce the cost of the solution
    and improve accuracy. We have described why it is important to submit reports in our blog:
    https://2captcha.com/ru/blog/reportgood-reportbad

    We recommend reporting both incorrect and correct answers.

    Args:
        locator (str): The XPath locator of the success message.
        id (str): The captcha id for reporting.
    """
    try:
        # Check for success message
        message = get_present_element(locator).text
        print(message)
        is_success = True

    except TimeoutException:
        # If the element is not found within the timeout
        print("Timed out waiting for success message element")
        is_success = False
    except Exception as e:
        # If another error occurs
        print(f"Error retrieving final message: {e}")
        is_success = False

    # Send the report anyway
    solver.report(id, is_success)
    print(f"Report sent for id: {id}, success: {is_success}")

# MAIN LOGIC

# Configure Chrome options with proxy settings
chrome_options = setup_proxy(proxy)

with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as browser:
    browser.get(url)
    print("Started")

    callback_function, sitekey = get_captcha_params(script)

    if sitekey:
        result = solver_captcha(sitekey, url, proxy)

        if result:
            id, token = result['captchaId'], result['code']
            send_token_callback(callback_function, token)

            final_message_and_report(success_message_locator, id)
            print("Finished")
        else:
            print("Failed to solve captcha")
    else:
        print("Sitekey not found")