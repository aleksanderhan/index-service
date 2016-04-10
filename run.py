# -*- coding: utf-8 -*-
from index_service import IndexService
from node_api import *
import sys


# Main
def main():

    #test_url = "http://instabart.no/"
    stopword_file_path = "stopwords_norwegian.txt"
    index_service = IndexService('despina.128.no', '5432', 'index', 'index', sys.argv[1], stopword_file_path)


if __name__ == "__main__":  
    main()
