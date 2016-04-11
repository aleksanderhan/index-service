# Index-service
Indexing micoservice for the IT2901 project 2016

- run setup.sh (not working atm) - or install the dependencies manually
- to run the service write: "python run.py <database_password>"
- Option 1: Makes new tables in the database, clears all current data
- Option 2: If choosen, the service will request all articles from the publish service and index the articles on startup
- Option 3: Starts the service. Listens to POST requests on port 8001. If Option 2 was chosen, 
            the service will index the articles before starting up.


Send JSON POST request to 'http://index_service_ip:8001'<br />
JSON format:<br />
Input: '{'task' : 'getSuggestions', 'word' : str}' Output: '{'suggestions' : ['word1', 'word2', ...]}'<br />
Input: '{'task' : 'getArticles', 'word' : str}' Output: '{'articleID' : ['id1', 'id2', ...]}'<br />
Input: '{'task' : 'getFrequencyList'}' Output: '{'word1' : freq_word1, 'word2' : freq_word2}'<br />
