# Index-service
Indexing micoservice for the IT2901 project 2016


Send JSON POST request to 'http://index_service_ip:8001'<br />
JSON format:<br />
Input: '{'task' : 'getSuggestions', 'word' : str}' Output: '{'suggestions' : ['word1', 'word2', ...]}'<br />
Input: '{'task' : 'getArticles', 'word' : str}' Output: '{'articleID' : ['id1', 'id2', ...]}'<br />
Input: '{'task' : 'getFrequencyList'}' Output: '{'word1' : freq_word1, 'word2' : freq_word2}'<br />
