import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

import logging
err_logger = logging.getLogger('error_logger')

# https://conflu.101xp.com/display/apidocs/API+Documentation - api
# https://conflu.101xp.com/pages/viewpage.action?pageId=1409074 - sign in
# https://conflu.101xp.com/display/apidocs/POST+refresh+-+Getting+new+access_token - refresh
# https://conflu.101xp.com/display/apidocs/GET+account - account data

class _101xpBase:
    def __init__(self, login_details):
        self.__domain = "https://101xp.com/"
        self.__login_details = login_details
        self.__client_id = None
        self.__auth_cache = dict()
        if self.__get_client_id() is True:
            self.__load_all_auth_data()

    def __get_client_id(self):
        r = requests.get(self.__domain)
        if r.status_code == 200:
            page = BeautifulSoup(r.text, 'html.parser')
            for tag in page.find_all('script'):
                if tag.string is not None and "regionConfigGlobal" in tag.string:
                    index = tag.string.find('=') + 2
                    data = json.loads(tag.string[index:])
                    self.__client_id = data['client_id']
                    return True
        return False

    def __load_all_auth_data(self):
        for username in self.__login_details:
            self.__load_auth_data(username, self.__login_details[username])

    def __load_auth_data(self, username, password):
        auth_file = self.__format_auth_file_path(username)
        if auth_file.is_file():
            with auth_file.open('r+', encoding='utf-8') as file:
                data = file.readline()
                data_json = json.loads(data)
                if self.__is_access_token_valid(username, data_json['access_token']):
                    self.__auth_cache.update({username: data})
                    return True
                else:
                    p = {
                        'client_id': self.__client_id,
                        'refresh_token': data_json['refresh_token']
                    }
                    r = requests.post('https://auth.101xp.com/refresh', json=p)
                    if r.status_code == 200:
                        new_data = json.loads(r.text)
                        if new_data['status'] == "success":
                            data_json['access_token'] = new_data['access']['access_token']
                            data_json['expires'] = new_data['access']['expires']
                            data_json['expires_in'] = new_data['access']['expires_in']
                            data_json['refresh_token'] = new_data['access']['refresh_token']
                            data = json.dumps(data_json)
                            file.truncate(0)
                            file.seek(0)
                            err_logger.debug("{}: trying to rewrite the auth file. (data: {})".format(username, data))
                            file.write(data)
                            self.__auth_cache.update({username: data})
                            return True
                    elif r.status_code == 400:
                        file.close()
                        auth_file.unlink()
                        return self.__build_auth_file(username, password)
        else:
            return self.__build_auth_file(username, password)
        return False

    def __format_auth_file_path(self, username):
        return Path('data/{}.auth'.format(username))

    def __build_auth_file(self, username, password):
        p = {
            'username': username,
            'password': password,
            'remember': True,
            'client_id': self.__client_id,
            'locale': "ru"
        } 
        r = requests.post('https://auth.101xp.com/signin/', json=p)
        err_logger.debug("{}: login attempt. (status code: {}, data: {})".format(username, r.status_code, p))
        if r.status_code == 200:
            data = json.loads(r.text)
            if data['status'] == "success":
                err_logger.debug("{}: successful login. (response: {})".format(username, data))
                try:
                    json_str = json.dumps(data['access'])
                except KeyError:
                    err_logger.error("{}: auth file not created. ('access' data not exists)".format(username))
                else:
                    auth_file = self.__format_auth_file_path(username)
                    auth_file.parent.mkdir(parents=True, exist_ok=True)
                    with auth_file.open('w', encoding='utf-8') as file:
                        file.write(json_str)
                        self.__auth_cache.update({username: json_str})
                        err_logger.debug("{}: auth file was successfully created.".format(username))
                        return True
        else:
            err_logger.error("{}: login failed. (status code: {})".format(username, r.status_code))
        return False

    def __is_access_token_valid(self, username, access_token):
        p = {
            'access_token': access_token
        }
        r = requests.get('https://api.101xp.com/account', params=p)
        if r.status_code == 200:
            data = json.loads(r.text)
            if data['status'] == "success":
                if data['account']['email'] == username:
                    return True
        return False

    def get_auth(self, username):
        return self.__auth_cache.get(username)