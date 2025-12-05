from __future__ import annotations
from typing import Dict, Iterable, List, Optional
import sqlite3
import csv
import re


DB_PATH = 'database\\crm.db'

NAME_ALLOWED = re.compile("^[A-Za-zА-Яа-яЁё\\-' ]+$")
PHONE_ALLOWED = re.compile('^[0-9+()\\- ]+$')

def validate_name_or_raise(name: str) -> None:
    """
    Функция для проверки корректности введённого имени.
    Допускаются только буквы (латиница/кириллица), пробел, дефис и апостроф.
    Выбрасывает исключение class: 'ValueError', если имя некорректно.

    Параметры:
        name: Имя контакта (обязательное поле).
    """
    if not name or not NAME_ALLOWED.fullmatch(name.strip()):
        raise ValueError('Ошибка. Имя должно содержать только буквы, пробелы, дефис или апостроф.')

def validate_email_or_raise(email: Optional[str]) -> None:
    """
    Функция для минимальной проверки email на наличие символа `@`.
    Допускается пустое значение. Считает некорректными варианты,
    где символ `@` отсутствует или стоит первым/последним символом.

    Параметры:
        email: Email или `None`.
    """
    if not email:
        return
    email_address = email.strip()
    if '@' not in  email_address or email_address.startswith('@') or email_address.endswith('@'):
        raise ValueError("Ошибка. Проверьте корректность введённого email.")

def validate_phone_or_raise(phone: Optional[str]) -> None:
    """
    Проверяет допустимость символов телефонного номера.
    Разрешенные символы: цифры, пробел, +, (), -.

    Параметры:
        phone: Номер телефона или 'None'.
    """
    if phone and (not PHONE_ALLOWED.fullmatch(phone)):
        raise ValueError('Ошибка. Телефон содержит недопустимые символы.')

def normalize_phone(source_phone: Optional[str]) -> str:
    """Нормализует номер для хранения — оставляет только цифры и ведущий '+'.

    Параметры:
        source_phone: Исходный ввод пользователя.
    Возвращает:
        Нормализованный номер (например, '+79991234567')
    """
    return re.sub('[^\\d+]', '', source_phone or '')

def get_connect() -> sqlite3.Connection:
    """
    Создаёт соединение с базой данных SQLite и включает получение строк как словарей.

    Возвращает:
        Объект соединения 'sqlite3.Connection'.
    """
    connect = sqlite3.connect(DB_PATH)
    connect.row_factory = sqlite3.Row
    return connect

def init_db() -> None:
    """
    Создаёт таблицу 'contacts' при первом запуске.
    Столбец 'created_at' по умолчанию заполняется текущим временем (UTC).
    """
    connect = get_connect()
    try:
        with connect:
            connect.execute(
                '''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    company TEXT,
                    tags TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                '''
            )
    finally:
        connect.close()

def list_contacts(substring_search: str='') -> List[Dict]:
    """
    Возвращает список контактов (опционально — с фильтром по подстроке).
    Ищет совпадения в полях: 'name', 'email', 'phone', 'company', 'tags'.

    Параметры:
        substring_search: Подстрока для поиска (если пусто — возвращает все записи).
    Возвращает:
        Список словарей, каждый — одна запись контакта.
    """
    sql = 'SELECT * FROM contacts'
    params = []
    if substring_search:
        sql += ' WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR company LIKE ? OR tags LIKE ?'
        like = f'%{substring_search}%'
        params = [like, like, like, like, like]
    sql += ' ORDER BY created_at DESC'

    connect = get_connect()
    try:
        return [dict(row) for row in connect.execute(sql, params)]
    finally:
        connect.close()

