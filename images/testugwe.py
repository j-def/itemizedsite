import requests

jsondata = {
    'command': 'list',
    'site': 'mercari',
    'item': 'timmy45qittkrkfnvaayzqfghehskdzg'
}
print(requests.post('http://127.0.0.1:8354/api/queue/add/', json=jsondata).text)