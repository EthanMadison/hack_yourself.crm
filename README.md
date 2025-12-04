# hack_yourself.CRM (Tkinter + SQLite)

Настольное приложение на **Tkinter** и **SQLite** для управления контактами.

## Возможности
- Добавление, редактирование, удаление контактов (CRUD).
- Поиск по нескольким полям: имя, email, телефон, компания, теги.
- Поля «Заметки», «Теги» для быстрых пометок.
- Автоустановка времени создания (`created_at`).
- Русский интерфейс (подписи полей, кнопки и подсказки).

## Установка
```bash
  python -m venv .venv
  # Windows PowerShell
  .venv\Scripts\Activate.ps1
  
  # macOS/Linux
  source .venv/bin/activate
```

## Запуск
```bash
  python hack_yourself.crm/app.py
```

## Структура проекта
```
├─ assets/                   # логотоипы в формате .png и .ico
│
├─ database/                 
│  ├─ db.py                  # функции для работы с db и её данными
│  ├─ crm.db                 # база данных (создаётся при первом запуске)
│
├─ ui/                       
│  ├─ ui.py                  # гафическая оболочка с функциями валидации данных
│  ├─ ui_helpers.py          # дополнительные функции для графической оболочки
│
├─ app.py                    # точка входа (python app.py)
└─ README.md                 # этот файл
```

## База данных
БД — файл SQLite (обычно `crm.db`) рядом с приложением. Минимальная схема:
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT,
phone TEXT,
company TEXT,
tags TEXT,
notes TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
```

### Обновление схемы
Если старая БД создана без некоторых колонок, добавьте их через `ALTER TABLE` или удалите файл БД для пересоздания.

## Интерфейс
- `ui.py`: `MainWindow` (поле поиска, кнопки, таблица `Treeview`) и `ContactDialog` (диалог добавления/редактирования).
- Русские метки полей, валидация имени и e‑mail (диалог не закрывается при ошибке).

## Иконка и логотип
- `assets/app.png` — иконка окна (Tk `iconphoto`) и логотип в шапке.
- `assets/app.ico` — иконка Windows (Tk `iconbitmap`).
