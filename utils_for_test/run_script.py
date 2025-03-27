import os
import sys
import django

#--------- Запускать через 'python utils_for_test/run_script.py' -------------------------

# Добавляем корневую папку проекта в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

# Устанавливаем переменную окружения для Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eventManager.settings")

# Настраиваем Django
django.setup()

# Выполняем основной скрипт
exec(open("utils_for_test/scriptForTest.py", encoding="utf-8").read())
