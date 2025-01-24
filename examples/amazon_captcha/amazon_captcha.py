import json
import time
from selenium import webdriver
import os
from twocaptcha import TwoCaptcha

# CONFIGURATION
url = "https://sso.nifty.com/sso/login/"
apikey = os.getenv('APIKEY_2CAPTCHA')


# ACTIONS
def get_captcha_parameters():
    """
    Retrieves captcha parameters (key, iv, context and scripts) from a web page.

    The function executes JavaScript in the browser to receive parameters,
    necessary for solving captcha, such as keys and links to scripts.

    Returns:
        dict: Dictionary with captcha parameters (key, iv, context, captcha_script, challenge_script),
              or None if no parameters were found.
    """
    script = """
    return new Promise((resolve) => {
        let counter = 0;
        const MAX_ATTEMPTS = 2000; // Maximum number of attempts (~ 10 seconds at the interval of 5 ms)

        const interval = setInterval(() => {
            if (window.CaptchaScript) {
                clearInterval(interval); // Stop interval if CaptChascript is found

                let params = window.gokuProps || {}; // Obtaining the basic parameters of captcha
                Array.from(document.querySelectorAll('script')).forEach(s => {
                    const src = s.getAttribute('src');
                    if (src && src.includes('captcha.js')) params.captcha_script = src;
                    if (src && src.includes('challenge.js')) params.challenge_script = src;
                });
                resolve(params); // Return of parameters
            }
            if (counter++ > MAX_ATTEMPTS) {
                clearInterval(interval); // Continuing the search after the limit exceeds
                resolve(null); // If the parameters are not found, return null
            }
        }, 5);
    });
    """
    try:
        params = browser.execute_script(script) # Executing JavaScript via Selenium
        if not params:
            print("Captcha parameters not found.")
        return params
    except Exception as e:
        print(f"Error retrieving captcha parameters: {e}")
        return None

def solver_captcha(params):
    """
    Solves the captcha using the 2Captcha service.

    Args:
        params (dict): Captcha parameters retrieved from the page.

    Returns:
        dict: The solved captcha token or None if failed.
    """
    # Check for the presence of all necessary parameters
    if not all(k in params for k in ["key", "iv", "context", "captcha_script", "challenge_script"]):
        print("Missing required captcha parameters!")
        return None

    solver = TwoCaptcha(apikey, pollingInterval=1) # Initializing the 2Captcha client
    try:
        print("Sending captcha parameters to 2Captcha...")
        # Send the captcha parameters to solve
        result = solver.amazon_waf(
            url=url,
            sitekey=params["key"],
            iv=params["iv"],
            context=params["context"],
            challenge_script=params["challenge_script"],
            captcha_script=params["captcha_script"]
        )
        print("Captcha solved successfully.")
        return json.loads(result['code']) # Return the lattice token
    except Exception as e:
        print(f"Error solving captcha: {e}")
        return None

def submit_captcha(token):
    """
    Submits the solved captcha token using JavaScript.

    Args:
        token (dict): Solved captcha token (captcha_voucher).
    """
    try:
        # JavaScript to send captcha token
        js_script = f"""
        return new Promise(async (resolve, reject) => {{
            try {{
                const response = await ChallengeScript.submitCaptcha("{token['captcha_voucher']}");
                resolve(response); // Finish with a successful response
            }} catch (error) {{
                reject(error); // Completing with an error
            }}
        }});
        """
        browser.execute_script(js_script) # Executing JavaScript via Selenium
    except Exception as e:
        print(f"Error during captcha submission: {e}")

# MAIN LOGIC

with webdriver.Chrome() as browser:
    try:
        # Go to page with captcha
        browser.get(url)
        print("Started")

        # Retrieving captcha parameters
        params = get_captcha_parameters()
        if not params:
            print("Failed to retrieve captcha parameters.")
            exit(1)

        # Solving captcha using 2Captcha
        token = solver_captcha(params)
        if not token:
            print("Failed to solve captcha.")
            exit(1)

        # Sending a solved token to the server
        submit_captcha(token)
        print("Captcha process completed.")

        print("Finished")
        # A slight delay to observe the result
        time.sleep(15)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.quit() # Closing the browser after completion of work
