import tkinter as tk
from tkinter import ttk

def ask_yes_no(parent: tk.Misc, title: str, message: str) -> bool:
    """
    Показывает модальное окно подтверждения с кнопками «Да» и «Отмена».
    Диалог делает окно модальным (grab_set), привязывает Enter к действию «Да»,
    Esc — к «Отмена» и возвращает выбор пользователя в виде булева значения.

    Параметры:
        parent: Родительский виджет/окно;
        title: Заголовок диалогового окна;
        message: Текст сообщения внутри диалога.

    Возвращает:
        bool: 'True', если пользователь нажал «Да», иначе 'False'.
    """
    win = tk.Toplevel(parent)
    win.title(title)
    win.transient(parent)
    win.grab_set()

    ttk.Label(win, text=message, wraplength=380, justify="left").pack(padx=16, pady=(16,10))

    var = tk.BooleanVar(value=False)

    btns = ttk.Frame(win); btns.pack(padx=16, pady=(0,16))
    def _yes(): var.set(True);  win.destroy()
    def _no():  var.set(False); win.destroy()

    ttk.Button(btns, text="Да", command=_yes, width=10).pack(side="left", padx=6)
    ttk.Button(btns, text="Отмена", command=_no, width=10).pack(side="left", padx=6)

    win.bind("<Return>", lambda e: _yes())
    win.bind("<Escape>", lambda e: _no())

    parent.wait_window(win)
    return bool(var.get())
