from __future__ import annotations
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional, LiteralString
from database.db import (add_contact, delete_contacts, export_contacts_csv, import_contacts_csv,
                         init_db, list_contacts, update_contact)
from ui.ui import ContactDialog, MainWindow
from ui.ui_helpers import ask_yes_no


def _add_header_logo(parent: tk.Misc) -> None:
    """Показывает логотип в верхней части окна."""
    img_path = _resource_path("assets", "app.png")
    if not os.path.exists(img_path):
        return
    parent.logo_img = tk.PhotoImage(file=img_path)
    header = ttk.Frame(parent)
    header.pack(fill="x", pady=(6, 2))
    tk.Label(header, image=parent.logo_img).pack(side="left", padx=(6, 8))
    ttk.Label(header, text="hack_yourself.CRM", font=("Segoe UI", 14, "bold")).pack(side="left")

def _resource_path(*parts: str) -> LiteralString | str | bytes:
    """Находит файлы иконок как при обычном запуске, так и в PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, *parts)

def _set_app_icon(root: tk.Tk) -> None:
    """Ставит иконку для окна (.png/.ico). Без ошибок, даже если файл не найден."""
    try:
        # кроссплатформенно: .png через iconphoto
        png_path = _resource_path("assets", "app.png")
        if os.path.exists(png_path):
            img = tk.PhotoImage(file=png_path)
            root.iconphoto(True, img)
    except Exception:
        pass

    # доп. для Windows: если есть .ico, используем его тоже
    if sys.platform.startswith("win"):
        try:
            ico_path = _resource_path("assets", "app.ico")
            if os.path.exists(ico_path):
                root.iconbitmap(ico_path)
        except Exception:
            pass

def main() -> None:
    """
    Точка входа настольного приложения hack_yourself.CRM.

    Инициализирует базу данных, создаёт главное окно, настраивает обработчики,
    загружает данные и запускает главный цикл Tk.
    """
    init_db()
    root = tk.Tk()
    _set_app_icon(root)
    root.title('hack_yourself.CRM')
    _add_header_logo(root)
    root.geometry('1000x560')
    style = ttk.Style()
    style.theme_use('clam')


    def load(q: str='') -> None:
        """
        Загружает контакты из БД и передаёт их в таблицу.

        Аргументы:
            q: Строка поиска (по умолчанию пусто — все записи)
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
        """
        Открывает диалог редактирования выбранной записи.

        Аргументы:
            contact_id: 'id' выбранного контакта из таблицы
        """
        if not contact_id:
            messagebox.showinfo('Изменить', 'Выберите запись.')
            return
        item = ui.tree.item(str(contact_id))['values']
        initial = dict(
            name=item[0],
            email=item[1],
            phone=item[2],
            company=item[3],
            tags=item[4],
            notes=item[5]
        )
        dlg = ContactDialog(root, 'Изменить контакт', initial=initial)
        if dlg.result:
            try:
                update_contact(contact_id, dlg.result)
            except ValueError as e:
                messagebox.showerror('Ошибка валидации', str(e))
                return
            load()

    def on_del(ids: len) -> None:
        title = "Удаление"
        msg = f"Удалить выбранную запись?" if len(ids) == 1 else f"Удалить выбранные записи ({len(ids)} шт.)?"
        if not ids:
            messagebox.showinfo("Удалить", "Выберите записи.")
            return
        if ask_yes_no(root, title, msg):
            delete_contacts(ids)
            load()

    def on_search(q: str) -> None:
        """Применяет поиск по подстроке и обновляет таблицу."""
        load(q)

    def on_export() -> None:
        """Сохраняет все контакты в CSV-файл, выбранный пользователем."""
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV', '*.csv')],
            title='Экспорт контактов в CSV'
        )
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
