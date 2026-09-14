
# 🚀 S3 Benchmark Automation (MinIO Warp)

Автоматизированный скрипт для проведения нагрузочного тестирования S3-совместимых хранилищ с использованием [MinIO Warp](https://github.com/minio/warp). 

Скрипт автоматически прогоняет набор YAML-конфигов через заданный список бакетов и сохраняет сжатые результаты тестов.

## 📋 Требования и Установка

1. **Установите MinIO WARP** 
   Скачайте и установите [warp](https://github.com/minio/warp/releases), обязательно добавьте его в системный `$PATH`.
2. **Установите uv** 
   Установите менеджер пакетов [uv](https://docs.astral.sh/uv/getting-started/installation/).
3. **Скачайте репозиторий**
   ```bash
   git clone <url-репозитория>
   cd <имя-репозитория>
   ```
4. **Подготовьте переменные окружения**
   ```bash
   cp .env.template .env
   ```
5. **Заполните `.env`**
   Укажите ваши `S3_ENDPOINT`, `S3_ACCESS_KEY` и `S3_SECRET_KEY`.

---

## ⚙️ Настройка экспериментов

> **Примечание:** *Блок с переменными сделан "на коленке", чтобы быстро работало. Предельное время эксперимента и целевые бакеты задаются напрямую в коде.*

Откройте `main.py` (или соответствующий файл конфигурации) и отредактируйте следующие параметры:

```python
variables = {
    "S3_ENDPOINT" : os.environ.get("S3_ENDPOINT"),
    "S3_ACCESS_KEY": os.environ.get("S3_ACCESS_KEY"),
    "S3_SECRET_KEY": os.environ.get("S3_SECRET_KEY"),
    
    # ⚠️ Укажите максимальную длительность. Рекомендуется от 20m
    "DURATION" : "10s",                                     
    
    "BUCKET" : "",
    "BENCH_DATA": results_folder,
    "TLS": "true",
    "INSECURE": "false",
}

# ⚠️ Укажите список тестируемых бакетов
bucket_list = ["warm-warp-test", "cold-warp-test"]          
```

---

## ▶️ Запуск

Запуск всех тестов осуществляется одной командой:

```bash
uv run --env-file .env main.py
```

---


## ▶️ Циклический запуск в качестве сервиса (systemd)

Сервис запускает `main.py`, дожидается завершения, ждёт 30 секунд
и запускает снова — бесконечно. Автоматически стартует при загрузке ОС.

### 1. Подготовьте unit-файл

Скопируйте шаблон и откройте его на редактирование:

```bash
cp warp-tests.service.template warp-tests.service
nano warp-tests.service
```

Обязательно проверьте в файле:
- `User=` — под каким пользователем запускать (не root);
- `Group=` — соответствующая группа;
- `WorkingDirectory=` — абсолютный путь до проекта;
- `ExecStart=` — путь до `uv` (узнать: `which uv`) и до `main.py`.

### 2. Установите сервис

```bash
sudo cp warp-tests.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 3. Включите автозапуск и стартуйте

```bash
sudo systemctl enable --now warp-tests.service
```

### Наблюдение за работой

```bash
# Логи в реальном времени (аналог консоли)
journalctl -u warp-tests.service -f

# Последние 200 строк
journalctl -u warp-tests.service -n 200

# Текущий статус: активна ли, сколько раз перезапускалась, PID
systemctl status warp-tests.service
```

### Управление сервисом

```bash
# Остановить (текущий цикл прервётся, следующий не запустится)
sudo systemctl stop warp-tests.service

# Запустить снова
sudo systemctl start warp-tests.service

# Перезапустить (например, после правки unit-файла;
# перед этим не забудьте `sudo systemctl daemon-reload`)
sudo systemctl restart warp-tests.service

# Убрать из автозапуска
sudo systemctl disable warp-tests.service
```

### Если правите unit-файл

После любого изменения `/etc/systemd/system/warp-tests.service`:

```bash
sudo systemctl daemon-reload
sudo systemctl restart warp-tests.service
```
---

## 🧠 Логика работы

1. Скрипт сканирует папку `benchmarks/` и забирает оттуда все `.yml` конфиги экспериментов.
2. Запускается вложенный цикл прогона тестов:
   - **Внешний цикл:** по каждому YAML-конфигу.
   - **Внутренний цикл:** по каждому бакету из `bucket_list`.
3. *Текущее количество прогонов:* **66**.

### 📂 Результаты

По итогу выполнения в директории `results/` создается папка с именем, соответствующим времени запуска (`datetime.now().strftime("%Y-%m-%d_%H-%M-%S")`).

Внутри неё в формате `{config_name}_{bucket_name}.json.zst` записываются результаты всех прогонов warp.

**Структура вывода:**
```text
results/
└── 2026-09-09_14-30-00/
    ├── get_config_warm-warp-test.json.zst
    ├── get_config_cold-warp-test.json.zst
    ├── put_config_warm-warp-test.json.zst
    └── ...
```