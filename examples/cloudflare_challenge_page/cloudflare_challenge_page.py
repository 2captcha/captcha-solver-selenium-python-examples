import os
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from twocaptcha import TwoCaptcha



# CONFIGURATION

url = "https://2captcha.com/demo/cloudflare-turnstile-challenge"
apikey = os.getenv('APIKEY_2CAPTCHA')


"""
When a web page first loads, some JavaScript functions and objects (such as window.turnstile) may already be initialized
and executed. If the interception script is launched too late, this may lead to the fact that the necessary parameters 
will already be lost, or the script simply will not have time to intercept the right moment. Refreshing the page ensures
that everything starts from scratch and you trigger the interception at the right time.
"""
intercept_script = """ 
    console.clear = () => console.log('Console was cleared')
    const i = setInterval(()=>{
    if (window.turnstile)
     console.log('success!!')
     {clearInterval(i)
         window.turnstile.render = (a,b) => {
          let params = {
                sitekey: b.sitekey,
                pageurl: window.location.href,
                data: b.cData,
                pagedata: b.chlPageData,
                action: b.action,
                userAgent: navigator.userAgent,
            }
            console.log('intercepted-params:' + JSON.stringify(params))
            window.cfCallback = b.callback
            return        } 
    }
},50)    
"""

# LOCATORS

success_message_locator = "//p[contains(@class,'successMessage')]"


# GETTERS

def get_element(locator):
    """Waits for an element to be clickable and returns it"""
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))


# ACTIONS

def get_captcha_params(script):
    """
    Refreshes the page, injects a JavaScript script to intercept Turnstile parameters, and retrieves them.

    Args:
        script (str): The JavaScript code to be injected.

    Returns:
        dict: The intercepted Turnstile parameters as a dictionary.
    """
    browser.refresh() # Refresh the page to ensure the script is applied correctly

    browser.execute_script(script) # Inject the interception script

    time.sleep(5) # Allow some time for the script to execute

    logs = browser.get_log("browser") # Retrieve the browser logs
    params = None
    for log in logs:
        if "intercepted-params:" in log['message']:
            log_entry = log['message'].encode('utf-8').decode('unicode_escape')
            match = re.search(r'intercepted-params:({.*?})', log_entry)
            if match:
                json_string = match.group(1)
                params = json.loads(json_string)
                break
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
        result = solver.turnstile(sitekey=params["sitekey"],
                                  url=params["pageurl"],
                                  action=params["action"],
                                  data=params["data"],
                                  pagedata=params["pagedata"],
                                  useragent=params["userAgent"])
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token_callback(token):
    """
    Executes the callback function with the given token.

    Args:
        token (str): The solved captcha token.
    """
    script = f"cfCallback('{token}')"
    browser.execute_script(script)
    print("The token is sent to the callback function")

def final_message(locator):
    """
    Retrieves and prints the final success message.

    Args:
        locator (str): The XPath locator of the success message.
    """
    message = get_element(locator).text
    print(message)


# MAIN LOGIC

chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/126.0.0.0 Safari/537.36")
# Set logging preferences to capture only console logs
chrome_options.set_capability("goog:loggingPrefs", {"browser": "INFO"})

with webdriver.Chrome(service=Service(), options=chrome_options) as browser:
    browser.get(url)
    print("Started")

    params = get_captcha_params(intercept_script)

    if params:
        token = solver_captcha(apikey, params)

        if token:
            send_token_callback(token)
            final_message(success_message_locator)
            time.sleep(5)
            print("Finished")
        else:
            print("Failed to solve captcha")
    else:
        print("Failed to intercept parameters")
