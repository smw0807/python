# https://2.python-requests.org/en/master/user/advanced/#id1
# pip install requests

import requests

def fetcher(session, url):
  with session.get(url) as response:
    return response.text

def main():
  #url = "https://naver.com"
  urls = ["https://naver.com", "https://google.com", "https://instagram.com"]

  #session = requests.Session()
  #session.get(url)
  #session.close()

  with requests.Session() as session:
    #result = fetcher(session, url)
    result = [fetcher(session, url) for url in urls]
    print(result)

if __name__ == "__main__":
  main()