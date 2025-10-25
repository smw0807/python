print('안녕하세요')

print('안녕하세요', '반가워요', '좋은 아침이에요')

print(1 + 1);

print('1 + 1 =', 1 + 1)

print('안녕하세요' * 5)

name = '송민우 입니다.'
print(name)
print(name[0])
print(name[0:3])

print('--------------------------------')

car = ['K5', 'white', [5000, 6000]]
print(car)

print(car[0])
print(car[0:2])
car[1] = 'black'
print(car)
print(car[2][0])
print(car[2][1])


print('--------------------------------')

car2 = {
  'brand': 'BMW',
  'model': '520d',
  'price': 5000
}
print(car2)
print(car2['brand'])
print(car2['model'])
print(car2['price'])

del car2['brand']
print(car2)

print('--------------------------------')