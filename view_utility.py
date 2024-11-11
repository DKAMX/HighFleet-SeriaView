from tkinter import *
from tkinter import filedialog, messagebox


def ask_directory(title: str):
    return filedialog.askdirectory(title=title)


def ask_openfilename(title: str):
    return filedialog.askopenfilename(filetypes=[('Seria files', '*.seria')], title=title)


def ask_savefilename(title: str):
    return filedialog.asksaveasfilename(filetypes=[('Seria files', '*.seria')], title=title)


def show_message(title: str, message: str):
    messagebox.showinfo(title, message)


def grid_btn(master: Frame, text: str, command):
    _, row = master.grid_size()
    button = Button(master, text=text, command=command)
    button.grid(row=row, column=0, sticky=EW)
    return button


def grid_lbl_ent(parent, text: str, state: str = NORMAL, variable: StringVar = None):
    _, row = parent.grid_size()
    label = Label(parent, text=text)
    entry = Entry(parent, state=state, textvariable=variable, width=10)
    label.grid(row=row, column=0, sticky=W)
    entry.grid(row=row, column=1, sticky=EW)
    return entry


def grid_lbl_sc(parent, text: str, from_: int, to: int, step: int, variable: StringVar = None, callback=None):
    _, row = parent.grid_size()

    label = Label(parent, text=text)
    scale = Scale(parent, orient=HORIZONTAL, variable=variable, digits=3,
                  from_=from_, to=to, resolution=step, length=10, width=5)
    label.grid(row=row, column=0, sticky=W)
    scale.grid(row=row, column=1, sticky=EW)

    if variable is not None:
        variable.trace_add('write', callback)

    return scale
