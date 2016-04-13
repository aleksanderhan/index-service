# Index-service
Indexing micoservice for the IT2901 project 2016

- Run setup.sh (not working atm) - or install the dependencies manually
- Edit the config.txt to add the database password
- To run the service, type in console: "python run.py"
- Option 1: Makes new tables in the database, clears all current data
- Option 2: If choosen, the service will request all articles from the publish service and index the articles on startup
- Option 3: Starts the service. Listens to POST requests on port 8001. If Option 2 was chosen, 
            the service will index the articles before starting up.
- Option 4: Quit the program.


Send JSON POST request to 'http://index_service_ip:8001'<br />
JSON format:<br />
Input: {'task' : 'getSuggestions', 'word' : str}            Output: {'suggestions' : ['word1', 'word2', ...]}<br />
Input: {'task' : 'getArticles', 'word' : str}               Output: {'articleID' : ['id1', 'id2', ...]}<br />
Input: {'task' : 'getFrequencyList'}                        Output: {'word1' : freq_word1, 'word2' : freq_word2}<br />

The index service requires that the publish module responds with a JSON on the form:  <br />
{"list": [{"id": id1, ""title":title1}, {"id": id2, ""title":title2}, {"id": id2, ""title":title2}, ...]}<br />
when GET requests are sent to 'http://publish_module_ip:port_num/list'<br />

Furthermore publish needs to send JSON POST requests to 'http://index_service_ip:8001' when an article is published, removed or updated on the form:<br />
Input: {'task' : 'publishedArticle', 'articleID' : 'id'}<br />
Input: {'task' : 'removedArticle', 'articleID' : 'id'}<br />
Input: {'task' : 'updatedArticle', articleID' : 'id'}
