import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass

SENTINEL = object()


@dataclass(frozen=True)
class GradeRecord:
    student: str
    subject: str
    score: int | float


def validate_record(record: dict) -> GradeRecord:
    """Проверяет корректность полей записи об оценке."""
    if not isinstance(record, dict):
        raise ValueError("Запись должна быть словарем")

    student = str(record.get("student", "")).strip()
    subject = str(record.get("subject", "")).strip()
    score = record.get("score")

    if not student:
        raise ValueError("Не указано имя студента")
    if not subject:
        raise ValueError("Не указан предмет")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("Оценка должна быть числом")
    if not (0 <= score <= 100):
        raise ValueError(f"Оценка {score} вне диапазона [0, 100]")

    return GradeRecord(student=student, subject=subject, score=score)


async def process_record(record: dict, delay: float = 0.15) -> dict:
    """Имитирует асинхронную проверку и сохранение записи в БД."""
    await asyncio.sleep(delay)
    valid = validate_record(record)
    status = "зачет" if valid.score >= 60 else "незачет"
    return {
        "student": valid.student,
        "subject": valid.subject,
        "score": valid.score,
        "status": status,
    }


async def producer(
    queue: asyncio.Queue,
    records: list[dict],
    num_workers: int,
    produce_delay: float = 0.05,
    verbose: bool = True,
) -> None:
    """Читает исходные записи и помещает их в ограниченную очередь."""
    for record in records:
        await asyncio.sleep(produce_delay)
        await queue.put(record)
        if verbose:
            print(f"[Producer] Отправлено в очередь: {record}")

    # Отправляем сигнал завершения для каждого потребителя
    for _ in range(num_workers):
        await queue.put(SENTINEL)


async def consumer(
    name: str,
    queue: asyncio.Queue,
    results: list[dict],
    errors: list[str],
    process_delay: float = 0.15,
    timeout_sec: float = 1.0,
    verbose: bool = True,
) -> None:
    """Извлекает записи из очереди, валидирует и сохраняет результаты."""
    while True:
        item = await queue.get()
        try:
            if item is SENTINEL:
                if verbose:
                    print(f"[{name}] Получен SENTINEL. Завершение работы.")
                return

            try:
                async with asyncio.timeout(timeout_sec):
                    processed = await process_record(item, delay=process_delay)
                results.append(processed)
                if verbose:
                    print(f"[{name}] Успешно: {processed}")
            except TimeoutError:
                err_msg = f"Тайм-аут при обработке записи: {item}"
                errors.append(err_msg)
                if verbose:
                    print(f"[{name}] ОШИБКА: {err_msg}")
            except ValueError as exc:
                err_msg = f"Ошибка валидации ({exc}) в записи: {item}"
                errors.append(err_msg)
                if verbose:
                    print(f"[{name}] ОШИБКА: {err_msg}")
        finally:
            queue.task_done()


def build_student_rating(results: list[dict]) -> list[tuple[str, float]]:
    """Формирует рейтинг студентов по среднему баллу (задание повышенной сложности)."""
    scores_by_student: dict[str, list[float]] = defaultdict(list)
    for item in results:
        scores_by_student[item["student"]].append(float(item["score"]))

    averages = [
        (student, sum(scores) / len(scores))
        for student, scores in scores_by_student.items()
    ]
    # Сортировка по убыванию среднего балла, затем по имени
    return sorted(averages, key=lambda x: (-x[1], x[0]))


