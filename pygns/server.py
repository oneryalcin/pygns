# -*- coding: utf-8 -*-

import logging
import requests
from requests.exceptions import ConnectionError
from pygns.exceptions import GNS3ServerConnectionError

GNS3_API_VERSION = 'v2'


class GNS3Server:
    """
        GNS3 Server Instance: 
        http://api.gns3.net/en/latest/curl.html#sample-session-using-curl
    """

    def __init__(self, server_address='localhost', server_port='3080'):
        self._server_address = server_address
        self._server_port = server_port
        self._log = logging.getLogger(__name__)
        self._url = 'http://{}:{}/{}/'.format(server_address, server_port, GNS3_API_VERSION)
        try:
            self._response = requests.get(self._url)
        except ConnectionError as e:
            raise GNS3ServerConnectionError(e)

    def __str__(self):
        return '{} at {}'.format(self.__class__.__name__, self._url)

    def __repr__(self):
        return '{}: GNS3 Server running at {} port {}'.format(self.__class__.__name__,
                                                              self._server_address,
                                                              self._server_port)

    def get_version(self):
        """
            Display GNS3 Server Version
        :return: 
        """
        url = self._url + 'version'
        response = requests.get(url)
        return response.json().get('version')

    def list_computes(self):
        """
             list the computes node where we can run our nodes on this server
             http://api.gns3.net/en/latest/curl.html#list-computes
        :return: 
        """
        url = self._url + 'computes'
        response = requests.get(url)
        return response.json()

    def api_endpoint(self):
        """
            Get API URL base        
        :return: 
        """
        return self._url
