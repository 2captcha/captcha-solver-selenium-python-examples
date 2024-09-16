from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import os
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/clickcaptcha"
apikey = os.getenv('APIKEY_2CAPTCHA')

solver = TwoCaptcha(apikey)

# LOCATORS

img_locator_captcha_for_get = "._widgetForm_1f3oo_26 img"
img_locator_captcha_for_click = "//div[@class='_widget_s7q0j_5']//img"
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

def solver_captcha(image):
    """
    Solves captcha using the 2captcha service and returns the coordinates of points in the image

    Args:
        image (str): Path to the captcha image.
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.coordinates(image)
        print(f"Captcha solved")
        return result
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

def pars_coordinates(answer_to_captcha):
    """
    Parses the coordinates from the captcha solution string.

    Args:
        answer_to_captcha (str): Captcha solution string containing coordinates.
    Returns:
        list: List of dictionaries with 'x' and 'y' coordinates.
    """
    # We remove the "coordinates:" prefix and split the line at the ";" symbol.
    coordinate_pairs = answer_to_captcha.replace("coordinates:", "").split(";")
    # Creating a list of dictionaries
    coordinates_list = []

    for pair in coordinate_pairs:
        # We split each pair of coordinates by a comma and then by the "=" sign.
        coords = pair.split(",")
        coord_dict = {
            "x": int(coords[0].split("=")[1]),
            "y": int(coords[1].split("=")[1])
        }
        coordinates_list.append(coord_dict)

    print("The received response is converted into a list of coordinates")
    return coordinates_list

def clicks_on_coordinates(coordinates_list, img_locator_captcha):
    """
    Clicks on the specified coordinates within the image element using ActionChains.

    Args:
        coordinates_list (list): List of dictionaries with 'x' and 'y' coordinates.
        img_locator_captcha (str): XPath locator of the image element.
    """
    action = ActionChains(browser)

    img_element = get_clickable_element(img_locator_captcha)

    # Getting the initial coordinates of the image element
    location = img_element.location
    img_x = location['x']
    img_y = location['y']

    for coord in coordinates_list:

        # Calculate absolute coordinates on the page
        x_offset = img_x + coord['x']
        y_offset = img_y + coord['y']

        # Click on the calculated coordinates
        action.move_by_offset(x_offset, y_offset).click().perform()

        # We return the cursor back so as not to move the next clicks
        action.move_by_offset(-x_offset, -y_offset)

    print('The coordinates are marked on the image')

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

    image_base64 = get_image_canvas(img_locator_captcha_for_get)
    result = solver_captcha(image_base64)

    if result:

        id, answer_to_captcha = result['captchaId'], result['code']
        coordinates_list = pars_coordinates(answer_to_captcha)
        clicks_on_coordinates(coordinates_list, img_locator_captcha_for_click)
        click_check_button(submit_button_captcha_locator)
        final_message_and_report(success_message_locator, id)

        print("Finished")
    else:
        print("Failed to solve captcha")