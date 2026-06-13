# https://docs.aiohttp.org/en/stable/
# pip install aiohttp~=3.7.3


# - aiohttp — 비동기 HTTP 클라이언트 라이브러리 (requests의 async 버전)
# - asyncio — Python 비동기 I/O 프레임워크
# - time — 실행 시간 측정용
import aiohttp
import asyncio
import time

# 단일 URL 비동기 요청
# - async def → 코루틴 함수
# - session.get(url) → HTTP GET 요청을 보냄
# - async with → 응답 객체를 컨텍스트 매니저로 관리 (자동 close)
# - await response.text() → 응답 body를 텍스트로 읽을 때까지 대기 (non-blocking)
async def fetcher(session, url):
  async with session.get(url) as response:
    return await response.text()

async def main():
  #url = "https://naver.com"
  urls = ["https://naver.com", "https://google.com", "https://instagram.com"] * 10

  async with aiohttp.ClientSession() as session:
    #result = fetcher(session, url)
    result = await asyncio.gather(*[fetcher(session, url) for url in urls])
    # result = await fetcher(session, urls[0])
    print(result)

if __name__ == "__main__":
  start = time.time()
  asyncio.run(main())
  end = time.time()
  print(end - start)