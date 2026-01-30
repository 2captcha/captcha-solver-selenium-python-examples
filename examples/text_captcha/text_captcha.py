import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/text"


# LOCATORS

captcha_question_locator = "//label[@for='text-captcha-field']"
captcha_input_locator = "//input[@id='text-captcha-field']"
submit_button_captcha_locator = "//button[@type='submit']"
success_message_locator = "//p[contains(@class,'successMessage')]"

# GETTERS

def get_element(browser, locator):
    """
    Waits for an element to be clickable and returns it.

    This helper can be copied and reused in other projects that use Selenium.
    """
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def get_captcha_question(browser, locator):
    """
    Extracts the captcha question text from the specified element.

    Args:
        browser (webdriver): The Selenium WebDriver instance.
        locator (str): XPath locator of the captcha question element
    Returns:
        str: Text of the captcha question
    """
    question_element = get_element(browser, locator)
    text_question = question_element.text
    return text_question

def solver_captcha(question, apikey):
    """
    Solves a captcha using the 2Captcha service and returns the solution code

    Args:
        image (str): Path to the captcha image
        apikey (str): API key to access the 2Captcha service
    Returns:
        str: Captcha solution code, if successful, otherwise None
    """
    solver = TwoCaptcha(apikey)
    try:
        result = solver.text(question)
        print(f"Captcha solved. Code: {result['code']}")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_answer(browser, locator, answer):
    """
    Inputs the captcha answer into the specified input field.

    Args:
        browser (webdriver): The Selenium WebDriver instance.
        locator (str): XPath locator of the input field
        answer (str): Captcha answer
    """
    input_element = get_element(browser, locator)
    input_element.send_keys(answer)
    print("Entering the answer to captcha")

def click_check_button(browser, locator):
    """
    Clicks the check button on a web page

    Args:
        browser (webdriver): The Selenium WebDriver instance.
        locator (str): XPATH locator of the captcha verification button
    """
    button = get_element(browser, locator)
    button.click()
    print("Pressed the Check button")

def final_message(browser, locator):
    """
    Retrieves and prints the final success message.

    Args:
        locator (str): The XPath locator of the success message.
    """
    message = get_element(browser, locator).text
    print(message)


def main():
    """
    Runs the demo flow for solving a text captcha using 2Captcha.

    Helper functions (`get_captcha_question`, `solver_captcha`, `send_answer`, etc.)
    are designed so they can be copied and reused independently.
    """
    apikey = os.getenv("APIKEY_2CAPTCHA")
    if not apikey:
        raise RuntimeError("Set APIKEY_2CAPTCHA environment variable")

    # Automatically closes the browser after block execution completes
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as browser:
        # Go to page with captcha
        browser.get(url)
        print("Started")

        # Get the text of the captcha question
        captcha_question = get_captcha_question(browser, captcha_question_locator)

        # Solve the captcha using 2Captcha
        answer = solver_captcha(captcha_question, apikey)

        if answer:
            # Enter the captcha answer
            send_answer(browser, captcha_input_locator, answer)

            # Click the check button
            click_check_button(browser, submit_button_captcha_locator)

            # Retrieve and display the success message
            final_message(browser, success_message_locator)

            # Explicit pause to observe the result
            time.sleep(5)
            print("Finished")
        else:
            print("Failed to solve captcha")


if __name__ == "__main__":
    main()
