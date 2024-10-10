from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/mtcaptcha"
apikey = os.getenv('APIKEY_2CAPTCHA')

solver = TwoCaptcha(apikey)


# LOCATORS

css_locator_for_input_send_token = 'input[name="mtcaptcha-verifiedtoken"]'
submit_button_captcha_locator = "//button[@data-action='demo_action']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_clickable_element(locator):
    """Waits for an element to be clickable and returns it"""
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))

def get_present_element(locator):
    """Waits for an element to be present and returns it"""
    return WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, locator)))


# ACTIONS

def get_sitekey():
    """
    Retrieves the MTCaptcha sitekey from the webpage using JavaScript.

    Returns:
        str: The sitekey for MTCaptcha.
    """
    time.sleep(3)  # Adding a delay to ensure the sitekey is loaded
    sitekey = browser.execute_script("""
        return window.mtcaptchaConfig.sitekey || window.mtcaptcha.getConfiguration().sitekey;
        """)

    print("Sitekey received")
    return sitekey

def solver_captcha(sitekey, url):
    """
    Solves the MTCaptcha using the 2Captcha service.

    Args:
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.mtcaptcha(sitekey=sitekey, url=url)
        print(f"Captcha solved. Answer: {result['code']}.")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(css_locator, captcha_token):
    """
    Sends the captcha token to the MTCaptcha response field.

    Args:
        css_locator (str): The CSS locator for the input field.
        captcha_token (str): The solved captcha token.
    """
    script = f"""
        var element = document.querySelector('{css_locator}');
        if (element) {{
            element.value = "{captcha_token}";
        }}
    """
    browser.execute_script(script)
    print("Token sent")

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

    # Getting a site key
    sitekey = get_sitekey()

    if sitekey:
        # Sent captcha to the solution in 2captcha API
        result = solver_captcha(sitekey, url)

        if result:
            # From the response from the service we get the captcha id and token
            id, token = result['captchaId'], result['code']
            # Applying the token on the page
            send_token(css_locator_for_input_send_token, token)
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



