import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

import logging
err_logger = logging.getLogger('error_logger')

class ChromeDriver:
    def __init__(self, path='chromedriver'):
        self.__driver = None
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--log-level=3')
            self.__driver = webdriver.Chrome(executable_path=path, options=chrome_options)
        except WebDriverException:
            err_logger.error("Unable to start a WebDriver session.")
            sys.exit("An error has occurred, see the '{}' file.".format(err_logger.handlers[0].baseFilename))

    def __del__(self):
        if self.__driver is not None:
            self.__driver.quit()

    def open_url(self, url):
        try:
            self.__driver.get(url)
        except WebDriverException as error:
            err_logger.error("Error opening url. (url: {}, error: {})".format(url, error.msg))
            return False
        return True

    def execute_script(self, script, *args):
        try:
            self.__driver.execute_script(script, *args)
        except WebDriverException as error:
            err_logger.error("Something went wrong during script execution. (error: {})".format(error.msg))
            return False
        return True

    def find_element(self, method, query):
        try:
            element = self.__driver.find_element(method, query)
        except WebDriverException as error:
            err_logger.error("Element not found. (error: {}, query: {})".format(error.msg, query))
            return None
        return element

    def find_elements(self, method, query):
        try:
            elements = self.__driver.find_elements(method, query)
        except WebDriverException as error:
            err_logger.error("Elements not found. (error: {}, query: {})".format(error.msg, query))
            return None
        return elements

    def refresh_tab(self):
        return self.execute_script("window.location.reload();")

    def wait_until(self, timeout, method):
        try:
            wait = WebDriverWait(self.__driver, timeout).until(method)
        except WebDriverException as error:
            err_logger.error("WebDraiver wait failure. (error: {})".format(error.msg))
            return None
        return wait

    @property
    def get(self):
        return self.__driver
