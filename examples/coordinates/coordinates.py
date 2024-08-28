from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/clickcaptcha"
apikey = os.getenv('APIKEY_2CAPTCHA')


# LOCATORS

img_locator_captcha_for_get = "._widgetForm_1f3oo_26 img"
img_locator_captcha_for_click = "//div[@class='_widget_s7q0j_5']//img"
submit_button_captcha_locator = "//button[@type='submit']"
success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(locator):
    """Waits for an element to be clickable and returns it"""
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
        result = solver.coordinates(image)
        print(f"Captcha solved. Coordinates received")
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

    img_element = get_element(img_locator_captcha)

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
    button = get_element(locator)
    button.click()
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

# Automatically closes the browser after block execution completes
with webdriver.Chrome() as browser:
    # Go to page with captcha
    browser.get(url)
    print("Started")

    # Getting captcha image in base64 format
    image_base64 = get_image_canvas(img_locator_captcha_for_get)

    answer_to_captcha = solver_captcha(image_base64, apikey)

    if answer_to_captcha:

        coordinates_list = pars_coordinates(answer_to_captcha)

        clicks_on_coordinates(coordinates_list, img_locator_captcha_for_click)

        click_check_button(submit_button_captcha_locator)

        final_message(success_message_locator)

        browser.implicitly_wait(5)
        print("Finished")
    else:
        print("Failed to solve captcha")