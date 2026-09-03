numbers = [4, 7, 2, 9, 12, 5, 8, 3]
# 1. Решение генераторным выражением
result_gen = sum(n ** 2 for n in numbers if n % 2 == 0)
# 2. Отдельный список квадратов чётных чисел
even_squares = [n ** 2 for n in numbers if n % 2 == 0]
print("Результат (генератор):", result_gen)
print("Список квадратов чётных чисел:", even_squares)
