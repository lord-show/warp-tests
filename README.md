becnchmarks
    fix_size
        get
            get128KB
            get1MB
            get10MB
            get100MB
            get1GB
            get10GB
        put
        mixed
    rand_size
        get
        put
        mixed

bucket_list = ["warm-warp-test", "cold-warp-test", "standard-warp-test"]
object_size_list = ["128КБ", "1МБ", "10МБ", "100МБ", "1ГБ", "10ГБ"]
object_rand_size_list = ["1МБ", "10МБ", "100МБ", "1ГБ", "10ГБ", "10ГБ"]


Добавить итерации по размерам объектов
для get и mixed сделать отдельные циклы

Всего получиться 
    get put mixed 3 метода 
    bucket_list = ["warm-warp-test", "cold-warp-test"] 2
    object_size_list = ["128КБ", "1МБ", "10МБ", "100МБ", "1ГБ", "10ГБ"] 6
    # object_rand_size_list = ["1МБ", "10МБ", "100МБ", "1ГБ", "10ГБ", "100ГБ"] 6

    72 варианта по 20 мин = 1440 мин = 24 часа