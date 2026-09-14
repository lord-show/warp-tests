#!/usr/bin/env python3
"""
Скрипт для автоматического запуска всех benchmark-конфигов из папки benchmark.
Для каждого .yml или .yaml файла выполняется команда: warp run <file>
"""

from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys

def get_benchmark_files(benchmark_dir: str) -> list:
    """
    Возвращает список относительных путей ко всем YAML-файлам в папке benchmark.

    Args:
        benchmark_dir: Путь к папке с конфигами

    Returns:
        Список строк с относительными путями к файлам
    """
    benchmark_path = Path(benchmark_dir)

    if not benchmark_path.exists():
        print(f"❌ Ошибка: папка '{benchmark_dir}' не найдена")
        sys.exit(1)
    
    if not benchmark_path.is_dir():
        print(f"❌ Ошибка: '{benchmark_dir}' не является папкой")
        sys.exit(1)

    # Ищем все файлы с расширением .yml или .yaml
    yaml_files = sorted(benchmark_path.glob("*.yml")) + sorted(benchmark_path.glob("*.yaml"))

    if not yaml_files:
        print(f"⚠️  В папке '{benchmark_dir}' нет YAML-файлов")
        return []

    # Преобразуем в относительные пути (относительно текущей рабочей директории)
    relative_paths = []
    for file_path in yaml_files:
        rel_path = os.path.relpath(file_path, start=os.getcwd())
        relative_paths.append(rel_path)

    return relative_paths

def get_cmd(config_file: str, variables: dict) -> list:
    variables["BENCH_DATA"] = variables["BENCH_DATA"] / (Path(config_file).stem + variables["BUCKET"])
    cmd = ["warp", "run", config_file] 
    if variables:
        for key, value in variables.items():
            cmd.extend(["--var", f"{key}={value}"])

    variables["BENCH_DATA"] = variables["BENCH_DATA"].parent 
    return cmd

def run_warp_benchmark(config_file: str, variables: dict) -> bool:
    """
        Запускает warp run для указанного конфигурационного файла.
    
        Args:
            config_file: Путь к YAML-файлу
    
        Returns:
            True если выполнение успешно, иначе False
    """

    cmd = get_cmd(config_file, variables)

    try:
        # Запускаем процесс warp run
        result = subprocess.run(
            cmd,
            capture_output=False,  # Выводим stdout/stderr в реальном времени
            text=True,
            check=False,  # Не выбрасываем исключение при ненулевом коде возврата
        )

        if result.returncode == 0:
            print(f"\n✅ Бенчмарк завершён успешно: {config_file}")
            return True
        else:
            print(f"\n❌ Бенчмарк завершился с ошибкой (код {result.returncode}): {config_file}")
            return False

    except FileNotFoundError:
        print("❌ Ошибка: команда 'warp' не найдена. Убедитесь, что warp установлен и доступен в PATH.")
        print("   Скачать warp можно здесь: https://github.com/minio/warp/releases")
        return False
    except Exception as e:
        print(f"❌ Непредвиденная ошибка при запуске {config_file}: {e}")
        return False

def main():

    """uv run --env-file .env python main.py"""

    benchmark_dir = "benchmarks"

    results_folder = Path("results") / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_folder.mkdir(parents=True, exist_ok=True)
    
    variables = {
        "S3_ENDPOINT" : os.environ.get("S3_ENDPOINT"),
        "S3_ACCESS_KEY": os.environ.get("S3_ACCESS_KEY"),
        "S3_SECRET_KEY": os.environ.get("S3_SECRET_KEY"),
        "DURATION" : "20m",
        "BUCKET" : "" ,
        "BENCH_DATA": results_folder,
        "TLS": "true",
        "INSECURE": "false",
    }
    bucket_list = ["warm-warp-test", "cold-warp-test"]
    
    print("🔍 Поиск конфигурационных файлов в папке 'benchmark'...")
    
    config_files = get_benchmark_files(benchmark_dir)

    if not config_files:
        print("📭 Нет файлов для запуска. Завершение работы.")
        return

    print(f"📄 Найдено {len(config_files)} конигураций")
    # for f in config_files:
    #     print(f"   - {f}")

    

    print("🚀 Начинаем последовательный запуск бенчмарков...")
    
    failed = []
    for i, config_file in enumerate(config_files, 1):
        print(f"\n[{i}/{len(config_files)}]")
        for bucket in bucket_list:
            variables["BUCKET"] = bucket
            success = run_warp_benchmark(config_file,variables)
            if not success:
                failed.append(config_file)

    # Итоговый отчёт
    print(f"\n{'='*60}")
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print(f"{'='*60}")
    print(f"✅ Успешно выполнено: {len(config_files) - len(failed)}")
    print(f"❌ Завершилось с ошибкой: {len(failed)}")

    if failed:
        print("\n❌ Список проваленных бенчмарков:")
        for f in failed:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("\n🎉 Все бенчмарки выполнены успешно!")
        sys.exit(0)

if __name__ == "__main__":
    main()


