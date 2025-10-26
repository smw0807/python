for i in range(1, 20):
  print('T' + str(i).zfill(5))


a = []

def make_serial(n):
  return 'T' + str(n).zfill(5)

for i in range(1, 20):
  a.append(make_serial(i))

print(a)