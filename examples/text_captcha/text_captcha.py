from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/text"
apikey = os.getenv('APIKEY_2CAPTCHA')

solver = TwoCaptcha(apikey)


# LOCATORS

captcha_question_locator = "//label[@for='text-captcha-field']"
captcha_input_locator = "//input[@id='text-captcha-field']"
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

def get_captcha_question(locator):
    """
    Extracts the captcha question text from the specified element.

    Args:
        locator (str): XPath locator of the captcha question element.
    Returns:
        str: Text of the captcha question.
    """
    question_element = get_present_element(locator)
    text_question = question_element.text
    return text_question

def solver_captcha(question):
    """
    Solves a captcha using the 2Captcha service and returns the solution code.

    Args:
        question (str): Captcha text.
        apikey (str): API key to access the 2Captcha service.
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.text(question)
        print(f"Captcha solved")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_answer(locator, answer):
    """
    Inputs the captcha answer into the specified input field.

    Args:
        locator (str): XPath locator of the input field.
        answer (str): Captcha answer.
    """
    input_element = get_clickable_element(locator)
    input_element.send_keys(answer)
    print("Entering the answer to captcha")

def click_check_button(locator):
    """
    Clicks the check button on a web page.

    Args:
        locator (str): XPATH locator of the captcha verification button.
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

    captcha_question = get_captcha_question(captcha_question_locator)
    result = solver_captcha(captcha_question)

    if result:
        id, answer = result['captchaId'], result['code']
        send_answer(captcha_input_locator, answer)
        click_check_button(submit_button_captcha_locator)
        final_message_and_report(success_message_locator, id)

        print("Finished")
    else:
        print("Failed to solve captcha")
