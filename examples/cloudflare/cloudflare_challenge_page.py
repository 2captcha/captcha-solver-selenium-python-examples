import os
import time
from seleniumbase import Driver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha


# CONFIGURATION

url = "https://2captcha.com/demo/cloudflare-turnstile-challenge"
apikey = os.getenv("APIKEY_2CAPTCHA")
browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


"""
When a web page first loads, some JavaScript functions and objects (such as window.turnstile) may already be initialized
and executed. If the interception script is launched too late, this may lead to the fact that the necessary parameters
will already be lost, or the script simply will not have time to intercept the right time.
Refreshing the page ensures that everything starts from scratch and you trigger the interception at the right time.
"""
intercept_script = """
    window.__cfTurnstileParams = null;
    window.__cfCallback = null;
    const i = setInterval(() => {
        if (window.turnstile) {
            clearInterval(i);
            const originalRender = window.turnstile.render;
            window.turnstile.render = (a, b) => {
                window.__cfTurnstileParams = {
                    sitekey: b.sitekey,
                    pageurl: window.location.href,
                    data: b.cData,
                    pagedata: b.chlPageData,
                    action: b.action,
                    userAgent: navigator.userAgent,
                };
                window.__cfCallback = b.callback;
                return originalRender ? originalRender(a, b) : undefined;
            };
        }
    }, 50);
"""


# LOCATORS

success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(browser, locator):
    """
    Waits for an element to be clickable and returns it.

    This helper can be copied and reused in other projects that use SeleniumBase.
    """
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def get_captcha_params(browser, script):
    """
    Refreshes the page, injects a JavaScript script to intercept Turnstile parameters, and retrieves them.

    Args:
        browser: The SeleniumBase driver instance.
        script (str): The JavaScript code to be injected.

    Returns:
        dict: The intercepted Turnstile parameters as a dictionary.
    """
    browser.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": script},
    )
    browser.refresh()

    try:
        WebDriverWait(browser, 30).until(
            lambda driver: driver.execute_script("return window.__cfTurnstileParams !== null;")
        )
    except TimeoutException as exc:
        raise TimeoutException("Timed out waiting for Cloudflare Turnstile parameters") from exc

    params = browser.execute_script("return window.__cfTurnstileParams;")
    print("Parameters received")
    return params

def solver_captcha(apikey, params):
    """
    Solves the Turnstile captcha using the 2Captcha service.

    Args:
        apikey (str): The 2Captcha API key.
        params (dict): The intercepted Turnstile parameters.

    Returns:
        str: The solved captcha token.
    """
    solver = TwoCaptcha(apikey)
    try:
        result = solver.turnstile(
            sitekey=params["sitekey"],
            url=params["pageurl"],
            action=params["action"],
            data=params["data"],
            pagedata=params["pagedata"],
            useragent=params["userAgent"],
        )
        print("Captcha solved")
        return result["code"]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token_callback(browser, token):
    """
    Executes the callback function with the given token.

    Args:
        browser: The SeleniumBase driver instance.
        token (str): The solved captcha token.
    """
    browser.execute_script("window.__cfCallback(arguments[0]);", token)
    print("The token is sent to the callback function")

def final_message(browser, locator):
    """
    Retrieves and prints the final success message.

    Args:
        browser: The SeleniumBase driver instance.
        locator (str): The XPath locator of the success message.
    """
    message = get_element(browser, locator).text
    print(message)


def main():
    """
    Runs the demo flow for solving Cloudflare Turnstile challenge using 2Captcha.

    Helper functions (`get_captcha_params`, `solver_captcha`, `send_token_callback`, etc.)
    are designed so they can be copied and reused independently.
    """
    if not apikey:
        raise RuntimeError("Set APIKEY_2CAPTCHA environment variable")

    with Driver(browser="chrome", headless=False, agent=browser_user_agent) as browser:
        browser.get(url)
        print("Started")

        params = get_captcha_params(browser, intercept_script)

        if params:
            token = solver_captcha(apikey, params)

            if token:
                send_token_callback(browser, token)
                final_message(browser, success_message_locator)
                time.sleep(5)
                print("Finished")
            else:
                print("Failed to solve captcha")
        else:
            print("Failed to intercept parameters")


if __name__ == "__main__":
    main()
