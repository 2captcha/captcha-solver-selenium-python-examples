from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v3"
apikey = os.getenv('APIKEY_2CAPTCHA')

solver = TwoCaptcha(apikey)

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
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_clickable_element(locator):
    """Waits for an element to be clickable and returns it"""
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))

def get_present_element(locator):
    """Waits for an element to be present and returns it"""
    return WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, locator)))


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
            # Extract the action's value and sitekey
            sitekey = result[0]['sitekey']
            action = result[0]['action']
            print('Parameters sitekey and action received')
            return sitekey, action
        except (IndexError, KeyError, TypeError) as e:
            retries += 1
            time.sleep(1)  # Wait a bit before retrying

    print('No reCaptcha parameters found after retries')
    return None, None

def solver_captcha(sitekey, url, action):
    """
    Solves the reCaptcha using the 2Captcha service.

    Args:
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
        action (str): The value of the action parameter that you found in the site code.
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.recaptcha(sitekey=sitekey, url=url, action=action, version='V3')
        print(f"Captcha solved. Token: {result['code']}.")
        return result
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
    get_clickable_element(locator).click()
    print("Pressed the Check button")

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

with webdriver.Chrome() as browser:
    browser.get(url)
    print("Started")

    # Getting a site key and action's value
    sitekey, action = get_captcha_params(script)

    if sitekey:
        # Sent captcha to the solution in 2captcha API
        result = solver_captcha(sitekey, url, action)

        if result:
            # From the response from the service we get the captcha id and token
            id, token = result['captchaId'], result['code']
            # Applying the token on the page
            send_token(token)
            # Checking whether the token has been accepted
            click_check_button(submit_button_captcha_locator)

            # We check if there is a message about the successful solution of the captcha and send a report on the result
            # using the captcha id
            final_message_and_report(success_message_locator, id)
            print("Finished")
        else:
            print("Failed to solve captcha")
    else:
        print("Sitekey not found")




