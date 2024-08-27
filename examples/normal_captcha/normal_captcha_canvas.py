from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/normal"
apikey = os.getenv('APIKEY_2CAPTCHA')


# LOCATORS

img_locator = "._captchaImage_rrn3u_9"
input_captcha_locator = "//input[@id='simple-captcha-field']"
submit_button_captcha_locator = "//button[@type='submit']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_locator(locator):
    """
    Waits for the element specified by the locator to become clickable and returns its web element

    Args:
        locator (str): XPATH locator to find an element on the page
    Returns:
        WebElement: A web element that has become clickable
    """
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def solver_captcha(image, apikey):
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
        result = solver.normal(image)
        print(f"Captcha solved. Code: {result['code']}")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_image_canvas(locator):
    """
    Gets the Base64 representation of an image displayed on a web page using canvas

    Args:
        locator (str): CSS selector for locating an image on a page
    Returns:
        str: Base64 image string
    """

    # JavaScript code to create a canvas, draw an image to the canvas and get its Base64 representation
    canvas_script = """
        function getBase64Image(imgElement) {
            let canvas = document.createElement('canvas');
            canvas.width = imgElement.width;
            canvas.height = imgElement.height;
            let ctx = canvas.getContext('2d');
            ctx.drawImage(imgElement, 0, 0);
            let base64Image = canvas.toDataURL();
            return base64Image;
        }
        return getBase64Image(document.querySelector(arguments[0]));
    """
    base63_image = browser.execute_script(canvas_script, locator)
    return base63_image

def input_captcha_code(locator, code):
    """
    Enters the captcha solution code into the input field on the web page

    Args:
        locator (str): XPATH locator of the captcha input field
        code (str): Captcha solution code
    """
    input_field = get_locator(locator)
    input_field.send_keys(code)
    print("Entered the answer to the captcha")

def click_check_button(locator):
    """
    Clicks the check button on a web page

    Args:
        locator (str): XPATH locator of the captcha verification button
    """
    button = get_locator(locator)
    button.click()
    print("Pressed the Check button")

def final_message(locator):
    """
    Retrieves and prints the final success message.

    Args:
        locator (str): The XPath locator of the success message.
    """
    message = get_locator(locator).text
    print(message)


# MAIN LOGIC

# Automatically closes the browser after block execution completes
with webdriver.Chrome() as browser:
    # Go to page with captcha
    browser.get(url)
    print("Started")

    # Getting captcha image in base64 format
    image_base64 = get_image_canvas(img_locator)

    # Solving captcha using 2Captcha
    code = solver_captcha(image_base64, apikey)

    if code:
        # Entering captcha code
        input_captcha_code(input_captcha_locator, code)
        # Pressing the test button
        click_check_button(submit_button_captcha_locator)
        # Receiving and displaying a success message
        final_message(success_message_locator)

        browser.implicitly_wait(5)
    else:
        print("Failed to solve captcha")

