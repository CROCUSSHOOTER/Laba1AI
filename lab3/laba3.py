"""
Лабораторная работа №3: Процедурное программирование.
Тема: Декомпозиция, процедуры, функции и области видимости.
Вариант 1: Посещаемость студентов.
Студент: Жусупов Айболат (Группа ТИИ-25-21)
"""

import unittest


# ==============================================================================
# 1. ВАЛИДАЦИЯ ДАННЫХ
# ==============================================================================

def validate_mark(mark: str) -> str:
    """
    Проверяет отметку посещаемости.
    Допустимые отметки: 'present' (присутствие), 'absent' (прогул), 'excused' (уважительный пропуск).
    """
    if not isinstance(mark, str):
        raise TypeError("Отметка должна быть строкой")
    
    cleaned = mark.strip().lower()
    if cleaned not in ("present", "absent", "excused"):
        raise ValueError(f"Недопустимая отметка: '{mark}'. Допустимо: 'present', 'absent', 'excused'")
    
    return cleaned


# ==============================================================================
# 2. ВЫЧИСЛИТЕЛЬНЫЕ ФУНКЦИИ (БЕЗ ПОБОЧНЫХ ЭФФЕКТОВ)
# ==============================================================================

def attendance_rate(marks: list[str]) -> float:
    """
    Вычисляет процент посещаемости (0.0 - 100.0).
    Уважительные пропуски ('excused') не снижают процент посещаемости.
    Если от отметок нет или только уважительные, возвращает 100.0.
    """
    validated = [validate_mark(m) for m in marks]
    
    present_count = validated.count("present")
    absent_count = validated.count("absent")
    
    total_accounted = present_count + absent_count
    if total_accounted == 0:
        return 100.0
        
    return (present_count / total_accounted) * 100.0


def determine_access(rate: float, threshold: float = 70.0) -> str:
    """Определяет статус допуска по полученному проценту и порогу."""
    if not (0.0 <= threshold <= 100.0):
        raise ValueError("Порог допуска должен быть от 0 до 100")
        
    return "допущен" if rate >= threshold else "не допущен"


def summarize_student(student: dict, threshold: float = 70.0) -> dict:
    """Принимает словарь студента, проверяет его и возвращает новую сводную запись."""
    student_id = student.get("id")
    name = student.get("name")
    marks = student.get("marks", [])
    
    if isinstance(student_id, bool) or not isinstance(student_id, int):
        raise TypeError("Идентификатор студента должен быть целым числом")
    if student_id <= 0:
        raise ValueError("Идентификатор студента должен быть положительным")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Имя студента не может быть пустым")
        
    rate = attendance_rate(marks)
    status = determine_access(rate, threshold)
    
    return {
        "id": student_id,
        "name": name.strip(),
        "attendance_rate": rate,
        "status": status
    }


def build_rating(students: list[dict], threshold: float = 70.0) -> list[dict]:
    """Формирует и сортирует список студентов по проценту посещаемости (по убыванию)."""
    summaries = [summarize_student(s, threshold) for s in students]
    
    return sorted(
        summaries,
        key=lambda item: item["attendance_rate"],
        reverse=True
    )


# ==============================================================================
# 3. ФУНКЦИЯ ФОРМАТИРОВАНИЯ (БЕЗ КОНСОЛЬНОГО ВЫВОДА)
# ==============================================================================

def format_report(rating: list[dict]) -> str:
    """Формирует текстовый отчет из отсортированного списка студентов."""
    lines = []
    for pos, item in enumerate(rating, start=1):
        line = f"{pos}. {item['name']}: {item['attendance_rate']:.1f}%; {item['status']}"
        lines.append(line)
        
    return "\n".join(lines)


# ==============================================================================
# 4. ДЕМОНСТРАЦИЯ ОБЛАСТЕЙ ВИДИМОСТИ (CLOSURE & NONLOCAL)
# ==============================================================================

def make_call_counter():
    """Демонстрация Enclosing-области видимости и инструкции nonlocal."""
    count = 0
    def register_call():
        nonlocal count
        count += 1
        return count
    return register_call


# ==============================================================================
# 5. ТОЧКА ВХОДА (MAIN)
# ==============================================================================

def main():
    print("=== ДЕМОНСТРАЦИЯ РАБОТЫ (Вариант 1: Посещаемость) ===\n")
    
    raw_students = [
        {"id": 101, "name": "Жусупов Айболат", "marks": ["present", "present", "present", "excused"]},
        {"id": 102, "name": "Болатов Асан", "marks": ["present", "absent", "present", "absent"]},
        {"id": 103, "name": "Серік Аружан", "marks": ["present", "present", "present", "present"]}
    ]
    
    rating = build_rating(raw_students, threshold=70.0)
    report_text = format_report(rating)
    print(report_text)
    print("\n=======================================================\n")


# ==============================================================================
# 6. АВТОМАТИЧЕСКИЕ ТЕСТЫ (UNITTEST)
# ==============================================================================

class AttendanceFunctionsTests(unittest.TestCase):
    
    def test_attendance_rate_calculation(self):
        # 3 присутствия / (3 присутствия + 1 прогул) = 75.0%
        marks = ["present", "present", "present", "absent"]
        self.assertEqual(attendance_rate(marks), 75.0)

    def test_excused_absences_handling(self):
        # 1 присутствие + 1 уважительный = 100.0%
        marks = ["present", "excused"]
        self.assertEqual(attendance_rate(marks), 100.0)

    def test_input_list_not_modified(self):
        source_marks = ["present", "absent"]
        attendance_rate(source_marks)
        self.assertEqual(source_marks, ["present", "absent"])

    def test_invalid_mark_raises_value_error(self):
        with self.assertRaises(ValueError):
            attendance_rate(["present", "late"])

    def test_invalid_student_id_raises_exception(self):
        bad_student = {"id": -5, "name": "Айболат", "marks": ["present"]}
        with self.assertRaises(ValueError):
            summarize_student(bad_student)

    def test_empty_marks_returns_100_percent(self):
        self.assertEqual(attendance_rate([]), 100.0)


if __name__ == "__main__":
    main()
    print("Запуск автоматических тестов...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)