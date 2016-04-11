# Index-service
Indexing micoservice for the IT2901 project 2016\n


Send JSON POST request to 'http://index_service_ip:8001'\n
JSON format:\n
Input: '{'task' : 'getSuggestions', 'word' : str}' Output: '{'suggestions' : ['word1', 'word2', ...]}'\n
Input: '{'task' : 'getArticles', 'word' : str}' Output: '{'articleID' : ['id1', 'id2', ...]}'\n
Input: '{'task' : 'getFrequencyList'}' Output: '{'word1' : freq_word1, 'word2' : freq_word2}'\n
