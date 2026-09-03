class NumberCollection:
    def __init__(self, numbers):
        self._numbers = list(numbers)
    def get_even_numbers(self):
        return [n for n in self._numbers if n % 2 == 0]
    def sum_even_squares(self):
        return sum(n ** 2 for n in self._numbers if n % 2 == 0)
    def count_even_numbers(self) -> int:
        return len(self.get_even_numbers())
    def find_maximum(self):
        return max(self._numbers) if self._numbers else None
    def calculate_average(self) -> float:
        return sum(self._numbers) / len(self._numbers) if self._numbers else 0.0
# Создание первого объекта
coll1 = NumberCollection([4, 7, 2, 9, 12, 5, 8, 3])
print("Коллекция 1 — Кол-во чётных:", coll1.count_even_numbers())
print("Коллекция 1 — Максимум:", coll1.find_maximum())
print("Коллекция 1 — Среднее:", coll1.calculate_average())
# Создание второго объекта
coll2 = NumberCollection([10, 15, 20, 25])
print("Коллекция 2 — Чётные:", coll2.get_even_numbers())
print("Коллекция 2 — Среднее:", coll2.calculate_average())
