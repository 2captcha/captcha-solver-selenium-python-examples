from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, parse_qs
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
from twocaptcha import TwoCaptcha
from utilities.proxy_extension import proxies


# CONFIGURATION

url = 'https://2captcha.com/demo/hcaptcha'
apikey = os.getenv('APIKEY_2CAPTCHA')
proxy = {'type': 'HTTP',
         'uri': 'username:password@ip:port'}

solver = TwoCaptcha(apikey)

# LOCATORS

iframe_locator = "//div[@class='h-captcha']//iframe"
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

def parse_proxy_uri(proxy):
    """
    Parses the proxy URI to extract the scheme, login, password, IP, and port.

    Args:
        proxy (dict): Dictionary containing the proxy type and URI.
    Returns:
        tuple: A tuple containing scheme, login, password, IP, and port.
    """
    # Extract proxy type and convert to lowercase
    scheme = proxy['type'].lower
    # Split URI into authentication info and address (IP:port)
    auth, address = proxy['uri'].split('@')
    # Extract login and password from auth
    login, password = auth.split(':')
    # Extract IP and port from address
    ip, port = address.split(':')
    # Return extracted proxy details
    return scheme, login, password, ip, port

def setup_proxy(proxy):
    """
    Sets up the proxy configuration for Chrome browser.

    Args:
        proxy (dict): Dictionary containing the proxy type and URI.

    Returns:
        Options: Configured Chrome options with proxy settings.
    """
    # Initialize Chrome options to modify default Chrome behavior
    chrome_options = webdriver.ChromeOptions()
    # Extract proxy details (scheme, username, password, IP, port)
    scheme, username, password, ip, port = parse_proxy_uri(proxy)
    # Create a proxy extension with the extracted credentials
    proxies_extension = proxies(scheme, username, password, ip, port)
    # Add proxy extension to Chrome options
    chrome_options.add_extension(proxies_extension)
    # Return the configured Chrome options
    return chrome_options

def get_sitekey(locator):
    """
    Extracts the sitekey from the iframe's URL.

    Args:
        locator (str): The XPath locator of the iframe element.
    Returns:
        str: The sitekey value.
    """
    # Switch to the iframe using its XPath locator
    iframe_element = get_clickable_element(locator)
    # Get the iframe's URL from the 'src' attribute
    url = iframe_element.get_attribute('src')
    # Parse the URL to get different components
    parsed_url = urlparse(url)
    # Extract the sitekey from the URL fragment
    params = parse_qs(parsed_url.fragment)
    sitekey = params.get('sitekey', [None])[0]
    # Print the received sitekey for debugging
    print(f"Sitekey received: {sitekey}")
    return sitekey

def solver_captcha(sitekey, url, proxy):
    """
    Solves the hCaptcha using the 2Captcha service.

    Args:
        sitekey (str): The sitekey for the captcha.
        url (str): The URL where the captcha is located.
    Returns:
        dict: The captcha id and the solved captcha code.
    """
    try:
        result = solver.hcaptcha(sitekey=sitekey, url=url, proxy=proxy)
        print(f"Captcha solved. Token: {result['code']}.")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token(captcha_token):
    """
    Sends the captcha token to the hCaptcha iframe and response field.

    Args:
        captcha_token (str): The solved captcha token.
    """
    script = f"""
        document.querySelector('iframe[src*=\\"hcaptcha\\"]').setAttribute('data-hcaptcha-response', '{captcha_token}');
        document.querySelector('[name="h-captcha-response"]').innerText = '{captcha_token}';
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

# Automatically closes the browser after block execution completes
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as browser:
    browser.get(url)
    print("Started")

    # Getting a site key
    sitekey = get_sitekey(iframe_locator)

    if sitekey:
        # Sent captcha to the solution in 2captcha API
        result = solver_captcha(sitekey, url, proxy)

        if result:
            # From the response from the service we get the captcha id and token
            id, token = result['captchaId'], result['code']
            # Applying the token on the page
            send_token(token)
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