async def run_pipeline(
    records: list[dict],
    maxsize: int = 3,
    num_workers: int = 3,
    produce_delay: float = 0.05,
    process_delay: float = 0.15,
    timeout_sec: float = 1.0,
    verbose: bool = True,
) -> dict:
    """Запускает полный цикл конвейера и возвращает сводную статистику."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
    results: list[dict] = []
    errors: list[str] = []

    started = time.perf_counter()

    workers = [
        asyncio.create_task(
            consumer(
                name=f"Worker-{i}",
                queue=queue,
                results=results,
                errors=errors,
                process_delay=process_delay,
                timeout_sec=timeout_sec,
                verbose=verbose,
            )
        )
        for i in range(1, num_workers + 1)
    ]

    await producer(
        queue=queue,
        records=records,
        num_workers=num_workers,
        produce_delay=produce_delay,
        verbose=verbose,
    )
    await queue.join()
    await asyncio.gather(*workers)

    elapsed = time.perf_counter() - started
    avg_score = (
        sum(r["score"] for r in results) / len(results) if results else 0.0
    )
    rating = build_student_rating(results)

    return {
        "processed_count": len(results),
        "error_count": len(errors),
        "average_score": avg_score,
        "elapsed": elapsed,
        "results": results,
        "errors": errors,
        "rating": rating,
    }


async def run_tests() -> None:
    """Запуск 7 тестовых сценариев согласно требованиям."""
    print("\n" + "=" * 60)
    print("ЗАПУСК ТЕСТОВЫХ СЦЕНАРИЕВ")
    print("=" * 60)

    # Тест 1: Все записи корректны
    t1_data = [
        {"student": "Айболат", "subject": "Python", "score": 95},
        {"student": "Дамир", "subject": "Python", "score": 80},
    ]
    res1 = await run_pipeline(t1_data, verbose=False)
    assert res1["processed_count"] == 2 and res1["error_count"] == 0
    print("[Тест 1: Все записи корректны] -> ПРОЙДЕН")

    # Тест 2: Пустое имя студента
    t2_data = [
        {"student": "", "subject": "Физика", "score": 75},
        {"student": "Алия", "subject": "Физика", "score": 85},
    ]
    res2 = await run_pipeline(t2_data, verbose=False)
    assert res2["processed_count"] == 1 and res2["error_count"] == 1
    print("[Тест 2: Пустое имя] -> ПРОЙДЕН")

    # Тест 3: Оценка < 0 или > 100
    t3_data = [
        {"student": "Валерий", "subject": "Алгоритмы", "score": -5},
        {"student": "Эрик", "subject": "Алгоритмы", "score": 105},
        {"student": "Мадина", "subject": "Алгоритмы", "score": 60},
    ]
    res3 = await run_pipeline(t3_data, verbose=False)
    assert res3["processed_count"] == 1 and res3["error_count"] == 2
    print("[Тест 3: Оценка вне диапазона 0..100] -> ПРОЙДЕН")

    # Тест 4: Очередь maxsize=1 (обратное давление без потери данных)
    t4_data = [
        {"student": f"Студент_{i}", "subject": "БД", "score": 70 + i}
        for i in range(5)
    ]
    res4 = await run_pipeline(t4_data, maxsize=1, verbose=False)
    assert res4["processed_count"] == 5 and res4["error_count"] == 0
    print("[Тест 4: Очередь maxsize=1] -> ПРОЙДЕН")

    # Тест 5: Сравнение 1 и 3 потребителей
    t5_data = [
        {"student": f"Студент_{i}", "subject": "Сети", "score": 80}
        for i in range(6)
    ]
    res_1w = await run_pipeline(
        t5_data, num_workers=1, produce_delay=0.01, process_delay=0.1, verbose=False
    )
    res_3w = await run_pipeline(
        t5_data, num_workers=3, produce_delay=0.01, process_delay=0.1, verbose=False
    )
    assert res_3w["elapsed"] < res_1w["elapsed"]
    print(
        f"[Тест 5: 1 vs 3 воркера] -> ПРОЙДЕН "
        f"(1 воркер: {res_1w['elapsed']:.2f}с, 3 воркера: {res_3w['elapsed']:.2f}с)"
    )

    # Тест 6: Тайм-аут при обработке (task_done вызывается, join не зависает)
    t6_data = [{"student": "Руслан", "subject": "ИИ", "score": 90}]
    res6 = await run_pipeline(
        t6_data, process_delay=0.3, timeout_sec=0.05, verbose=False
    )
    assert res6["processed_count"] == 0 and res6["error_count"] == 1
    print("[Тест 6: Обработка тайм-аута] -> ПРОЙДЕН")

    # Тест 7: Пустой входной список (нет деления на ноль)
    res7 = await run_pipeline([], verbose=False)
    assert res7["processed_count"] == 0 and res7["average_score"] == 0.0
    print("[Тест 7: Пустой входной список] -> ПРОЙДЕН")


async def main() -> None:
    sample_records = [
        {"student": "Айболат", "subject": "Парадигмы программирования", "score": 92},
        {"student": "Дамир", "subject": "Парадигмы программирования", "score": 78},
        {"student": "Валерий", "subject": "Базы данных", "score": 88},
        {"student": "Айболат", "subject": "Базы данных", "score": 98},
        {"student": "Эрик", "subject": "Парадигмы программирования", "score": 55},
        {"student": "Дамир", "subject": "Базы данных", "score": 84},
        {"student": "", "subject": "Физика", "score": 90},           # Ошибка: нет имени
        {"student": "Мадина", "subject": "Математика", "score": 110}, # Ошибка: балл > 100
    ]

    print("=== ЗАПУСК ОСНОВНОГО КОНВЕЙЕРА (ВАРИАНТ 4) ===")
    stats = await run_pipeline(sample_records, maxsize=3, num_workers=3)

    print("\n--- ИТОГОВАЯ СТАТИСТИКА ---")
    print(f"Успешно обработано записей: {stats['processed_count']}")
    print(f"Количество ошибок: {stats['error_count']}")
    print(f"Общий средний балл: {stats['average_score']:.2f}")
    print(f"Время выполнения: {stats['elapsed']:.2f} сек.")

    print("\n--- РЕЙТИНГ СТУДЕНТОВ ПО СРЕДНЕМУ БАЛЛУ ---")
    for rank, (student, avg) in enumerate(stats["rating"], start=1):
        print(f"{rank}. {student}: {avg:.2f}")

    if stats["errors"]:
        print("\n--- ЖУРНАЛ ОШИБОК ---")
        for err in stats["errors"]:
            print(f"• {err}")

    await run_tests()


if __name__ == "__main__":
    asyncio.run(main())
