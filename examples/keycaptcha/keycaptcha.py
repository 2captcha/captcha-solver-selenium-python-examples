import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/keycaptcha"
apikey = os.getenv('APIKEY_2CAPTCHA')


# LOCATORS

iframe_captcha = "//iframe[@name='key-captcha-widget']"
submit_button_captcha_locator = "//button[@type='submit']"
success_message_locator = "//p[contains(@class,'successMessage')]"
captcha_script_for_removal = "https://backs.keycaptcha.com/swfs/cap.js"
captcha_div_for_removal = "//div[@id='div_for_keycaptcha']"


# GETTERS

def get_element(locator):
    """Waits for an element to be clickable and returns it"""
    return WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def switch_to_element(locator):
    """Switches to the iframe by locator"""
    element = get_element(locator)
    browser.switch_to.frame(element)

def get_captcha_parameters():
    """Executes JavaScript to extract captcha variables"""
    variables = browser.execute_script(
        """
        return [
            window.s_s_c_user_id,
            window.s_s_c_session_id,
            window.s_s_c_web_server_sign,
            window.s_s_c_web_server_sign2
        ];
        """
    )
    return variables

def solver_captcha(apikey,
                   s_s_c_user_id,
                   s_s_c_session_id,
                   s_s_c_web_server_sign,
                   s_s_c_web_server_sign2,
                   url):
    """
    Solves the Claudflare Turnstile using the 2Captcha service.

    Args:
        apikey (str): The 2Captcha API key.
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
    Returns:
        str: The solved captcha code.
    """
    solver = TwoCaptcha(apikey)
    try:
        result = solver.keycaptcha(s_s_c_user_id=s_s_c_user_id,
                                   s_s_c_session_id=s_s_c_session_id,
                                   s_s_c_web_server_sign=s_s_c_web_server_sign,
                                   s_s_c_web_server_sign2=s_s_c_web_server_sign2,
                                   url=url)
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def token_usage(captcha_token):
    """
    Use the captcha token to the hidden input field.

    Args:
        captcha_token (str): The solved captcha token.
    """
    script = f"""
        var element = document.querySelector("input[name='capcode']");
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

def remove_element(identifier, by="xpath"):
    """
    Removes an HTML element from the page.

    Args:
        identifier (str): The identifier of the element to be removed.
            - If `by="xpath"`, this should be the XPath of the element.
            - If `by="src"`, this should be the `src` of a <script> tag.
        by (str): The type of identifier ("id", "xpath", or "src").
    """
    if by == "id":
        script = f"""
            var element = document.getElementById('{identifier}');
            if (element) {{
                element.parentNode.removeChild(element);
            }}
        """
    elif by == "xpath":
        script = f"""
            var element = document.evaluate(
                "{identifier}",
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            ).singleNodeValue;
            if (element) {{
                element.parentNode.removeChild(element);
            }}
        """
    elif by == "src":
        script = f"""
            var element = document.querySelector('script[src="{identifier}"]');
            if (element) {{
                element.parentNode.removeChild(element);
            }}
        """
    else:
        raise ValueError("Invalid value for 'by'. Must be 'id', 'xpath', or 'src'.")

    browser.execute_script(script)
    print(f"Element identified by {by}='{identifier}' has been removed")


# MAIN LOGIC

# Automatically closes the browser after block execution completes
with webdriver.Chrome() as browser:
    # Go to page with captcha
    browser.get(url)
    print("Started")

    # Wait for iframe and switch to it
    switch_to_element(iframe_captcha)

    # Get captcha parameters
    s_s_c_user_id, s_s_c_session_id, s_s_c_web_server_sign, s_s_c_web_server_sign2 = get_captcha_parameters()

    # Solving captcha using 2Captcha
    token = solver_captcha(apikey,
                           s_s_c_user_id,
                           s_s_c_session_id,
                           s_s_c_web_server_sign,
                           s_s_c_web_server_sign2,
                           url)

    if token:

        # Insert the token into the field
        token_usage(token)

        # Removing captcha elements
        remove_element(captcha_script_for_removal, by='src')
        remove_element(captcha_div_for_removal, by='xpath')

        # Returning to the main context
        browser.switch_to.default_content()

        # Click the check button
        click_check_button(submit_button_captcha_locator)
        final_message(success_message_locator)

        print("Finished")
    else:
        print("Failed to solve captcha")