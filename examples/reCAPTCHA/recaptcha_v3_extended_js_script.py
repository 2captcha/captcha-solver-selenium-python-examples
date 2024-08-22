from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v3"
apikey = os.getenv('APIKEY_2CAPTCHA')

script = """
function findRecaptchaData() {
    const results = [];

    // Collecting the text of all scripts on the page
    const scriptContents = Array.from(document.scripts)
        .map(script => script.innerHTML || '')
        .join('\\n');

    // Regular expressions to find sitekey and action
    const sitekeyPattern = /['"]sitekey['"]\\s*:\\s*['"]([^'"]+)['"]/gi;
    const actionPattern = /['"]action['"]\\s*:\\s*['"]([^'"]+)['"]/gi;
    const executePattern = /grecaptcha\\.execute\\s*\\(\\s*['"]([^'"]+)['"]\\s*,\\s*\\{[^}]*?\\baction\\b\\s*:\\s*['"]([^'"]+)['"][^}]*?\\}/gi;

    let match;

    // We are looking for sitekey and action in grecaptcha.execute
    while ((match = executePattern.exec(scriptContents)) !== null) {
        results.push({
            sitekey: match[1],
            action: match[2]
        });
    }

    // We are looking for sitekey and action in separate code blocks
    const sitekeys = [];
    while ((match = sitekeyPattern.exec(scriptContents)) !== null) {
        sitekeys.push(match[1]);
    }

    const actions = [];
    while ((match = actionPattern.exec(scriptContents)) !== null) {
        actions.push(match[1]);
    }

    // We connect the found sitekey and action
    for (let i = 0; i < Math.min(sitekeys.length, actions.length); i++) {
        results.push({
            sitekey: sitekeys[i],
            action: actions[i]
        });
    }

    return results;
}

return findRecaptchaData();
"""


# LOCATORS

submit_button_captcha_locator = "//button[@type='submit']"
success_message_locator = "//p[@class='_successMessage_mbkq7_1']"


# GETTERS

def get_element(locator):
    """Waits for an element to be clickable and returns it"""
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

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

def solver_captcha(apikey, sitekey, url, action):
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
        result = solver.recaptcha(sitekey=sitekey, url=url, action=action, version='V3')
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

with webdriver.Chrome() as browser:
    browser.get(url)
    print("Started")

    # Get captcha parameters
    sitekey, action = get_captcha_params(script)

    # Solve the captcha
    token = solver_captcha(apikey, sitekey, url, action)

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


