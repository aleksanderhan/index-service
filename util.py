#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import logging.config

IP_DELIM = "|"

def parse_node_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="Usage: PORT_TO_USE")
    parser.add_argument("-b", "--bootstrap_node", nargs=2,
                        help="Usage: KNOWN_NODE_IP KNOWN_NODE_PORT")
    return parser.parse_args()

def ips_to_string(ip_list):
    return IP_DELIM.join(ip_list)

def split_ips(ip_as_string):
    return ip_as_string.split(IP_DELIM)

def create_logger(filename):
    logger = logging.getLogger(__name__)
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': filename,
                'formatter': 'standard',
            },
        },

        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True
            }
        }
    })
    return logger
