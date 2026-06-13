import time
import os
import threading
from concurrent.futures import ProcessPoolExecutor

nums = [50, 63, 32]

def cpu_bound_func(num):
  print(f"{os.getpid()} process | {threading.get_ident()} thread")
  numbers = range(1, num)
  total = 1
  for i in numbers:
    for j in numbers:
      for k in numbers:
        total *= i * j * k
  return total

def main():
  executor = ProcessPoolExecutor(max_workers=10)
  list(executor.map(cpu_bound_func, nums)) # 9 sec

if __name__ == "__main__":
  start = time.time()
  main()
  end = time.time()
  print(end - start)