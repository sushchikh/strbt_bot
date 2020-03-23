import requests
url = 'http://stroybatinfo.ru/test/IMG_20200229_122430.jpg'
r = requests.get(url)

with open('./../img/test.jpg', 'wb') as f:
    f.write(r.content)
print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)