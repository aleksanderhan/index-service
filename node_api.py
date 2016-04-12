#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import print_function # Not needed ?
from node import Node
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.web.server import Site
import cgi
import json
import util

#logger = util.create_logger("node_api.log")


class NodeAPI(Resource):
    """
    Handles the basic routing of requests to the appropirate resource.
    '/{register, unregister}/<service_name>' maps to the 'Register' resource.
    '/<service_name>' maps to the 'Service' resource.
    """

    def __init__(self, node, web_port):
        Resource.__init__(self)
        self.node = node

        reactor.listenTCP(web_port, Site(self))
        logger.info("API listening on: {}".format(web_port))

    def getChild(self, request_str, request):
        if request_str in ['register', 'unregister']:
            return Register(self.node, request_str)
        else:
            return Service(self.node, request_str)


class Register(Resource):
    """
    Handles the registration and unregistration of a service.
    A service is registered in the DHT with the service name as the key,
    and a string of IPs to nodes of the service type as the value.
    """

    def __init__(self, node, register_action):
        Resource.__init__(self)
        self.node = node
        self.register_action = register_action

    def unregister(self, service_name):
        pass

    def async_success(self, result, request):
        if not result:
            logger.info("Action successful!")
            request.setResponseCode(200)
            request.finish()
        else:
            request.setResponseCode(500)
            request.finish()

    def initiate_registration(self, request):
        """
        Determine whether there exists services of the same type, if so append
        the IP of this node to the list of IPs, otherwise create a new list of
        IPs.
        """
        json_data = json.loads(cgi.escape(request.content.read()))
        service_name = str(json_data["value"])

        deferred_result = self.node.get_value(service_name)
        deferred_result.addCallback(self.finish_registration,
                                    request, service_name)

        return NOT_DONE_YET

    def finish_registration(self, result, request, service_name):
        """
        Actually store the IP and service name of the current node, or return
        something that indicates that something went wrong.
        """
        node_ip = self.node.get_ip("wlan0")
        service_ips = []

        if type(result) is dict:
            service_ips.extend(util.split_ips(result[service_name]))

        service_ips.append(node_ip)
        deferred_result = self.node.store_value(service_name,
                                            util.ips_to_string(service_ips))
        deferred_result.addCallback(self.async_success, request)
        logger.info("Registering {} as {}".format(node_ip, service_name))

        return NOT_DONE_YET

    def render_POST(self, request):
        if self.register_action == 'register':
            self.initiate_registration(request)
            return NOT_DONE_YET
        else:
            self.unregister(service_name)
            return 404


class Service(Resource):

    def __init__(self, node, service_name):
        Resource.__init__(self)
        self.service_name = service_name
        self.node = node

    def async_success(self, result, request):
        if not result:
            request.setResponseCode(200)
            request.finish()
        else:
            request.setResponseCode(500)
            request.finish()

    def async_return(self, result, request):
        request.write(json.dumps(result))
        request.finish()

    def render_GET(self, request):
        deferred_result = self.node.get_value(self.service_name)
        deferred_result.addCallback(self.async_return, request)
        return NOT_DONE_YET

    def render_POST(self, request):
        json_data = json.loads(cgi.escape(request.content.read()))
        deferred_result = self.node.store_value(self.service_name,
                                               json_data["value"])
        deferred_result.addCallback(self.async_success, request)
        return NOT_DONE_YET


if __name__ == '__main__':

    args = util.parse_node_arguments()
    node = Node(logger, **vars(args))
    root = NodeAPI(node, 8080)

    reactor.run()
