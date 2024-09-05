# Code examples of solving captchas in Python using Selenium

Examples of solving captchas using the Python programming language, and the [2captcha-python] and [Selenium] libraries.

This repository contains examples of automation of solving the most popular types of captcha, such as [reCAPTCHA][recaptcha-v2-demo], [Cloudflare Turnstile][cloudflare-turnstile], [Cloudflare Challenge page][cloudflare-challenge], [normal captcha][normal-captcha-demo], [hCaptcha][hcaptcha-demo] and others. Selenium library is used for browser automation in the examples. The [2Captcha] service is used for solving captchas, therefore, for the correct work of the examples it is necessary to have an account in the [captcha solving service][2Captcha] service with a positive balance, or you can try to test it using [sandbox] mode to solve captchas manually.
 Also, for `proxy` examples to work correctly, you need to have your own `proxy` and set it in the example code. The examples of captcha automation solving use captchas located on the [captchas demo pages](https://2captcha.com/demo).

We have our own proxies that we can offer you. [Buy residential proxies] to avoid restrictions and blocks. [Quick start].
Official 2Captcha webpage for [selenium captcha solver](https://2captcha.com/p/selenium-captcha-solver).

- [Code examples of solving captchas in python using selenium](#code-examples-of-solving-captchas-in-python-using-selenium)
  - [Usage](#usage)
    - [Clone](#clone)
    - [Install dependencies](#install-dependencies)
    - [Configure](#configure)
    - [Run](#run)
  - [Captcha solving code examples](#captcha-solving-code-examples)
    - [reCAPTCHA examples](#recaptcha-examples)
      - [reCAPTCHA V2](#recaptcha-v2)
      - [reCAPTCHA V2 + proxy](#recaptcha-v2--proxy)
      - [reCAPTCHA V2 with callback](#recaptcha-v2-with-callback)
      - [reCAPTCHA V2 with callback + proxy](#recaptcha-v2-with-callback--proxy)
      - [reCAPTCHA V3](#recaptcha-v3)
      - [reCAPTCHA V3 (extended script)](#recaptcha-v3-extended-script)
      - [reCAPTCHA V3 + proxy](#recaptcha-v3--proxy)
    - [hCaptcha examples](#hcaptcha-examples)
      - [hCaptcha](#hcaptcha)
      - [hCaptcha + proxy](#hcaptcha--proxy)
    - [Cloudflare examples](#cloudflare-examples)
      - [Cloudflare Turnstile](#cloudflare-turnstile)
      - [Cloudflare Challenge page](#cloudflare-challenge-page)
    - [Text captcha example](#text-captcha-example)
    - [Normal captcha examples](#normal-captcha-examples)
      - [Normal captcha (screenshot)](#normal-captcha-screenshot)
      - [Normal captcha (canvas)](#normal-captcha-canvas)
      - [Normal captcha (canvas + additional-parameters)](#normal-captcha-canvas--additional-parameters)
    - [Coordinates example](#coordinates-example)
    - [MTCaptcha example](#mtcaptcha)
  - [General algorithm for solving captchas using 2captcha service](#general-algorithm-for-solving-captchas-using-2captcha-service)
  - [Get in touch](#get-in-touch)
  - [License](#license)
    - [Graphics and Trademarks](#graphics-and-trademarks)

## Usage

### Clone:

```
git clone git@github.com:2captcha/captcha-solver-selenium-python-examples.git
cd captcha-solver-selenium-python-examples
```

### Install dependencies:

`pip install -r requirements.txt`

### Configure:

Set the `APIKEY` environment variable. You can get the `APIKEY` value in your personal [2captcha][2captcha-enterpage] account.

`export APIKEY=your_api_key`

### Run:

Go to the examples directory and run the required example.

Running the `recaptcha_v2.py` example:

```
cd examples/reCAPTCHA
python recaptcha_v2.py
```

## Captcha solving code examples

Examples of captcha solving using Selenium are described below.

### reCAPTCHA examples

reCAPTCHA is one of the most popular captcha types. reCAPTCHA has different types. The approach to solving reCAPTCHA depends on the type of reCAPTCHA. reCAPTCHA is divided into two types, first type is reCAPTCHA V2 and second type is reCAPTCHA V3. Type reCAPTCHA V3 is characterized by the fact that the captcha task is not displayed and the captcha independently determines the user's rating, if as a result of checking the rating will be lower than required, then successfully pass the captcha will not be possible. Type reCAPTCHA V2 is characterized by the fact that the user is offered to pass the task with captcha, for example, to select all traffic lights on the displayed image.

Additionally, there are subspecies of reCAPTCHA such as:

- [reCAPTCHA V2 Invisible][recaptcha-v2-invisible-demo]
- [reCAPTCHA V2 with callback][recaptcha-v2-callback-demo]
- [reCAPTCHA V2 Enterprise][recaptcha-v2-enterprise-demo]
- [reCAPTCHA V3 Enterprise][recaptcha-v3-enterprise-demo]

In practice, you can often see two types of reCAPTCHA on a page. For example reCAPTCHA V3 and reCAPTCHA V2. First the user passes reCAPTCHA V3, then depending on the result of passing reCAPTCHA V3 the user may be shown reCAPTCHA V2 captcha. In case of successful passing of reCAPTCHA V3 the reCAPTCHA V2 captcha is not displayed, and in case of unsuccessful passing of reCAPTCHA V3 the user will be offered to pass additional verification with reCAPTCHA V2.

The reCAPTCHA bypass can also be complicated by the presence of additional parameters such as `data-s`. Example [described in the article](https://2captcha.com/blog/google-search-recaptcha).

There are several fundamentally different ways to bypass reCAPTCHA V2:

- **Token based solution** - Solution of reCAPTCHA V2 on [token based](https://2captcha.com/2captcha-api#solving_recaptchav2_new). In this case our worker receives a captcha sent to the service and solves it. The answer of the captcha is a token to be applied on the captcha page.

- **Grid** - Solution of reCAPTCHA V2 using [Grid method](https://2captcha.com/2captcha-api#grid). In this case it is necessary to send to the service the source image with captcha, and the instruction to the captcha. The worker will receive the image and select the quadrants matching the requirements. The response returns the numbers of quadrants corresponding to the instructions sent. When solving captchas with this method, it is necessary to independently retrieve the original captcha image and instructions to the captcha. Then after receiving the answer, you need to click on the required squares by yourself.

  This method can help to bypass complex reCAPTCHA implementations, for example, when it is difficult to figure out how to apply the token, or in cases when captcha traversal is intentionally complicated. The advantages of this approach are that the built-in logic of applying the token works when the token is applied. When solving in this way, it is necessary to pay attention to browser automation anti-detection, and take measures to hide the fact of browser automation.

- **Coordinates** - Solution of reCAPTCHA V2 using [coordinates method](https://2captcha.com/2captcha-api#coordinates). In this case it is necessary to send a screenshot of the captcha to the service. The instruction to the captcha can be contained in the captcha image itself or can be sent as a separate parameter. The employee receives the image and clicks with the mouse on the corresponding coordinates on the image. The response returns the coordinates of the clicks that correspond to the sent instructions. In this case it is also necessary to retrieve images and instructions to them independently, then, after receiving the response, it is necessary to click on the received coordinates independently.

   This method can help to bypass complex reCAPTCHA implementations, for example, when it is difficult to figure out how to apply the token, or in cases when captcha traversal is intentionally complicated. The advantages of this approach are that the built-in logic of applying the token works when the token is applied. When solving in this way, it is necessary to pay attention to browser automation anti-detection, and take measures to hide the fact of browser automation.

- **Audio** - Solution of reCAPTCHA V2 with [audio method](https://2captcha.com/2captcha-api#audio). For people with disabilities reCAPTCHA has the functionality of passing captcha with the help of audio task. This method can be used as an alternative to the previous ones. To use this audio method, you need to capture an audio recording containing the task, then send the audio recording to the service using [audio method](https://2captcha.com/2captcha-api#audio). The response will contain the text contained in the audio recording. After receiving the response you need to use it on the page.

#### reCAPTCHA V2

Token based reCAPTCHA V2 solution.

This example implements bypassing reCAPTCHA V2 captcha located on the page https://2captcha.com/demo/recaptcha-v2. Selenium library is used to automate browser actions. After receiving the solution result (token), the script automatically uses the received answer on the page with the captcha.

**Source code:** [`./examples/reCAPTCAHA/recaptcha_v2.py`](./examples/reCAPTCHA/recaptcha_v2.py)

#### reCAPTCHA V2 + `proxy`

Token based reCAPTCHA V2 solution.

This example implements bypassing reCAPTCHA V2 captcha located on the page https://2captcha.com/demo/recaptcha-v2 using `proxy`. Selenium library is used to automate browser actions. After receiving the solution result (token), the script automatically uses the received answer on the page with the captcha.

From time to time when bypassing captchas there is a need to use proxies, in such cases it is important to use the same proxies both when loading the page and when solving the captcha itself. To do this, you need to pass the parameters of the `proxy` used with the parameters of the captcha, so that the captcha would be loaded and solved from the same ip address.

For the example to work correctly, you need to set the value of the `proxy` used in the example code.

**Source code:** [`./examples/reCAPTCAHA/recaptcha_v2_proxy.py`](./examples/reCAPTCHA/recaptcha_v2_proxy.py)

#### reCAPTCHA V2 with callback

Token based reCAPTCHA V2 with callback solutions.

In these examples implements bypassing reCAPTCHA V2 with callback located on the page https://2captcha.com/demo/recaptcha-v2-callback using different realizations. Selenium library is used to automate browser actions. After receiving the solution result (token), the script automatically uses the received answer on the page with the captcha.

Sometimes there's no submit button and a callback function is used isntead. The function is executed when reCAPTCHA is solved.

In this repository you can find three example implementations of the reCAPTCHA V2 with callback solution:

1. [recaptcha_v2_callback_variant1.py](./examples/reCAPTCHA/recaptcha_v2_callback_variant1.py) - The value of the `sitekey` parameter is extracted from the page code automaticly. The value of the `callback` function “`verifyDemoRecaptcha()`” is specified manually. The name of the “`verifyDemoRecaptcha()`” function may be different when bypassing captcha on another page. You need to fugure out the name of the `callback` function yourself and specify it in the code.

    **Source code:** [`./examples/reCAPTCAHA/recaptcha_v2_callback_variant1.py`](./examples/reCAPTCHA/recaptcha_v2_callback_variant1.py)

2. [recaptcha_v2_callback_variant2.py](./examples/reCAPTCHA/recaptcha_v2_callback_variant2.py) - Captcha parameters are determined automatically with the help of JavaScript script executed on the page.

    **Source code:** [`./examples/reCAPTCAHA/recaptcha_v2_callback_variant2.py`](./examples/reCAPTCHA/recaptcha_v2_callback_variant2.py)
  
3. [recaptcha_v2_callback_proxy.py](./examples/reCAPTCHA/recaptcha_v2_callback_proxy.py) - [This example describe below](#recaptcha-v2-with-callback--proxy).

    **Source code:** [`./examples/reCAPTCAHA/recaptcha_v2_callback_proxy.py`](./examples/reCAPTCHA/recaptcha_v2_callback_proxy.py)

#### reCAPTCHA V2 with callback + proxy

Token based reCAPTCHA V2 with callback solutions using proxy.

In these example implements bypassing reCAPTCHA V2 with callback located on the page https://2captcha.com/demo/recaptcha-v2-callback using proxy. Selenium library is used to automate browser actions. After receiving the solution result (token), the script automatically uses the received answer on the page with the captcha.

For the example to work correctly, you need to set the value of the `proxy` used in the example code.

**Source code:** [`./examples/reCAPTCAHA/recaptcha_v2_callback_proxy.py`](./examples/reCAPTCHA/recaptcha_v2_callback_proxy.py)

#### reCAPTCHA v3

Token based reCAPTCHA V3 solution.

This example demonstrates bypassing the reCAPTCHA V3 challenge on the page https://2captcha.com/demo/recaptcha-v3. The Selenium library automates browser interactions. Captcha parameters are determined automatically with the help of JavaScript script executed on the page. Upon obtaining the solution (token), the script programmatically applies the response to the captcha page.

**Source code:** [`./examples/reCAPTCAHA/recaptcha_v3.py`](./examples/reCAPTCHA/recaptcha_v3.py)

#### reCAPTCHA v3 (extended script)

Token based reCAPTCHA V3 solution.

This example demonstrates bypassing the reCAPTCHA V3 challenge on the page https://2captcha.com/demo/recaptcha-v3. The Selenium library automates browser interactions. Captcha parameters are determined automatically with the help of JavaScript extended script executed on the page. Upon obtaining the solution (token), the script programmatically applies the response to the captcha page.

**Source code:** [`./examples/reCAPTCAHA/recaptcha_v3_extended_js_script.py`](./examples/reCAPTCHA/recaptcha_v3_extended_js_script.py)

#### reCAPTCHA v3 + proxy

Token based reCAPTCHA V3 solution using proxy.

This example demonstrates bypassing the reCAPTCHA V3 challenge on the page https://2captcha.com/demo/recaptcha-v3. The Selenium library automates browser interactions. Captcha parameters are determined automatically with the help of JavaScript script on the page. Upon obtaining the solution (token), the script programmatically applies the response to the captcha page. A proxy is use during the captcha-solving process.

For the example to work correctly, you need to set the value of the `proxy` used in the example code.

**Source code:** [`./examples/reCAPTCAHA/recaptcha_v3_proxy.py`](./examples/reCAPTCHA/recaptcha_v3_proxy.py)

### hCaptcha examples

Below are examples of automating the hCaptcha solution using the Selenium library.

In addition to the token, the captcha answer also constain a `userAgent` value, we recommend that you use you received `userAgent` value when applying the token.

#### hCaptcha

Token based hCaptcha solutions.

In these example implements bypassing hCaptcha located on the page https://2captcha.com/demo/hcaptcha. Selenium library is used to automate browser actions. After receiving the solution result (token), the script automatically uses the received answer on the page with the captcha.

For the example to work correctly, you need to set the value of the `proxy` used in the example code.

**Source code:** [`./examples/hCaptcha/hcaptcha.py`](./examples/hCaptcha/hcaptcha.py)

#### hCaptcha + proxy

Token based hCaptcha solutions using `proxy`.

In these example implements bypassing hCaptcha located on the page https://2captcha.com/demo/hcaptcha using `proxy`. Selenium library is used to automate browser actions. After receiving the solution result (token), the script automatically uses the received answer on the page with the captcha.

**Source code:** [`./examples/hCaptcha/hcaptcha_proxy.py`](./examples/hCaptcha/hcaptcha_proxy.py)

### Cloudflare examples

Cloudflare is one of the most popular captcha types. Cloudflare has two types. First type is [Cloudflare Turnstile][cloudflare-turnstile] and second type is [Cloudflare challenge][cloudflare-challenge] page.

- [Cloudflare Turnstile][cloudflare-turnstile] - In this case, the captcha is displayed on the target page, the captcha badge is embedded in the target page code. An example of implementation is shown on the page https://2captcha.com/demo/cloudflare-turnstile.

- [Cloudflare challenge][cloudflare-challenge] - In this case, a redirect to the challenge page will occur to pass the captcha, as implemented here https://2captcha.com/demo/cloudflare-turnstile-challenge.

The approach to bypassing these two types is different, so you need to determine which type of Cloudflare you are facing. Read more about bypassing Cloudflare captcha types below.

#### Cloudflare Turnstile

Token-based Cloudflare Turnstile solution.

This example demonstrates how to bypass the Cloudflare Turnstile CAPTCHA located on the page https://2captcha.com/demo/cloudflare-turnstile. The Selenium library is used to automate browser actions and retrieve CAPTCHA parameters. To solve this type of Cloudflare CAPTCHA, it is necessary to send parameters such as `pageurl` and `sitekey` to the [2Captcha API](https://2captcha.com/2captcha-api#turnstile). After receiving the solution result (token), the script automatically uses the received answer on the page.

**Source code:** [`./examples/cloudflare/cloudflare_turnstile.py`](./examples/cloudflare/cloudflare_turnstile.py)


#### Cloudflare Challenge page

Token-based Cloudflare Challenge page solution.

This example demonstrates how to bypass the Cloudflare Challenge located on the page https://2captcha.com/demo/cloudflare-turnstile-challenge. The Selenium library is used to automate browser actions and retrieve CAPTCHA parameters. To solve this type of Cloudflare CAPTCHA, it is necessary to send parameters such as `pageurl`,`sitekey`, `action`, `data`, `pagedata`, `useragent` to the [2Captcha API](https://2captcha.com/2captcha-api#turnstile). After receiving the solution result (token), the script automatically uses the received answer on the page.

> [!NOTE]
> When a web page first loads, some JavaScript functions and objects (such as `window.turnstile`) may already be initialized and executed. If the interception script is launched too late, this may lead to the fact that the necessary parameters will already be lost, or the script simply will not have time to intercept the right moment. Refreshing the page ensures that everything starts from scratch and you trigger the interception at the right time.

**Source code:** [`./examples/cloudflare/cloudflare_challenge_page.py`](./examples/cloudflare/cloudflare_challenge_page.py)

### Text captcha example

Text captcha solutions.

In these example implements bypassing Text captcha located on the page https://2captcha.com/demo/text. Selenium library is used to automate browser actions. After receiving the solution result (token), the script automatically uses the received answer on the page with the captcha.

**Source code:** [`./examples/text_captcha/text_captcha.py`](./examples/text_captcha/text_captcha.py)

### Normal captcha examples

Normal captcha is also one of the most popular types of captcha. Below are two examples of Normal captcha solutions. The examples differ in the way the captcha image is extracted from the page.

#### Normal captcha (screenshot)

Normal captcha solutions.

In these example implements bypassing Normal captcha located on the page https://2captcha.com/demo/normal. Selenium library is used to automate browser actions. After receiving the solution result, the script automatically uses the received answer on the page with the captcha. In this example, the captcha image is retrieved by creating a screenshot of the captcha image.

**Source code:** [`./examples/normal_captcha/normal_captcha_screenshot.py`](./examples/normal_captcha/normal_captcha_screenshot.py)

#### Normal captcha (canvas)

Normal captcha solutions.

In these example implements bypassing Normal captcha located on the page https://2captcha.com/demo/normal. Selenium library is used to automate browser actions. After receiving the solution result, the script automatically uses the received answer on the page with the captcha. In this example, the captcha image is extracted using `canvas`.

**Source code:** [`./examples/normal_captcha/normal_captcha_canvas.py`](./examples/normal_captcha/normal_captcha_canvas.py)

#### Normal captcha (canvas + additional parameters)

Normal captcha solutions using additional parameters.

In these example implements bypassing Normal captcha located on the page https://2captcha.com/demo/normal. Selenium library is used to automate browser actions. The captcha is sent using additional parameters such as `numeric`, `minLen`, `maxLen`, `lang`. Sending additional parameters allows you to increase the accuracy of the captcha solution. After receiving the solution result, the script automatically uses the received answer on the page with the captcha. In this example, the captcha image is extracted using `canvas`.

**Source code:** [`./examples/normal_captcha/normal_captcha_screenshot_params.py`](./examples/normal_captcha/normal_captcha_screenshot_params.py)

### Coordinates example

A coordinate captcha is a captcha in which you need to click on the image  in corresponding to the instructions for the image.This example implements a bypass of the coordinate captcha located on the page https://2captcha.com/demo/clickcaptcha.  The Selenium library is used to automate browser actions. After receiving the result of the solution, the script automatically clicks on the received coordinates on the captcha image.

**Source code:** [`./examples/coordinates/coordinates.py`](./examples/coordinates/coordinates.py)

### MTCaptcha

Token based MTCaptcha solutions.

In these example, we demonstrate bypassing MTCaptcha located on the page https://2captcha.com/demo/mtcaptcha. The Selenium library is utilized to automate browser actions. Upon receiving the solution result (token), the script automatically applies the obtained answer on the page containing the captcha.

**Source code:** [`./examples/mtcaptcha/mtcaptcha.py`](./examples/mtcaptcha/mtcaptcha.py)

## General algorithm for solving captchas using [2captcha] service

The process of bypassing captcha with the help of 2captcha service can be divided into several main stages:

1. **Identifying the type of captcha on the target page.**

   You need to determine what type of captcha is located on the target page. In general, this is not difficult, as the captcha is usually clearly displayed on the page. In more complex cases, there may be several types of captcha on the page, or the captcha may be displayed not immediately but after certain actions.

   You can try using [2captcha-detector] tool to simplify captcha search on the page.

2. **Searching for captcha parameters.**

   After you have determined the type of captcha you need to solve, you need to find a list of mandatory parameters for this type of captcha in the documentation. Next, you need to find these captcha parameters on the target page.

   Mostly these captcha parameters are static, but in some cases they are dynamic. In case you have dynamic captcha parameters, you need to get new values every time you receive a captcha, more details about it are described in the API documentation.

3. **Sending captcha to 2Captcha API.**

   After you have successfully defined the captcha parameters, you need to send the captcha parameters to the API [2captcha]. In a successful case, the captcha id will be returned in response, which means that the captcha has been successfully passed to the worker for solving.

   If the captcha parameters were sent correctly, the worker will solve the captcha you sent and you will be able to get the answer to the captcha using the received captcha id.

   If for some reason the captcha could not be solved, you will receive a answer describing the error instead of the solution.

   In the examples, the [2captcha-python] library is used to interact with the [2Captcha] API. There are also official libraries for other programming languages.

   List of official libraries:

   - [2captcha-python]
   - [2captcha-javascript]
   - [2captcha-java]
   - [2captcha-csharp]
   - [2captcha-php]
   - [2captcha-go]
   - [2captcha-ruby]
   - [2captcha-cpp]

4. **Getting a captcha response.**

   Use the captcha id obtained in the previous step to get the captcha solution.

5. **Using of captcha answer.**

   After receiving the captcha solution, you need to correctly use the captcha solution on the target page. Standard methods of using the solution are described in the documentation and on [demo pages][2captcha-demo].

   In case the standard methods do not work, you need to figure out how the solution is used on the page. To do this, try to solve the captcha manually and understand how the captcha answer is used on the page.

## Get in touch

<a href="mailto:support@2captcha.com"><img src="https://github.com/user-attachments/assets/539df209-7c85-4fa5-84b4-fc22ab93fac7" width="80" height="30"></a>
<a href="https://2captcha.com/support/tickets/new"><img src="https://github.com/user-attachments/assets/be044db5-2e67-46c6-8c81-04b78bd99650" width="81" height="30"></a>

## License

The code in this repository is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

### Graphics and Trademarks

The graphics and trademarks included in this repository are not covered by the MIT License. Please contact <a href="mailto:support@2captcha.com">support</a> for permissions regarding the use of these materials.

<!-- Shared links -->
[2captcha-demo]: https://2captcha.com/demo
[recaptcha-v2-demo]: https://2captcha.com/demo/recaptcha-v2
[recaptcha-v2-invisible-demo]: https://2captcha.com/demo/recaptcha-v2-invisible
[recaptcha-v2-callback-demo]: https://2captcha.com/demo/recaptcha-v2-callback
[recaptcha-v2-enterprise-demo]: https://2captcha.com/demo/recaptcha-v2-enterprise
[recaptcha-v3-enterprise-demo]: https://2captcha.com/demo/recaptcha-v3-enterprise
[cloudflare-turnstile]: https://2captcha.com/demo/cloudflare-turnstile
[cloudflare-challenge]: https://2captcha.com/demo/cloudflare-turnstile-challenge
[normal-captcha-demo]: https://2captcha.com/demo/normal
[hcaptcha-demo]: https://2captcha.com/demo/hcaptcha
[2captcha]: https://2captcha.com
[2captcha-detector]: https://2captcha.com/blog/detector
[2captcha-enterpage]: https://2captcha.com/enterpage
[sandbox]: https://2captcha.com/2captcha-api#sandbox
[2captcha-python]: https://github.com/2captcha/2captcha-python
[2captcha-javascript]: https://github.com/2captcha/2captcha-javascript
[2captcha-java]: https://github.com/2captcha/2captcha-java
[2captcha-csharp]: https://github.com/2captcha/2captcha-csharp
[2captcha-php]: https://github.com/2captcha/2captcha-php
[2captcha-go]: https://github.com/2captcha/2captcha-go
[2captcha-ruby]: https://github.com/2captcha/2captcha-ruby
[2captcha-cpp]: https://github.com/2captcha/2captcha-cpp
[selenium]: https://pypi.org/project/selenium/
[Quick start]: https://2captcha.com/proxy?openAddTrafficModal=true
[Buy residential proxies]: https://2captcha.com/proxy/residential-proxies
