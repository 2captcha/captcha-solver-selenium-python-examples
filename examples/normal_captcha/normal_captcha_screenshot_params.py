from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/normal"
apikey = os.getenv('APIKEY_2CAPTCHA')

solver = TwoCaptcha(apikey)

# ADVANCED CAPTCHA OPTIONS

extra_options = {
    "numeric": 4,
    "minLen": 4,
    "maxLen": 10,
    "lang": "en"
}


# LOCATORS

img_locator = "//img[@class='_captchaImage_rrn3u_9']"
input_captcha_locator = "//input[@id='simple-captcha-field']"
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

def solver_captcha(image, **extra_options):
    """
    Solves a captcha using the 2Captcha service and returns the solution code

    Args:
        image (str): Path to the captcha image
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.normal(image, **extra_options)
        print(f"Captcha solved")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_image_base64(locator):
    """
    Captures a screenshot of the element specified by the locator and returns it as a base64-encoded string.

    Args:
        locator (str): The XPath locator of the image element.
    Returns:
        str: The base64-encoded screenshot of the image element.
    """
    image_element = get_present_element(locator)
    base64_image = image_element.screenshot_as_base64
    return base64_image

def input_captcha_code(locator, code):
    """
    Enters the captcha solution code into the input field on the web page
    Args:
        locator (str): XPATH locator of the captcha input field
        code (str): Captcha solution code
    """
    input_field = get_clickable_element(locator)
    input_field.send_keys(code)
    print("Entered the answer to the captcha")

def click_check_button(locator):
    """
    Clicks the check button on a web page
    Args:
        locator (str): XPATH locator of the captcha verification button
    """
    button = get_clickable_element(locator)
    button.click()
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

# Automatically closes the browser after block execution completes
with webdriver.Chrome() as browser:

    browser.get(url)
    print("Started")

    image_base64 = get_image_base64(img_locator)
    result = solver_captcha(image_base64, **extra_options)

    if result:
        id, code = result['captchaId'], result['code']
        input_captcha_code(input_captcha_locator, code)
        click_check_button(submit_button_captcha_locator)
        final_message_and_report(success_message_locator, id)

        browser.implicitly_wait(5)
        print("Finished")
    else:
        print("Failed to solve captcha")

