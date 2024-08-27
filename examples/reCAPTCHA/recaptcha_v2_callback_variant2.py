from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from twocaptcha import TwoCaptcha

# Description: 
# Captcha parameters are determined automatically with the help of JavaScript script executed on the page.


# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v2-callback"
apikey = os.getenv('APIKEY_2CAPTCHA')

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

def get_element(locator):
    """Waits for an element to be clickable and returns it"""
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

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

def final_message(locator):
    """
    Retrieves and prints the final success message.

    Args:
        locator (str): The XPath locator of the success message.
    """
    message = get_element(locator).text
    print(message)


with webdriver.Chrome() as browser:
    browser.get(url)
    print("Started")

    # Extracting callback function name and sitekey using the provided script
    callback_function, sitekey = get_captcha_params(script)

    # Solving the captcha and receiving the token
    token = solver_captcha(apikey, sitekey, url)

    if token:
        # Sending the solved captcha token to the callback function
        send_token_callback(callback_function, token)

        # Retrieving and printing the final success message
        final_message(success_message_locator)

        browser.implicitly_wait(5)
        print("Finished")
    else:
        print("Failed to solve captcha")





