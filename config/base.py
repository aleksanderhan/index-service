# General
stopword_file_path = "stopwords_norwegian.txt"
comm_host = "http://127.0.0.1:9001/" # DHT host
content_module_name = "publish" # Name of the content module in the DHT.

# Postgres database
db_host = "despina.128.no"
db_port = "5432"
db_name = "index"
db_user = "index"
db_pass = ""

server_port = 8001

run_as_daemon = False # Should the indexer be run as a daemon?

# Parser options
tags_to_ignore = ['script'] # Add HTML tag names in quotes to list to ignore.