def add_contact(data: Dict) -> int:
    """
    Добавляет контакт и возвращает его 'id'.
    Перед записью выполняется проверка имени/email/телефона, а телефон нормализуется.
    Исключение ValueError если валидация не пройдена.

    Параметры:
        data: Данные контакта (ключи: 'name', 'email', 'phone', 'company', 'tags', 'notes').
    Возвращает:
        'id' вставленной записи.
    """
    validate_name_or_raise(data.get('name', ''))
    validate_email_or_raise(data.get('email'))
    validate_phone_or_raise(data.get('phone'))
    phone = normalize_phone(data.get('phone'))

    connect = get_connect()
    try:
        with connect:
            cur = connect.execute(
            '''
                INSERT INTO contacts (name, email, phone, company, tags, notes) VALUES (?,?,?,?,?,?)
                ''',
    (
                data['name'],
                data.get('email'),
                phone,
                data.get('company'),
                data.get('tags'),
                data.get('notes'),
                )
            )
            return int(cur.lastrowid)
    finally:
        connect.close()


def update_contact(contact_id: int, data: Dict) -> None:
    """
    Обновляет существующий контакт по 'id'.
    Исключение ValueError если валидация не пройдена.

    Параметры:
        contact_id: Идентификатор редактируемого контакта;
        data: Новые значения полей.
    """
    validate_name_or_raise(data.get('name', ''))
    validate_email_or_raise(data.get('email'))
    validate_phone_or_raise(data.get('phone'))
    phone = normalize_phone(data.get('phone'))

    connect = get_connect()
    try:
        with connect:
            connect.execute(
            '''
                UPDATE contacts SET name=?, email=?, phone=?, company=?, tags=?, notes=? WHERE id=?
                ''',
    (
                data['name'],
                data.get('email'),
                phone,
                data.get('company'),
                data.get('tags'),
                data.get('notes'),
                contact_id,
              )
            )
    finally:
        connect.close()

def delete_contact(contact_id: int) -> None:
    """
    Удаляет контакт по 'id'.

    Параметры:
        contact_id: Идентификатор удаляемой записи.
    """
    connect = get_connect()
    try:
        with connect:
            connect.execute('DELETE FROM contacts WHERE id=?', (contact_id,))
    finally:
        connect.close()

def delete_contacts(contact_ids: list[int]) -> int:
    """Удаляет сразу несколько контактов по списку id. Возвращает число удалённых строк.

    Параметры:
        contact_ids: Идентификаторы удаляемых записей.
    """
    if not contact_ids:
        return 0
    # формирование плейсхолдеров (?, ?, ?, ...)
    placeholders = ",".join(["?"] * len(contact_ids))
    sql = f"DELETE FROM contacts WHERE id IN ({placeholders})"
    connect = get_connect()
    try:
        with connect:
            cur = connect.execute(sql, contact_ids)
        return cur.rowcount
    finally:
        connect.close()

def export_contacts_csv(path: str) -> int:
    """
    Экспортирует все контакты в CSV-файл.

    Параметры:
        path: Путь для сохранения CSV.
    Возвращает:
        Количество экспортированных записей.
    """
    rows = list_contacts('')
    with open(path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['name', 'email', 'phone', 'company', 'tags', 'notes'])
        writer.writeheader()
        for row in rows:
            writer.writerow({'name': row.get('name', ''), 'email': row.get('email', ''), 'phone': row.get('phone', ''),
                             'company': row.get('company', ''), 'tags': row.get('tags', ''),
                             'notes': row.get('notes', '')})
    return len(rows)

def import_contacts_csv(path: str) -> int:
    """
    Импортирует контакты из CSV.
    Ожидаемые заголовки: 'name, email, phone, company, tags, notes'.
    Пустые имена пропускаются. Телефон нормализуется.
    Исключение ValueError если строка CSV нарушает правила валидации.

    Параметры:
        path: Путь к входному CSV-файлу.
    Возвращает:
        Количество добавленных записей.
    """
    added = 0
    with open(path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data = {'name': (row.get('name') or '').strip(), 'email': (row.get('email') or '').strip(),
                          'phone': (row.get('phone') or '').strip(), 'company': (row.get('company') or '').strip(),
                          'tags': (row.get('tags') or '').strip(), 'notes': (row.get('notes') or '').strip()}
            if not data['name']:
                continue
            validate_name_or_raise(data['name'])
            validate_email_or_raise(data.get('email'))
            validate_phone_or_raise(data.get('phone'))
            data['phone'] = normalize_phone(data.get('phone'))
            add_contact(data)
            added += 1
    return added
