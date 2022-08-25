import pathlib
from pathlib import Path
import json

import logging
import logging.config
logging.config.fileConfig('cfg/logging.ini')
res_logger = logging.getLogger('result_logger')

from config import Data, Settings
from chromedriver import ChromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from _101xp import _101xpBase

def main():
    cfg_data = Data()
    cfg_settings = Settings()
    _101xp = _101xpBase(cfg_data.get)
    driver = ChromeDriver(str(pathlib.Path().resolve()) + "\chromedriver.exe")

    res_logger.info("Session started")
    for d in cfg_data.get:
        auth = _101xp.get_auth(d)
        if auth is not None:
            auth = json.loads(auth)
            if driver.open_url('https://fo4.101xp.com/') is True:
                driver.execute_script("""
                    var date = new Date(new Date().getTime() + 60 * 1000 * 60).toUTCString()
                    document.cookie = "auth_token={}; domain=.101xp.com; path=/; expires=" + date;
                    document.cookie = "refresh_token={}; domain=.101xp.com; path=/; expires=" + date;"""
                        .format(auth['access_token'], auth['refresh_token']))
                if driver.open_url('https://fo4.101xp.com/shop/marathon-1') is True:
                    reward_button = driver.wait_until(5, EC.element_to_be_clickable((By.XPATH, cfg_settings.get['xpath']['reward_button'])))
                    if reward_button is not None:
                        if reward_button.get_property('disabled') is False:
                            reward_button.click()
                    driver.refresh_tab()
                    balance = driver.find_element(By.XPATH, cfg_settings.get['xpath']['reward_balance'])
                    res_logger.info("{}: {}".format(d, balance.text))
    res_logger.info("Session ended")

main()
input("Press ENTER to exit") 