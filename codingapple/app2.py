cars = 10

if cars > 0 : 
  print('you can order')
else:
  print('you can not order')

cars = ['K5', 'BMW', 'Audi']

if 'K5' in cars:
  print('K5 is in cars')
else:
  print('K5 is not in cars')


print('--------------------------------')

for car in cars:
  print(car)


for i in range(1, 10):
  print(i)

objArray = [
  {
    'name': 'K5',
    'price': 5000
  },
  {
    'name': 'BMW',
    'price': 6000
  },
  {
    'name': 'Audi',
    'price': 7000
  }
]

for obj in objArray: 
  print(obj['name'], obj['price'])