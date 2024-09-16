from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
from twocaptcha import TwoCaptcha
from utilities.proxy_extension import proxies

# CONFIGURATION

url = "https://2captcha.com/demo/recaptcha-v2"
apikey = os.getenv('APIKEY_2CAPTCHA')
proxy = {'type': 'HTTPS',
         'uri': 'username:password@ip:port'}

solver = TwoCaptcha(apikey)

# LOCATORS

sitekey_locator = "//div[@id='g-recaptcha']"
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

def parse_proxy_uri(proxy):
    """
    Parses the proxy URI to extract the scheme, login, password, IP, and port.

    Args:
        proxy (dict): Dictionary containing the proxy type and URI.
    Returns:
        tuple: A tuple containing scheme, login, password, IP, and port.
    """
    scheme = proxy['type'].lower
    auth, address = proxy['uri'].split('@')
    login, password = auth.split(':')
    ip, port = address.split(':')
    return scheme, login, password, ip, port

def setup_proxy(proxy):
    """
    Sets up the proxy configuration for Chrome browser.

    Args:
        proxy (dict): Dictionary containing the proxy type and URI.

    Returns:
        Options: Configured Chrome options with proxy settings.
    """
    chrome_options = webdriver.ChromeOptions()
    scheme, username, password, ip, port = parse_proxy_uri(proxy)
    proxies_extension = proxies(scheme, username, password, ip, port)
    chrome_options.add_extension(proxies_extension)
    return chrome_options

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

def solver_captcha(sitekey, url, proxy):
    """
    Solves the reCaptcha using the 2Captcha service.

    Args:
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
        proxy (dict): Dictionary containing the proxy settings.
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.recaptcha(sitekey=sitekey, url=url, proxy=proxy)
        print(f"Captcha solved")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(captcha_token):
    """
    Sends the captcha token to the reCaptcha response field.

    Args:
        captcha_token (str): The solved captcha token.
        """
    script = f"""
        document.querySelector('[id="g-recaptcha-response"]').innerText = '{captcha_token}';
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

# Configure Chrome options with proxy settings
chrome_options = setup_proxy(proxy)

with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as browser:

    browser.get(url)
    print('Started')

    sitekey = get_sitekey(sitekey_locator)

    if sitekey:
        result = solver_captcha(sitekey, url, proxy)

        if result:
            id, token = result['captchaId'], result['code']
            send_token(token)
            click_check_button(submit_button_captcha_locator)
            final_message_and_report(success_message_locator, id)
            print("Finished")
        else:
            print("Failed to solve captcha")
    else:
        print("Sitekey not found")

