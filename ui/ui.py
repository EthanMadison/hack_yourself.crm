from __future__ import annotations
from typing import Callable, Dict, List, Optional
import re
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

NAME_ALLOWED = re.compile("^[A-Za-zА-Яа-яЁё\\-' ]*$")
PHONE_INPUT_PATTERN = re.compile('^[0-9+()\\- ]*$')

FIELD_LABELS = {
    "name": "ФИО",
    "email": "Электронная почта",
    "phone": "Номер телефона",
    "company": "Компания",
    "tags": "Теги",
    "notes": "Заметки",
}

def format_phone(phone_number: Optional[str]) -> str:
    """
    Возвращает красиво отформатированное представление телефона для UI.
    Пример: для номеров вида '+7XXXXXXXXXX' вернёт '+7 (XXX) XXX-XX-XX'.

    Параметры:
        phone_number: Нормализованный телефон (или произвольная строка).
    Возвращает:
        Строка для отображения.
    """
    if not phone_number:
        return ''
    digits = re.sub('\\D', '', phone_number)
    if (phone_number.startswith('+7')  or phone_number.startswith('8') or phone_number.startswith('7')
            and len(digits) == 11):
        return f'+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}'
    return phone_number

class ContactDialog(simpledialog.Dialog):
    """
    Модальное окно создания/редактирования контакта.
    Возвращает результат в свойстве 'result' (dict) после успешной валидации.
    """

    def __init__(self, parent: tk.Misc, title: str, initial: Optional[Dict]=None) -> None:
        self.result = None
        self.inputs = None
        self.initial: Dict = initial or {}
        super().__init__(parent, title)

    def body(self, master: tk.Misc) -> tk.Widget:
        """
        Строит форму и настраивает live-валидацию полей.

        Параметры:
            master: Родительский контейнер диалога.
        Возвращает:
            Виджет, получающий фокус при открытии (поле имени).
        """
        fields: List[str] = ['name', 'email', 'phone', 'company', 'tags', 'notes']
        self.inputs: Dict[str, ttk.Entry] = {}

        def _name_ok(new_value: str) -> bool:
            return bool(NAME_ALLOWED.fullmatch(new_value))

        def _phone_ok(new_value: str) -> bool:
            return bool(PHONE_INPUT_PATTERN.fullmatch(new_value))

        for i, f in enumerate(fields):
            label_text = FIELD_LABELS.get(f, f)
            ttk.Label(master, text=label_text + ':').grid(row=i, column=0, sticky='e', padx=6, pady=4)
            if f == 'name':
                ent = ttk.Entry(master, width=40)
                vcmd = (master.register(_name_ok), '%P')
                ent.configure(validate='key', validatecommand=vcmd)
            elif f == 'phone':
                vcmd = (master.register(_phone_ok), '%P')
                inv = (master.register(lambda: master.bell()),)
                ent = ttk.Entry(master, width=40, validate='key', validatecommand=vcmd, invalidcommand=inv)
            else:
                ent = ttk.Entry(master, width=40)
            ent.grid(row=i, column=1, sticky='we', padx=6, pady=4)
            ent.insert(0, self.initial.get(f, '') or '')
            self.inputs[f] = ent
        return self.inputs['name']

    def validate(self) -> bool:
        """Проверяет корректность данных при нажатии "ОК".

        Возвращает:
            'True' — закрыть окно; 'False' — оставить открытым.
        """
        name = self.inputs['name'].get().strip()
        email = self.inputs['email'].get().strip()
        if not name:
            messagebox.showwarning('Валидация', 'Ошибка. Поле "ФИО" обязательно для заполнения.')
            return False
        if not NAME_ALLOWED.fullmatch(name):
            messagebox.showwarning('Валидация', 'Ошибка. Поле "ФИО" должно содержать только буквы,'
                                                ' пробелы, дефис или апостроф.')
            return False
        if email and ('@' not in email or email.startswith('@') or email.endswith('@')):
            messagebox.showwarning('Валидация', "Ошибка. Проверьте корректность введённого email.")
            return False
        return True

    def apply(self) -> None:
        """Сохраняет значения полей из формы в 'self.result'."""
        self.result = {k: w.get().strip() for k, w in self.inputs.items()}

    def buttonbox(self):
        """Кастомная панель кнопок с русскими подписями."""
        box = ttk.Frame(self)

        ok_btn = ttk.Button(box, text="ОК", width=10, command=self.ok)
        ok_btn.pack(side="left", padx=5, pady=5)

        cancel_btn = ttk.Button(box, text="Отмена", width=10, command=self.cancel)
        cancel_btn.pack(side="left", padx=5, pady=5)

        # горячие клавиши
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

