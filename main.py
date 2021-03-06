import datetime
import emails
import os
import timeit
import time
import urllib.request

from selenium import webdriver
from random import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def withDefault(options, keyword, default):
    try:
        return options[keyword]
    except Exception:
        return default

# Arguments:
#   - browser
#   - options:
#       - injectExtention -> Defines if custom extention should be injected || Default = False
#       - agents -> Defiynes 'agents' || Default = 'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0'
#       - windowSize -> Defines window size || Default = '1024,860'
#       - phantomJSpath -> Defines path for phantomJS || Default is empty string
#       - firefoxProfilePath -> Defines path for firefox profile || Default is empty string
#       - shouldUseProxy -> Tells the function if proxy should be used || Default = False
#       - proxyIp -> Defines proxy Ip || Default is empty string
#       - proxyPort -> Defines proxy Port || Default is empty string
#       - proxyUser -> Defines proxy User || Default is empty string
#       - proxyPass -> Defines proxy Pass || Default is empty string
# Returns:
#   - driver
def initBrowser(browser, options={}):
    injectExtention = withDefault(options, 'injectExtention', False)
    agents = withDefault(options, 'agents', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0')
    windowSize = withDefault(options, 'windowSize', '1024,860')
    phantomJSpath = withDefault(options, 'phantomJSpath', '')
    firefoxProfilePath = withDefault(options, 'firefoxProfilePath', '')
    shouldUseProxy = withDefault(options, 'shouldUseProxy', False)
    proxyIp = withDefault(options, 'proxyIp', '')
    proxyPort = withDefault(options, 'proxyPort', '')
    proxyUser = withDefault(options, 'proxyUser', '')
    proxyPass = withDefault(options, 'proxyPass', '')

    # Headless
    if browser == 'headless':
        service_args = []

        if shouldUseProxy:
            proxy_args = [
                '--proxy={0}:{1}'.format(proxyIp, proxyPort),
                '--proxy-type=https',
                '--ignore-ssl-errors=true',
                '--web-security=false',
                '--proxy-auth={0}:{1}'.format(proxyUser, proxyPass)
                ]
            service_args.extend(proxy_args)

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (agents)

        driver = webdriver.PhantomJS(
            phantomJSpath,
            desired_capabilities=dcap,
            service_args=service_args
        )

        driver.set_window_size(1200,1024)
        return driver


    # Firefox
    if browser == 'firefox':
        profile = webdriver.FirefoxProfile(firefoxProfilePath)
        profile.set_preference("general.useragent.override", agents)
        if injectExtention == True:
            profile.add_extension(extension=CONFIG['ROOT_DIR'] + "/firefox_extentions/inject-javascript")

        return webdriver.Firefox(profile)

# Arguments:
#   - driver
#   - element
# Returns:
#   - element
def scrollToElement(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)

# Arguments:
#   - driver
#   - jquerySelector
# Returns:
#   - Number of elements
def countElements(driver, jquerySelector):
	return driver.execute_script("return window.jQuery('" + jquerySelector + "').length;")

# Arguments:
#   - driver
#   - jquerySelector
#   - id
def injectIdToElement(driver, jquerySelector, id):
	print("jquerySelector: {0}".format(jquerySelector))
	print("id: {0}".format(id))
	driver.execute_script("window.jQuery('{0}').attr('id', '{1}');".format(jquerySelector, id))

# Arguments:
#   - driver
#   - jquerySelector
#   - target
def changeLinkTarget(driver, jquerySelector, target):
	driver.execute_script("window.jQuery('{0}').setAttribute('target', '{1}');".format(jquerySelector, target))

# Arguments:
#   - element
#   - elementName
def downloadElement(element, elementName):
    src = element.get_attribute('src')
    urllib.request.urlretrieve(src, elementName)
    time.sleep(2)

# Arguments:
#   - driver
#   - method
#   - selector
#   - quitOnFail -> Defines if script should quit on except || Default = False
# Returns:
#   - element or undefined
def useElement(driver, method, selector, quitOnFail=False, mailData={}):
    def handleException(error):
        print('useElement failed: {0}'.format(error))
        sendMail(driver, 'Bot notification', "useElement failed: {0}".format(error), True, mailData)

        if quitOnFail:
            driver.close()
            quit()

    if method == 'xpath':
        try:
            element = driver.find_element_by_xpath(selector)
            return element
        except Exception as error:
            handleException(error)

    if method == 'id':
        try:
            element = driver.find_element_by_id(selector)
            return element
        except Exception as error:
            handleException(error)

    if method == 'class':
        try:
            element = driver.find_element_by_class_name(selector)
            return element
        except Exception as error:
            handleException(error)

    if method == 'name':
        try:
            element = driver.find_element_by_name(selector)
            return element
        except Exception as error:
            handleException(error)



# Arguments:
#   - driver
#   - method
#   - selector
# Returns:
#   - True or False
def isElementPresent(driver, method, selector):
    if method == 'xpath':
        try:
            element = driver.find_element_by_xpath(selector)
            return element.is_displayed()
        except:
            return False

    if method == 'id':
        try:
            element = driver.find_element_by_id(selector)
            return element.is_displayed()
        except:
            return False

    if method == 'class':
        try:
            element = driver.find_element_by_class(selector)
            return element.is_displayed()
        except:
            return False


# Arguments:
#   - driver
#   - element
#   - options:
#       - shouldPrint -> Defines if coordinates of click should be printed || Default = False
# Returns:
#   - undefined
def clickOnRandomSpotOnElement(driver, element, options={}):
    #desctruct options
    shouldPrint = withDefault(options, 'shouldPrint', False)

    actions = ActionChains(driver)
    pointOfOffsetX = randint(1, int(abs(element.size['width'])))
    pointOfOffsetY = randint(1, int(abs(element.size['height'])))

    if shouldPrint:
        print(pointOfOffsetX)
        print(pointOfOffsetY)

    actions.move_to_element_with_offset(element, pointOfOffsetX, pointOfOffsetY).click(element).perform()

# Arguments:
#   - driver
#   - options:
#       - name -> Name of the prefix of the screenshot  || Default = 'debug'
# Returns:
#   - screenshot name
def buildScreenshotWithTimestamp(driver, options={}):
    #desctruct options
    name = withDefault(options, 'name', 'debug')

    date = datetime.datetime.now().isoformat()
    screenshotName = '{0}_{1}.png'.format(name, date)
    driver.save_screenshot(screenshotName)
    print('New screenshot named "{0}" was created'.format(screenshotName))

    return screenshotName

# Arguments:
#   - driver
#   - subject -> Subject of mail
#   - content -> Content of mail
#   - shouldAddDebugScreenshot -> Determines if email should contain debug screenshot
#   - options:
#       - mail_from -> Defines 'from' field for email sending || Default = 'bots@gmail.com'
#       - mail_receiver -> Defines 'to/receiver' field for email sending || Default = ''
#       - mail_username -> Defines username for email SMTP || Default = ''
#       - mail_password -> Defines password for email SMTP || Default = ''
# Returns:
#   - undefined
def sendMail(driver, subject, content, shouldAddDebugScreenshot, options={}):
    #destruct options
    FROM = withDefault(options, 'mail_from', 'bots@gmail.com')
    TO = withDefault(options, 'mail_receiver', '')
    SUBJECT = subject
    CONTENT = content
    USERNAME = withDefault(options, 'mail_username', '')
    PASSWORD = withDefault(options, 'mail_password', '')

    # create html email
    html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
    html +='"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml">'
    html +='<body style="font-size:12px;font-family:Verdana"><p>'
    html += str(CONTENT)
    html +='</p>'
    html += "</body></html>"
    message = emails.html( html=html,
                           subject=SUBJECT,
                           mail_from=('Bot notifications', FROM))

    if shouldAddDebugScreenshot:
        screenshotName = buildScreenshotWithTimestamp(driver, {
        'name': 'debugging'
        })
        message.attach(data=open(screenshotName, 'rb'), filename=screenshotName)

    try:
        response = message.send(to=('Jup someone', TO),
                smtp={'host':'smtp.gmail.com',
                'port': 465,
                'ssl': True,
                'user': USERNAME,
                'password': PASSWORD
                })
        print(response)
    except Exception as error:
        print(error)
        print("failed to send mail")

# Arguments:
#   - driver
#   - username
#   - password
# Returns:
#   - undefined
def loginFacebook(driver, username, password):
    driver.get("https://www.facebook.com")
    useElement(driver, 'xpath', '//*[@id="email"]', True).send_keys(username)
    useElement(driver, 'xpath', '//*[@id="pass"]', True).send_keys(password)
    useElement(driver, 'id', 'loginbutton', True).click()

# Arguments:
#   - start_time
# Returns:
#   - Number of seconds passed
def secondsPassed(start_time):
    return timeit.default_timer() - start_time
