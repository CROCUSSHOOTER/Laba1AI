import sys
import os
import unittest

# ==============================================================================
# 1. МОДУЛЬ VALIDATION (university_rating/validation.py)
# ==============================================================================
def validate_scores(scores):
    """Возвращает проверенную копию последовательности баллов."""
    if not isinstance(scores, (list, tuple)):
        raise TypeError("scores должен быть списком или кортежем")
    checked = []
    for score in scores:
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError("Балл должен быть числом")
        if not 0 <= score <= 100:
            raise ValueError("Балл должен быть от 0 до 100")
        checked.append(float(score))
    return checked

def validate_student(student):
    """Проверяет обязательные поля записи студента."""
    if not isinstance(student, dict):
        raise TypeError("Запись студента должна быть словарём")
    required = {"id", "name", "scores"}
    missing = required - student.keys()
    if missing:
        raise ValueError(f"Отсутствуют поля: {sorted(missing)}")

# ==============================================================================
# 2. МОДУЛЬ CALCULATIONS (university_rating/calculations.py)
# ==============================================================================
PASSING_AVERAGE = 50.0

def calculate_average(scores):
    """Возвращает среднее значение или None для пустой последовательности."""
    return sum(scores) / len(scores) if scores else None

def determine_status(average):
    """Возвращает статус допуска по среднему баллу."""
    if average is None:
        return "нет данных"
    return "допущен" if average >= PASSING_AVERAGE else "не допущен"

def calculate_letter_grade(average):
    """
    Расширение (Вариант 1): Преобразует средний балл в буквенную оценку.
    Шкала:
    - 90 - 100    : A
    - 75 - 89.99  : B
    - 60 - 74.99  : C
    - 50 - 59.99  : D
    - 0  - 49.99  : F
    """
    if average is None:
        return "N/A"
    if average >= 90:
        return "A"
    elif average >= 75:
        return "B"
    elif average >= 60:
        return "C"
    elif average >= 50:
        return "D"
    else:
        return "F"

# ==============================================================================
# 3. МОДУЛЬ RATING (university_rating/rating.py)
# ==============================================================================
def build_student_result(student):
    """Формирует новую итоговую запись одного студента без изменения исходной."""
    validate_student(student)
    scores = validate_scores(student["scores"])
    average = calculate_average(scores)
    return {
        "id": student["id"],
        "name": student["name"],
        "average": average,
        "status": determine_status(average),
        "grade": calculate_letter_grade(average)  # Расширение Вариант 1
    }

def _sort_key(item):
    """Ключ для сортировки рейтинга по убыванию."""
    average = item["average"]
    return average is not None, average or 0.0

def build_rating(students):
    """Возвращает отсортированный рейтинг, не изменяя исходный список."""
    results = [build_student_result(item) for item in students]
    return sorted(results, key=_sort_key, reverse=True)

# ==============================================================================
# 4. МОДУЛЬ REPORT (university_rating/report.py)
# ==============================================================================
def format_average(value):
    """Форматирует средний балл с точностью до двух знаков."""
    return "-" if value is None else f"{value:.2f}"

def format_rating(rows):
    """Преобразует результаты рейтинга в текстовый отчёт."""
    lines = ["Рейтинг группы"]
    for position, row in enumerate(rows, start=1):
        average = format_average(row["average"])
        grade = row.get("grade", "-")
        lines.append(
            f"{position}. {row['name']}: {average} (Оценка: {grade}) — {row['status']}"
        )
    return "\n".join(lines)

# ==============================================================================
# 5. МОДУЛЬ MAIN (university_rating/main.py)
# ==============================================================================
def load_demo_data():
    """Демонстрационный набор данных."""
    return [
        {"id": 101, "name": "Amina", "scores": [88, 92, 79]},
        {"id": 102, "name": "Dias", "scores": [45, 52, 48]},
        {"id": 103, "name": "Mira", "scores": []},
        {"id": 104, "name": "Kairat", "scores": [95, 98, 100]},
        {"id": 105, "name": "Elena", "scores": [65, 70, 68]}
    ]

def run_application():
    """Главная функция для демонстрации работы проекта."""
    students = load_demo_data()
    rating = build_rating(students)
    print(format_rating(rating))

# ==============================================================================
# 6. МОДУЛЬ ТЕСТОВ (tests/test_rating.py)
# ==============================================================================
class RatingTests(unittest.TestCase):

    def test_empty_average(self):
        """Проверка пустых оценок."""
        self.assertIsNone(calculate_average([]))

    def test_status_boundary(self):
        """Проверка границ допуска."""
        self.assertEqual(determine_status(49.99), "не допущен")
        self.assertEqual(determine_status(50), "допущен")

    def test_invalid_score(self):
        """Проверка исключений при некорректных баллах."""
        with self.assertRaises(ValueError):
            validate_scores([80, 101])
        with self.assertRaises(TypeError):
            validate_scores([80, True])
        with self.assertRaises(TypeError):
            validate_scores([80, "90"])

    def test_source_is_not_changed(self):
        """Проверка неизменяемости исходного списка."""
        students = [{"id": 1, "name": "Test", "scores": [70, 80]}]
        before = [{"id": 1, "name": "Test", "scores": [70, 80]}]
        build_rating(students)
        self.assertEqual(students, before)

    # Тесты для Индивидуального задания (Вариант 1)
    def test_letter_grade_assignment(self):
        """Проверка корректности буквенной оценки."""
        self.assertEqual(calculate_letter_grade(95.0), "A")
        self.assertEqual(calculate_letter_grade(90.0), "A")
        self.assertEqual(calculate_letter_grade(89.9), "B")
        self.assertEqual(calculate_letter_grade(75.0), "B")
        self.assertEqual(calculate_letter_grade(60.0), "C")
        self.assertEqual(calculate_letter_grade(50.0), "D")
        self.assertEqual(calculate_letter_grade(49.9), "F")
        self.assertEqual(calculate_letter_grade(None), "N/A")

    def test_build_student_result_includes_grade(self):
        """Проверка наличия буквенной оценки в структуре студента."""
        student = {"id": 1, "name": "Ali", "scores": [90, 100, 95]}
        result = build_student_result(student)
        self.assertIn("grade", result)
        self.assertEqual(result["grade"], "A")

# ==============================================================================
# ТОЧКА ВХОДА ДЛЯ ЗАПУСКА ВСЕХ ЗАДАЧ
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("1. ВЫПОЛНЕНИЕ ОСНОВНОГО ПРИЛОЖЕНИЯ")
    print("=" * 60)
    run_application()
    
    print("\n" + "=" * 60)
    print("2. ЗАПУСК АВТОМАТИЧЕСКИХ ЮНИТ-ТЕСТОВ")
    print("=" * 60)
    # Запуск тестов через unittest runner
    suite = unittest.TestLoader().loadTestsFromTestCase(RatingTests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