class MainWindow(ttk.Frame):
    """Главное окно приложения: поиск, действия и таблица контактов."""

    def __init__(self,
                 master: tk.Misc,
                 on_add: Callable[[], None],
                 on_edit: Callable[[Optional[int]], None],
                 on_del: Callable[[Optional[int]], None],
                 on_search: Callable[[str], None],
                 on_import: Callable[[], None],
                 on_export: Callable[[], None]
                 ) -> None:
        super().__init__(master)
        self.on_add, self.on_edit, self.on_del = (on_add, on_edit, on_del)
        self.on_search, self.on_import, self.on_export = (on_search, on_import, on_export)
        self.pack(fill='both', expand=True, padx=10, pady=10)
        top = ttk.Frame(self)
        top.pack(fill='x')
        self.q = tk.StringVar()
        ttk.Entry(top, textvariable=self.q).pack(side='left', fill='x', expand=True)
        ttk.Button(top, text='Поиск', command=self._search).pack(side='left', padx=5)
        ttk.Button(top, text='Сброс', command=self._reset).pack(side='left')
        btns = ttk.Frame(self)
        btns.pack(fill='x', pady=6)
        ttk.Button(btns, text='Добавить', command=self._add).pack(side='left')
        ttk.Button(btns, text='Изменить', command=self._edit).pack(side='left', padx=1)
        ttk.Button(btns, text='Удалить', command=self._del).pack(side='left')
        ttk.Button(btns, text='Экспорт CSV', command=self.on_export).pack(side='right', padx=0)
        ttk.Button(btns, text='Импорт CSV', command=self.on_import).pack(side='right')
        self.tree = ttk.Treeview(self, columns=('name', 'email', 'phone', 'company', 'tags', 'notes'),
                                 show='headings', selectmode="extended")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=FIELD_LABELS.get(col, col))
            self.tree.column(col, width=120, anchor="w")
        self.tree.pack(fill='both', expand=True)

    def set_rows(self, rows: List[Dict]) -> None:
        """Полностью перерисовывает содержимое таблицы по списку записей.

        Параметры:
            rows: Список словарей, как возвращает 'db.list_contacts'.
        """
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert('', 'end', iid=str(r['id']), values=(r['name'], r.get('email'),
                                                                  format_phone(r.get('phone')), r.get('company'),
                                                                  r.get('tags'), r.get('notes')))

    def selected_id(self) -> Optional[int]:
        """Возвращает 'id' выделенной строки или 'None'."""
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def selected_ids(self) -> list[int] | None:
        """Возвращает список ID всех выделенных строк (может быть пустым)."""
        selected_id = self.tree.selection()  # кортеж iids (строковые)
        return [int(s) for s in selected_id] if selected_id else []

    def _add(self) -> None:
        """Открывает диалог добавления и передаёт управление обработчику 'on_add'."""
        self.on_add()

    def _edit(self) -> None:
        """Запускает обработчик 'on_edit' для текущей выделенной записи."""
        self.on_edit(self.selected_id())

    def _del(self) -> None:
        """Удаляет выбранные записи, передавая их ID(ы) обработчику 'on_del'."""
        self.on_del(self.selected_ids())

    def _search(self) -> None:
        """Передаёт текущую строку поиска обработчику 'on_search'."""
        self.on_search(self.q.get().strip())

    def _reset(self) -> None:
        """Очищает строку поиска и сбрасывает фильтр (показывает все записи)."""
        self.q.set('')
        self.on_search('')
