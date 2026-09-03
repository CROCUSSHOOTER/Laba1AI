numbers = [4, 7, 2, 9, 12, 5, 8, 3]
even_numbers = []
total_sum = 0
count = 0
for number in numbers:
    if number % 2 == 0:
        even_numbers.append(number)
        total_sum += number
        count += 1
average = total_sum / count if count > 0 else 0.0
print("Императивный стиль:")
print("Чётные числа:", even_numbers)
print("Сумма чётных:", total_sum)
print("Количество чётных:", count)
print("Среднее значение:", average)
