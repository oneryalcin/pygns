# -*- coding: utf-8 -*-

import json
import logging
import requests


class GNS3Node:
    """
        GNS Node Object
    """

    def __init__(self, project, node_name, node_type, compute_id="local"):
        """
            Create a GNS3 Node : refer to http://api.gns3.net/en/latest/curl.html#create-nodes

        :param compute_id: By default it is "local". This means it’s the local server embed in the GNS3 controller.
        :param node_name: GNS3 Node name
        :param node_type: GNS3 Node Type
        :param project: GNS3 Project object 
        """
        self._compute_id = compute_id
        self._node_name = node_name
        self._node_type = node_type
        self._project = project.get_project_params
        self._nodes_url, self._links_url = project.nodes_url, project.links_url

        data = {
            "name": self._node_name,
            "node_type": self._node_type,
            "compute_id": self._compute_id
        }
        self._response = requests.post(self._nodes_url, data=json.dumps(data))
        params = self.get_node_params()
        self.node_url = '{}/{}'.format(self._nodes_url, params['node_id'])

    def __repr__(self):
        params = self.get_node_params()
        return '{}: name={} node_id={}, node_type={} '.format(self.__class__.__name__,
                                                              params.get('name'),
                                                              params.get('node_id'),
                                                              params.get('node_type'))

    def get_node_params(self):
        """
            Important GNS3 Node Parameters
        :return: 
        """
        node = self._response.json()
        params = {
            'compute_id': node.get('compute_id'),
            'console': node.get('console'),
            'console_host': node.get('console_host'),
            'console_type': node.get('console_type'),
            'name': node.get('name'),
            'node_id': node.get('node_id'),
            'node_type': node.get('node_type'),
            'ports': node.get('ports'),
            'project_id': node.get('project_id'),
            'status': node.get('status'),
        }
        return params

    def link_to(self, local_interface, remote_node, remote_interface, ):
        """
            Connect physically this node to a remote node

        :param local_interface: Interface number Must be a number. For example 0 for Ethernet0
        :param remote_node: GNS3Node object
        :param remote_interface: Interface to physically connect to. Must be a number. For example 0 for Ethernet0
        :return: 
        """

        data = {"nodes":
            [
                {
                    "adapter_number": 0,  # TODO: Need to check this
                    "node_id": self.get_node_params().get('node_id'),
                    "port_number": local_interface
                },
                {
                    "adapter_number": 0,  # TODO: Need to check this
                    "node_id": remote_node.get_node_params().get('node_id'),
                    "port_number": remote_interface
                }
            ]
        }
        response = requests.post(self._links_url, data=json.dumps(data))
        return response.json().get('link_id')

    def get_status(self):
        """
            Get Node Status (started or stopped  
        :return: 
        """
        return self.get_node_params().get('status')

    def start(self):
        """
            Boot up Node
        :return: 
        """
        start_url = self.node_url + '/start'
        response = requests.post(start_url, data="{}")
        return response

    def stop(self):
        """
            Shot down Node
        :return: 
        """
        stop_url = self.node_url + '/stop'
        response = requests.post(stop_url, data="{}")
        return response