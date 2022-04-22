#! /usr/bin/env python3
# Monto support library
# Library functions to help write Monto sources, servers and sinks
# that communicate via a Monto broker.

import json
import os
import sys

try:
    import SublimeMonto.pathlib as pathlib
except ImportError:
    import pathlib

try:
    import SublimeMonto.zmq_compat as zmq
except ImportError:
    import zmq

# Error reporting


def error(msg):
    print('monto: {0!s}'.format(msg))

# Default addresses, can be overridden in .monto
FROMSOURCES_DEFAULT = b'tcp://127.0.0.1:5000'
TOSERVERS_DEFAULT = b'tcp://127.0.0.1:5001'
FROMSERVERS_DEFAULT = b'tcp://127.0.0.1:5002'
TOSINKS_DEFAULT = b'tcp://127.0.0.1:5003'

# Configuration file reading


def monto_config_file_path():
    return pathlib.Path(os.path.expanduser('~/.monto'))


def monto_read_config():
    with monto_config_file_path().open('r') as file:
        try:
            return json.load(file)
        except ValueError as err:
            error('can\'t parse config file as JSON: {0!s}'.format(err))
            sys.exit(3)

# Global configuration
monto_config = monto_read_config()

# Setup communication addresses


def monto_connection_or_default(name, default):
    if 'connections' in monto_config:
        connections = monto_config['connections']
        return connections.get(name, default)
    else:
        return default

FROMSOURCES = monto_connection_or_default('from_sources', FROMSOURCES_DEFAULT)
TOSERVERS = monto_connection_or_default('to_servers', TOSERVERS_DEFAULT)
FROMSERVERS = monto_connection_or_default('from_servers', FROMSERVERS_DEFAULT)
TOSINKS = monto_connection_or_default('to_sinks', TOSINKS_DEFAULT)

# broker

# The Monto broker. Waits for versions to come in from sources. Each version
# is published to the servers. Products from servers are published to the
# sinks.


def broker():
    context = zmq.Context()
    fromsources = context.socket(zmq.REP)
    fromsources.bind(FROMSOURCES)
    toservers = context.socket(zmq.PUB)
    toservers.bind(TOSERVERS)
    fromservers = context.socket(zmq.REP)
    fromservers.bind(FROMSERVERS)
    tosinks = context.socket(zmq.PUB)
    tosinks.bind(TOSINKS)

    poller = zmq.Poller()
    poller.register(fromsources, zmq.POLLIN)
    poller.register(fromservers, zmq.POLLIN)

    messages = {}

    while True:
        # print('broker: waiting')
        ready = dict(poller.poll(500))
        if ready.get(fromsources) == zmq.POLLIN:
            message = fromsources.recv()
            # print('broker: got fromsources->toservers: {0!s}'
            #       .format(message))
            fromsources.send(b'ack')
            # print('broker: sent ack to source')
            # Queue this message as the latest for its source
            version = json.loads(message.decode())
            source = version['source']
            messages[source] = message
            # print('broker: message for {0} queued'.format(source))
        else:
            # Send any messages we have queued up
            # print('broker: sending {0!s} messages'.format(len(messages)))
            for message in messages.values():
                toservers.send(message)
            messages = {}
        if ready.get(fromservers) == zmq.POLLIN:
            message = fromservers.recv()
            # print('broker: got fromservers->tosinks: {0!s}'.format(message))
            fromservers.send(b'ack')
            # print('broker: sent ack to server')
            tosinks.send(message)
            # print('broker: sent product to sinks')

# server

# General handler for writing Monto servers. Every time a version comes in
# server calls func with the contents of the version message as a JSON value.
# func should return a quadruple that contains the name of a product, the
# language that the product is in, the content of the product, and a
# continuation flag. The product, language and content are used to send
# a product. If the continuation flag is True then the server waits for
# another version, otheriwse it returns. If filter is set, this server only
# sends product for versions that have a matching language.


def server(func, filter=None):
    context = zmq.Context()
    toservers = context.socket(zmq.SUB)
    toservers.connect(TOSERVERS)
    toservers.setsockopt(zmq.SUBSCRIBE, b'')
    fromservers = context.socket(zmq.REQ)
    fromservers.connect(FROMSERVERS)
    while True:
        # print('server: waiting for version')
        version_message = toservers.recv().decode()
        version = json.loads(version_message)
        # print('server: got version {0!s}'.format(version))
        if not filter or filter == version['language']:
            # print('server: func produced {0!s}'.format(func(version)))
            (products, contflag) = func(version)
            for product in products:
                respond(fromservers, product)
            if not (contflag):
                return

# respond

# Send a product from a server back to the broker as a JSON message.


def respond(socket, product):
    # print('server: sent product {0!s}'.format(product))
    product_message = json.dumps(product).encode()
    socket.send(product_message)
    # print('server: waiting for ack')
    socket.recv()
    # print('server: got ack')

# send_product

# Send a single product from a server. In general servers should use
# the 'server' function to set up a server loop, but in some cases
# it is useful to be able to send back products separetely. For
# example, if the main server code is going to take some time we
# might want to send a temporary product that notifies the user of
# potential delay.


def send_product(product):
    context = zmq.Context()
    fromservers = context.socket(zmq.REQ)
    fromservers.connect(FROMSERVERS)
    respond(fromservers, product)

# sink

# General handler for writing Monto sinks. Products from servers are
# published to sinks by the broker. Each product is passed as JSON to
# func. func should return a Boolean that indicates whether the sink
# should continue or return. If raw=False (default), func will be passed
# a dict, otherwise func will be passed a 'raw' JSON string.


def sink(func, raw=False):
    context = zmq.Context()
    tosinks = context.socket(zmq.SUB)
    tosinks.connect(TOSINKS)
    tosinks.setsockopt(zmq.SUBSCRIBE, b'')
    while True:
        # print('sink: waiting for product')
        product_message = tosinks.recv().decode()
        product = product_message if raw else json.loads(product_message)
        # print('sink: got product {0!s}'.format(product))
        if not func(product):
            break

# source

# General functionality of Monto sources. Packaged as a class so that
# the source can be used to publish versions from other code.


class MontoSource:
    def __init__(self):
        self.fromsources = None

    def _init_zmq_socket(self):
        self.context = zmq.Context()
        self.fromsources = self.context.socket(zmq.REQ)
        self.fromsources.connect(FROMSOURCES)

    # Send a version message to the Monto broker. The message will be sent as
    # JSON with 'source', 'language', 'contents' and 'selections' fields
    # specified by the arguments. source should be a unique name but doesn't
    # have to reference anything in particular; often it is the name of the
    # file from which the contents came. language should be the name of the
    # language of the contents. The selection is a list of selection objects
    # that contain 'begin' and 'end' fields and defaults to the empty list.

    def publish_version(self, source, language, contents, selections=[]):
        if self.fromsources is None:
            self._init_zmq_socket()
        version = {
            'source': source,
            'language': language.lower(),
            'contents': contents,
            'selections': selections
        }
        # print('source: sent version {0!s}'.format(version))
        version_message = json.dumps(version).encode()
        self.fromsources.send(version_message)
        # print('source: waiting for ack')
        self.fromsources.recv()
        # print('source: got ack')

# Selections

# Return the selection text from a version. If no selection is specified
# return the empty string.


def get_selection_text(version):
    selection_text = ''
    if 'selections' in version:
        contents = version['contents']
        for selection in version['selections']:
            begin = selection['begin']
            end = selection['end']
            selection_text = selection_text + contents[begin:end]
    return selection_text
