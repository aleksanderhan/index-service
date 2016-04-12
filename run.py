# -*- coding: utf-8 -*-
from index_service import IndexService
from node_api import *
import sys


# Main
def main():

    c = read_config()
    index_service = IndexService(c['db_host'], c['db_port'], c['db_name'], c['db_user'], c['db_pass'], c['stopword_file_path'])


def read_config():
    try:
        with open('config.txt', 'r') as f:
            d = eval(f.read())
        return d
    except:
        raise IOError("config.txt not present")


if __name__ == "__main__":  
    main()
