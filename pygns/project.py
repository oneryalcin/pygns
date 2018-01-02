# -*- coding: utf-8 -*-

import json
import logging
import requests
from pygns.exceptions import GNS3GenericError, GNS3ProjectExitsError


class GNS3Project:
    """
        Create a new GNS3 Project
        http://api.gns3.net/en/latest/curl.html#create-project
    """

    def __init__(self, project_name, gns3server):
        """

        :param project_name: Project name
        :param gns3server: GNS3Server object
        """
        self._project_name = project_name
        self._api_endpoint = gns3server.api_endpoint()
        self._url = '{}projects'.format(self._api_endpoint)
        data = {"name": project_name}
        self._response = requests.post(self._url, data=json.dumps(data))
        status_code = self._response.status_code
        if status_code == 409:
            raise GNS3ProjectExitsError('File {}.gns3 already exists.'.format(project_name))
        elif status_code == 404:
            raise GNS3GenericError('This Error is not expected, please contact developer')
        else:
            params = self.get_project_params()
            self.base_url = '{}projects/{}'.format(params['server_end_point'], params['project_id'])
            self.nodes_url = self.base_url + '/nodes'
            self.links_url = self.base_url + '/links'

    def __repr__(self):
        params = json.dumps(self.get_project_params(), indent=4, sort_keys=True)
        return '{}: {}'.format(self.__class__.__name__, params)

    def get_project_params(self):
        """
            GNS3 Project params
        :return: 
        """
        r = self._response.json()
        params = {
            'server_end_point': self._api_endpoint,
            'project_id': r.get('project_id'),
            'filename': r.get('filename'),
            'path': r.get('path'),
            'status': r.get('status'),
        }
        return params

    def get_all_links(self):
        """
            List all links in the project
        :return: 
        """
        links_url = "{}/links".format(self._project_url)
        print(links_url)
        response = requests.get(links_url).json()
        return json.dumps(response, indent=4, sort_keys=True)
