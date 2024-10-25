from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from twocaptcha import TwoCaptcha

# Description: 
# The value of the `sitekey` parameter is extracted from the page code automaticly. 
# The value of the callback function “verifyDemoRecaptcha()” is specified manually.
# The name of the “verifyDemoRecaptcha()” function may be different when bypassing captcha on another page.
# You need to fugure out the name of the callback function yourself and specify it in the code.

# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v2-callback"
apikey = os.getenv('APIKEY_2CAPTCHA')

solver = TwoCaptcha(apikey)

# LOCATORS

sitekey_locator = "//div[@id='g-recaptcha']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_present_element(locator):
    """Waits for an element to be present and returns it"""
    return WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, locator)))


# ACTIONS

def get_sitekey(locator):
    """
    Extracts the sitekey from the specified element.

    Args:
        locator (str): The XPath locator of the element.
    Returns:
        str: The sitekey value.
    """
    sitekey_element = get_present_element(locator)
    sitekey = sitekey_element.get_attribute('data-sitekey')
    print(f"Sitekey received: {sitekey}")
    return sitekey

def solver_captcha(sitekey, url):
    """
    Solves the reCaptcha using the 2Captcha service.

    Args:
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.recaptcha(sitekey=sitekey, url=url)
        print(f"Captcha solved. Token: {result['code']}.")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(token):
    # verifyDemoRecaptcha() it is JavaScript callback function on page with captcha.
    # callback function executing for apply token.
    script = f"verifyDemoRecaptcha('{token}');"
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

with webdriver.Chrome() as browser:
    browser.get(url)
    print('Started')

    # Getting a site key
    sitekey = get_sitekey(sitekey_locator)

    if sitekey:
        # Sent captcha to the solution in 2captcha API
        result = solver_captcha(sitekey, url)

        if result:
            # From the response from the service we get the captcha id and token
            id, token = result['captchaId'], result['code']
            # Applying the token using the callback function
            send_token(token)

            # We check if there is a message about the successful solution of the captcha and send a report on the result
            # using the captcha id
            final_message_and_report(success_message_locator, id)
            print("Finished")
        else:
            print("Failed to solve captcha")
    else:
        print("Sitekey not found")
