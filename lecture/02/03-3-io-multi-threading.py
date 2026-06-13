# https://docs.python.org/3.7/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
import requests
import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor

def fetcher(params):
  print(params)
  session = params[0]
  url = params[1]
  print(f"{os.getpid()} process | {threading.get_ident()} url : {url}")
  with session.get(url) as response:
    return response.text
  
def main():
  urls = ["https://apple.com", "https://google.com"] * 50

  executor = ThreadPoolExecutor(max_workers=10)

  with requests.Session() as session:
    params = [(session, url) for url in urls]
    results = list(executor.map(fetcher, params))
    print(results)

if __name__ == "__main__":
  start = time.time()
  main()
  end = time.time()
  print(end - start) # thread 1 = 20 sec, thread 10 = 4 sec
