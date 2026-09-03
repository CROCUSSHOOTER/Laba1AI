numbers = [4, 7, 2, 9, 12, 5, 8, 3]
total = 0
even_numbers = []
squared_evens = []  # Список для хранения квадратов чётных чисел
iterations = 0      # Счётчик итераций цикла
for number in numbers:
    iterations += 1
    if number % 2 == 0:
        even_numbers.append(number)
        sq = number ** 2
        squared_evens.append(sq)
        total += sq
print("Чётные числа:", even_numbers)
print("Квадраты чётных чисел:", squared_evens)
print("Сумма квадратов:", total)
print("Количество итераций цикла:", iterations)
