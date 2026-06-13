import time

def delivery(name, mealtime):
  print(f"{name}에게 배달 완료!")
  time.sleep(mealtime)
  print(f"{name} 식사 완료, {mealtime}시간 소요...")
  print(f"{name} 그릇 수거 완료")

def main():
  delivery("A", 3)
  delivery("B", 3)
  delivery("C", 4)


if __name__ == "__main__":
  start = time.time()
  main()
  end = time.time()
  print(end - start)

# A에게 배달 완료!
# A 식사 완료, 3시간 소요...
# A 그릇 수거 완료
# B에게 배달 완료!
# B 식사 완료, 3시간 소요...
# B 그릇 수거 완료
# C에게 배달 완료!
# C 식사 완료, 4시간 소요...
# C 그릇 수거 완료
# 10.007935047149658