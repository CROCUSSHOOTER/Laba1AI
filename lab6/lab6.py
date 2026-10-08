"""
Лабораторная работа №6: Наследование, полиморфизм, интерфейсы и композиция.
Предмет: Парадигмы программирования.
Вариант 1: Экспорт оценок (GradeBook + Exporter).
"""

import unittest
from typing import Protocol


# ==============================================================================
# 1. ОПРЕДЕЛЕНИЕ КОНТРАКТА (ПРОТОКОЛА)
# ==============================================================================

class Exporter(Protocol):
    """
    Протокол (интерфейс) экспортера оценок.
    Любой класс-экспортер должен реализовывать метод export.
    """
    def export(self, student_name: str, average_score: float | None, status: str) -> str:
        """
        Формирует строковое представление данных студента.

        :param student_name: Имя студента
        :param average_score: Средний балл
        :param status: Статус допуска ("допущен", "не допущен", "нет данных")
        :return: Отформатированная строка экспорта
        """
        ...


# ==============================================================================
# 2. РЕАЛИЗАЦИИ ВЗАИМОЗАМЕНЯЕМЫХ КОМПОНЕНТОВ (EXPORTERS)
# ==============================================================================

class TextExporter:
    """Экспорт данных в текстовом формате (для вывода / чтения человеком)."""

    def export(self, student_name: str, average_score: float | None, status: str) -> str:
        avg_str = f"{average_score:.2f}" if average_score is not None else "N/A"
        return f"Студент: {student_name} | Средний балл: {avg_str} | Статус: {status}"


class CsvExporter:
    """Экспорт данных в формате CSV (строка с разделителями-запятыми)."""

    def export(self, student_name: str, average_score: float | None, status: str) -> str:
        avg_str = f"{average_score:.2f}" if average_score is not None else ""
        return f'"{student_name}",{avg_str},"{status}"'


class MemoryExporter:
    """
    Тестовый дублер (In-Memory Exporter).
    Сохраняет результаты экспорта в память (список) для автоматической проверки.
    """

    def __init__(self) -> None:
        self.exported_items: list[str] = []

    def export(self, student_name: str, average_score: float | None, status: str) -> str:
        avg_str = f"{average_score:.2f}" if average_score is not None else "N/A"
        result = f"{student_name};{avg_str};{status}"
        self.exported_items.append(result)
        return result


class JsonExporter:
    """
    Компонент повышенной сложности:
    Формирует экспорт в формате JSON-строки без изменения GradeBook.
    """

    def export(self, student_name: str, average_score: float | None, status: str) -> str:
        avg_str = f"{average_score:.2f}" if average_score is not None else "null"
        return f'{{"name": "{student_name}", "average": {avg_str}, "status": "{status}"}}'


# ==============================================================================
# 3. МОДЕЛЬ СТУДЕНТА (STUDENT)
# ==============================================================================

class Student:
    """Класс, представляющий студента и его успеваемость."""

    def __init__(self, student_id: int, name: str) -> None:
        if isinstance(student_id, bool) or not isinstance(student_id, int):
            raise TypeError("Идентификатор должен быть целым числом")
        if student_id <= 0:
            raise ValueError("Идентификатор студента должен быть положительным")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Имя студента не может быть пустым")

        self.student_id: int = student_id
        self.name: str = name.strip()
        self._scores: list[float] = []

    def add_score(self, score: float | int) -> None:
        """Добавляет балл студенту (от 0 до 100)."""
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError("Балл должен быть числом")
        if not (0 <= score <= 100):
            raise ValueError("Балл должен быть в диапазоне от 0 до 100")

        self._scores.append(float(score))

    @property
    def average(self) -> float | None:
        """Вычисляет средний балл студента."""
        if not self._scores:
            return None
        return sum(self._scores) / len(self._scores)

    @property
    def status(self) -> str:
        """Определяет статус допуска студента."""
        if self.average is None:
            return "нет данных"
        return "допущен" if self.average >= 50.0 else "не допущен"


# ==============================================================================
# 4. ПРИКЛАДНОЙ КЛАСС С КОМПОЗИЦИЕЙ (GRADEBOOK)
# ==============================================================================

class GradeBook:
    """
    Журнал успеваемости.
    Использует композицию: хранит ссылку на Exporter и делегирует ему экспорт.
    """

    def __init__(self, exporter: Exporter) -> None:
        self._students: dict[int, Student] = {}
        self._exporter: Exporter = exporter

    def register(self, student: Student) -> None:
        """Регистрирует нового студента в журнале."""
        if student.student_id in self._students:
            raise ValueError("Студент с таким ID уже зарегистрирован")
        self._students[student.student_id] = student

    def add_score(self, student_id: int, score: float | int) -> None:
        """Добавляет оценку студенту по ID."""
        student = self._get_student(student_id)
        student.add_score(score)

    def export_student(self, student_id: int) -> str:
        """
        Делегирует экспорт данных конкретному экспортеру.
        Не зависит от конкретного типа экспортера.
        """
        student = self._get_student(student_id)
        return self._exporter.export(student.name, student.average, student.status)

    def _get_student(self, student_id: int) -> Student:
        """Приватный вспомогательный метод получения студента."""
        try:
            return self._students[student_id]
        except KeyError as error:
            raise KeyError("Студент не найден") from error


