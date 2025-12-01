# === Файл автоматически дополнен док-стрингами и базовыми комментариями ===
'''"""
app.py — модуль проекта.

Этот файл был автоматически обогащён док-стрингами и базовыми комментариями.
Задачи модуля: опишите назначение, ключевые функции/классы и особенности реализации.
"""'''
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from typing import Optional
from database.db import (add_contact, delete_contacts, export_contacts_csv, import_contacts_csv,
                         init_db, list_contacts, update_contact)
from ui.ui import ContactDialog, MainWindow
from ui.ui_helpers import ask_yes_no


def main() -> None:
    """Точка входа настольного приложения Simple CRM.

    Инициализирует базу данных, создаёт главное окно, настраивает обработчики,
    загружает данные и запускает главный цикл Tk.
    """
    init_db()
    root = tk.Tk()
    root.title('CRM-система')
    root.geometry('1000x560')
    style = ttk.Style()
    style.theme_use('clam')

    def load(q: str='') -> None:
        """Загружает контакты из БД и передаёт их в таблицу.

        :param q: Строка поиска (по умолчанию пусто — все записи)
        """
        ui.set_rows(list_contacts(q))

    def on_add() -> None:
        """Открывает диалог создания контакта и сохраняет его при подтверждении."""
        dlg = ContactDialog(root, 'Новый контакт')
        if dlg.result:
            try:
                add_contact(dlg.result)
            except ValueError as e:
                messagebox.showerror('Ошибка валидации', str(e))
                return
            load()

    def on_edit(contact_id: Optional[int]) -> None:
        """Открывает диалог редактирования выбранной записи.

        :param contact_id: ``id`` выбранного контакта из таблицы
        """
        if not contact_id:
            messagebox.showinfo('Изменить', 'Выберите запись.')
            return
        item = ui.tree.item(str(contact_id))['values']
        initial = dict(name=item[0], email=item[1], phone=item[2], company=item[3], tags=item[4], notes=item[5])
        dlg = ContactDialog(root, 'Изменить контакт', initial=initial)
        if dlg.result:
            try:
                update_contact(contact_id, dlg.result)
            except ValueError as e:
                messagebox.showerror('Ошибка валидации', str(e))
                return
            load()

    def on_del(ids):
        title = "Удаление"
        msg = f"Удалить выбранную запись?" if len(ids) == 1 else f"Удалить выбранные записи ({len(ids)} шт.)?"
        if not ids:
            messagebox.showinfo("Удалить", "Выберите записи.")
            return
        if ask_yes_no(root, title, msg):
            delete_contacts(ids)
            load()
    # def on_del(contact_ids: list[int]):
    #     """Коллбэк удаления: удаляет одну или несколько выбранных записей."""
    #     if not contact_ids:
    #         messagebox.showinfo("Удалить", "Выберите записи.")
    #         return
    #
    #     n = len(contact_ids)
    #     title = "Удаление"
    #     msg = f"Удалить выбранную запись?" if n == 1 else f"Удалить выбранные записи ({n} шт.)?"
    #
    #     if messagebox.askyesno(title, msg):
    #         try:
    #             deleted = delete_contacts(contact_ids)
    #             # deleted может быть меньше n, если часть записей уже отсутствовала
    #             messagebox.showinfo("Готово", f"Удалено: {deleted}")
    #         except Exception as e:
    #             messagebox.showerror("Ошибка удаления", str(e))
    #         load()  # обновляем таблицу

    def on_search(q: str) -> None:
        """Применяет поиск по подстроке и обновляет таблицу."""
        load(q)

    def on_export() -> None:
        """Сохраняет все контакты в CSV-файл, выбранный пользователем."""
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')], title='Экспорт контактов в CSV')
        if not path:
            return
        try:
            n = export_contacts_csv(path)
            messagebox.showinfo('Экспорт завершён', f'Экспортировано записей: {n}')
        except Exception as e:
            messagebox.showerror('Ошибка экспорта', str(e))

    def on_import() -> None:
        """Импортирует контакты из выбранного CSV-файла."""
        path = filedialog.askopenfilename(filetypes=[('CSV', '*.csv')], title='Импорт контактов из CSV')
        if not path:
            return
        try:
            n = import_contacts_csv(path)
            load()
            messagebox.showinfo('Импорт завершён', f'Импортировано записей: {n}')
        except ValueError as e:
            messagebox.showerror('Ошибка валидации', str(e))
        except Exception as e:
            messagebox.showerror('Ошибка импорта', str(e))
    ui = MainWindow(root, on_add, on_edit, on_del, on_search, on_import, on_export)
    load()
    root.mainloop()
if __name__ == '__main__':
    main()