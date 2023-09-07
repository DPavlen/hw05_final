# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


cd HW05_FINAL

Cоздать виртуальное окружение:
```
python3 -m venv env
```
Активировать созданное виртуальное окружение:
```
source env/bin/activate
```
Выполните обновление инструмента установки пакетов pip для Python 3 на самую последнюю версию:
```
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
