import requests

url = "http://localhost:8888/rest/v1/"

#getting an addresl
url_testing = url + "addresses/mvaRDyLUeF4CP7Lu9umbU3FxehyC5nUz3L"
print url_testing
print requests.get(url_testing).json()