# ==============================================================================
# 5. ДЕМОНСТРАЦИОННЫЙ ЗАПУСК
# ==============================================================================

def main() -> None:
    print("=== ДЕМОНСТРАЦИЯ РАБОТЫ (Вариант 1: Экспорт оценок) ===\n")

    # Создаем студента
    student = Student(101, " Асан Болатов ")
    student.add_score(85)
    student.add_score(95)

    print(f"Зарегистрирован: {student.name} (ID: {student.student_id})")
    print(f"Средний балл: {student.average:.2f}, Статус: {student.status}\n")

    # 1. Использование TextExporter
    text_exp = TextExporter()
    gb_text = GradeBook(text_exp)
    gb_text.register(student)
    print("1. TextExporter:")
    print(gb_text.export_student(101))

    # 2. Использование CsvExporter
    csv_exp = CsvExporter()
    gb_csv = GradeBook(csv_exp)
    gb_csv.register(student)
    print("\n2. CsvExporter:")
    print(gb_csv.export_student(101))

    # 3. Использование JsonExporter (Повышенная сложность)
    json_exp = JsonExporter()
    gb_json = GradeBook(json_exp)
    gb_json.register(student)
    print("\n3. JsonExporter:")
    print(gb_json.export_student(101))

    # 4. Использование MemoryExporter
    mem_exp = MemoryExporter()
    gb_mem = GradeBook(mem_exp)
    gb_mem.register(student)
    gb_mem.export_student(101)
    print("\n4. MemoryExporter (данные в памяти):")
    print(mem_exp.exported_items)
    print("\n=======================================================\n")


# ==============================================================================
# 6. АВТОМАТИЧЕСКИЕ ТЕСТЫ (UNITTEST)
# ==============================================================================

class GradeBookExporterTests(unittest.TestCase):
    """Набор автоматических тестов (не менее 6 сценариев)."""

    def setUp(self) -> None:
        self.mem_exporter = MemoryExporter()
        self.book = GradeBook(self.mem_exporter)
        self.student = Student(1, "Amina")
        self.book.register(self.student)

    # --- ТЕСТ 1: Проверка корректности экспорта через внедренный MemoryExporter ---
    def test_export_via_injected_exporter(self) -> None:
        self.book.add_score(1, 80)
        self.book.add_score(1, 90)
        result = self.book.export_student(1)

        self.assertEqual(result, "Amina;85.00;допущен")
        self.assertIn("Amina;85.00;допущен", self.mem_exporter.exported_items)

    # --- ТЕСТ 2: Взаимозаменяемость (Подстановка JsonExporter и CsvExporter) ---
    def test_exporter_interchangeability(self) -> None:
        self.book.add_score(1, 40)  # Средний = 40 (не допущен)

        csv_gb = GradeBook(CsvExporter())
        csv_gb.register(self.student)
        self.assertEqual(csv_gb.export_student(1), '"Amina",40.00,"не допущен"')

        json_gb = GradeBook(JsonExporter())
        json_gb.register(self.student)
        self.assertEqual(json_gb.export_student(1), '{"name": "Amina", "average": 40.00, "status": "не допущен"}')

    # --- ТЕСТ 3: Обработка студента без оценок ("нет данных") ---
    def test_export_student_with_no_scores(self) -> None:
        result = self.book.export_student(1)
        self.assertEqual(result, "Amina;N/A;нет данных")

    # --- ТЕСТ 4: Ошибочный сценарий - Запрос несуществующего студента ---
    def test_unknown_student_raises_key_error(self) -> None:
        with self.assertRaisesRegex(KeyError, "Студент не найден"):
            self.book.export_student(999)

    # --- ТЕСТ 5: Ошибочный сценарий - Некорректный балл (больше 100 или bool) ---
    def test_invalid_score_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            self.book.add_score(1, 150)

        with self.assertRaises(TypeError):
            self.book.add_score(1, True)

    # --- ТЕСТ 6: Ошибочный сценарий - Попытка повторной регистрации ID ---
    def test_duplicate_student_registration_raises_error(self) -> None:
        duplicate = Student(1, "Amina Second")
        with self.assertRaisesRegex(ValueError, "Студент с таким ID уже зарегистрирован"):
            self.book.register(duplicate)


if __name__ == "__main__":
    main()
    print("Запуск автоматических тестов...")
    unittest.main(argv=["first-arg-is-ignored"], exit=False)