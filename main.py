# -*- coding: utf-8 -*-
from indexer import Indexer
from index_database import Database
import sys




# Main
def main():
        
    url1 = "http://folk.ntnu.no/alekh/it2805/02/me.html"
    url2 = "http://folk.ntnu.no/alekh/it2805/06/ex2/form.html"
    url3 = "http://instabart.no/"
    url4 = "http://nanowiki.no/wiki/TFY4235_-_Numerisk_fysikk"


    indexer = Indexer("stopwords_norwegian.txt")
    indexer.make_index(url3)


    index = Database()
    #index.make_tables()

    





if __name__ == "__main__":
    main()