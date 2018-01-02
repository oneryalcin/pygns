# -*- coding: utf-8 -*-
import json
import logging
import requests
from requests.exceptions import ConnectionError
from pygns.exceptions import GNS3GenericError, GNS3ServerConnectionError, GNS3ProjectExitsError

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


def main():
    import random
    from pprint import  pprint as pp
    server = GNS3Server()
    name = 'test_{}'.format(random.randint(3, 100000))
    project = GNS3Project(name, server)
    print(project)

    node1 = GNS3Node(project, node_name='VPCS 1', node_type='vpcs')
    print(node1)

    node2 = GNS3Node(project, node_name='VPCS 2', node_type='vpcs')
    print(node2)

    link_id = node1.link_to(0, node2, 0)

    print('end')


if __name__ == '__main__':
    main()
