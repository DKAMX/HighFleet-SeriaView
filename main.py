import json
import locale
import logging
import logging.config
import sys
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from seria_model import Ammo, AmmoModel
from view_controller import SeriaController

__author__ = 'Max'
__version__ = '0.3.0'

_LOCALE_PATH = 'locale'
_LOCALE_DEFAULT = 'en_US'

_VIEWMODE_SETTINGS = 0
_VIEWMODE_BASE = 1
_VIEWMODE_MAP = 2
_VIEWMODE_TREE = 3


# logging.basicConfig(level=logging.INFO)


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class L10N:
    def __init__(self):
        code, _ = locale.getdefaultlocale()
        self.messages = self._load_locale(code)
        self.messages_default = self._load_locale(_LOCALE_DEFAULT)

    def _load_locale(self, code):
        try:
            filepath = f'{sys._MEIPASS}/{code}.json' if is_bundled(
            ) else f'{_LOCALE_PATH}/{code}.json'
            with open(filepath, encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return dict()

    def text(self, key):
        return self.messages.get(key, self.messages_default.get(key, key))


class SeriaView:
    def __init__(self):
        self.logger = logging.getLogger('SeriaView')

        self.controller: SeriaController = SeriaController()

        self.root = Tk()
        self.root.title(f'SeriaView v{__version__}')
        self.root.geometry('640x480')
        self.root.minsize(640, 480)
        # self.root.resizable(False, False)

        # view related variable
        self.frame_list = list()
        self.tree_ammo: ttk.Treeview = None

        self.var_viewmode = IntVar(value=_VIEWMODE_BASE)
        self.var_viewmode.trace_add('write', self._on_viewmode_change)
        self.var_gamepath = StringVar(
            value=self.controller.config.get('gamepath', ''))
        self.var_ammo_amount = StringVar()

        # tuple of (entry, variable, editable, callback)
        self.ent_seria_attributes = list()
        # tuple of (scale, variable, callback)
        self.sc_seria_attributes = list()
        self.btn_seria_actions = list()
        self.ent_ammo_amount: Entry = None

        self.menu_file: Menu = None
        self._make_menu()

        # make frames, maintain this invokation order
        self._make_settings()
        self._make_baseview()
        self._make_mapview()
        self._make_treeview()

        # set the initial view
        if self.var_gamepath.get() == '':
            self.var_viewmode.set(_VIEWMODE_SETTINGS)
        self._on_viewmode_change()

        if self.controller.text is not None:
            self.menu_file.entryconfig(1, state=NORMAL)  # OPEN_PROFILE

        self.root.mainloop()

    # helper methods for building the widgets

    def _grid_btn(self, parent: Frame, text: str, command):
        _, row = parent.grid_size()

        button = Button(parent, text=text, command=command)
        button.grid(row=row, column=0, sticky=EW)

        return button

    def _grid_lbl_ent(self, parent, text: str, state: str = NORMAL, variable: StringVar = None, callback=None):
        _, row = parent.grid_size()

        label = Label(parent, text=text)
        entry = Entry(parent, state=state, textvariable=variable, width=10)
        label.grid(row=row, column=0, sticky=W)
        entry.grid(row=row, column=1, sticky=EW)

        if variable is not None:
            variable.trace_add('write', callback)

        return entry

    def _grid_lbl_ent_seria(self, parent, text: str, editable: bool = True, src_callback=None, var_callback=None):
        # src_callback: use to get the value from model, triggered by code
        # var_callback: from variable, update the model value, triggered by user input
        var_str = StringVar()
        entry = self._grid_lbl_ent(parent, text, 'readonly', var_str, lambda *args: var_callback(
            var_str.get()) if var_callback is not None else None)
        self.ent_seria_attributes.append(
            (entry, var_str, editable, src_callback))

    def _grid_lbl_sc(self, parent, text: str, from_: int, to: int, step: int, variable: StringVar = None, callback=None):
        _, row = parent.grid_size()

        label = Label(parent, text=text)
        scale = Scale(parent, orient=HORIZONTAL, variable=variable, digits=3,
                      from_=from_, to=to, resolution=step, length=10, width=5)
        label.grid(row=row, column=0, sticky=W)
        scale.grid(row=row, column=1, sticky=EW)

        if variable is not None:
            variable.trace_add('write', callback)

        return scale

    def _grid_lbl_sc_seria(self, parent, text: str, from_: int, to: int, step: int, src_callback=None, var_callback=None):
        var_int = IntVar()
        scale = self._grid_lbl_sc(parent, text, from_, to, step, var_int, lambda *args: var_callback(
            var_int.get()) if var_callback is not None else None)
        scale.config(state=DISABLED)
        self.sc_seria_attributes.append((scale, var_int, src_callback))

    def _grid_lbl_sc_seria_worldview(self, parent, text: str, attribute: str):
        self._grid_lbl_sc_seria(parent, text, -3, 3, 0.25,
                                lambda: self.controller.profile_model.get_worldview(
                                    attribute),
                                lambda v: self.controller.profile_model.set_worldview(attribute, v))

    # methods defining the view

    def _make_menu(self):
        menu = Menu(self.root)

        self.menu_file = Menu(menu, tearoff=False)
        self.menu_file.add_command(
            label=L10N().text('OPEN'), command=self._open_file)

        menu_file_profile = Menu(self.menu_file, tearoff=False)
        menu_file_profile.add_command(label=L10N().text(
            'PROFILE_1'), command=lambda: self._open_profile(1))
        menu_file_profile.add_command(label=L10N().text(
            'PROFILE_2'), command=lambda: self._open_profile(2))
        menu_file_profile.add_command(label=L10N().text(
            'PROFILE_3'), command=lambda: self._open_profile(3))
        self.menu_file.add_cascade(label=L10N().text(
            'OPEN_PROFILE'), state=DISABLED, menu=menu_file_profile)

        self.menu_file.add_command(
            label=L10N().text('SAVE'), command=self._save_file)
        self.menu_file.add_command(label=L10N().text(
            'CLOSE'), command=self._close_file)
        self.menu_file.add_command(label=L10N().text(
            'SETTINGS'), command=lambda: self.var_viewmode.set(_VIEWMODE_SETTINGS))
        menu.add_cascade(label=L10N().text('FILE'), menu=self.menu_file)

        menu_view = Menu(menu, tearoff=False)
        menu_view.add_radiobutton(label=L10N().text(
            'VIEW_BASE'), value=_VIEWMODE_BASE, variable=self.var_viewmode, command=self._on_viewmode_change)
        # menu_view.add_radiobutton(label=L10N().text(
        #     'VIEW_MAP'), value=_VIEWMODE_MAP, variable=self.var_viewmode, command=self._on_viewmode_change)
        # menu_view.add_radiobutton(label=L10N().text(
        #     'VIEW_TREE'), value=_VIEWMODE_TREE, variable=self.var_viewmode, command=self._on_viewmode_change)
        menu.add_cascade(label=L10N().text('VIEW'), menu=menu_view)

        menu.add_command(label=L10N().text('ABOUT'), command=self._about)

        self.root.config(menu=menu)

    def _make_settings(self):
        frm_settings = Frame(self.root)
        self.frame_list.append(frm_settings)

        frm_settings.columnconfigure(1, weight=1)

        self._grid_btn(frm_settings, L10N().text('BACK'),
                       lambda: self.var_viewmode.set(_VIEWMODE_BASE))
        self._grid_lbl_ent(frm_settings, L10N().text(
            'GAME_PATH'), 'readonly', self.var_gamepath, self._on_gamepath_change)
        Button(frm_settings, command=self._set_gamepath,
               text=L10N().text('BROWSE')).grid(row=1, column=2)

    def _make_baseview(self):
        frm_baseview = ttk.Notebook(self.root)
        self.frame_list.append(frm_baseview)

        # frm_fleet = Frame(frm_baseview)
        # frm_npc = Frame(frm_baseview)

        # frm_fleet.pack(fill=BOTH, expand=True)
        # frm_npc.pack(fill=BOTH, expand=True)

        frm_baseview.add(self._make_player_frame(
            frm_baseview), text=L10N().text('PLAYER'))
        # frm_baseview.add(frm_fleet, text=L10N().text('FLEET'))
        # frm_baseview.add(frm_npc, text=L10N().text('NPC'))

    def _make_mapview(self):
        frm_mapview = Frame(self.root)
        self.frame_list.append(frm_mapview)

    def _make_treeview(self):
        frm_treeview = Frame(self.root)
        self.frame_list.append(frm_treeview)

    def _make_player_frame(self, parent) -> Frame:
        # player frame (basic information panel)
        frm_player = Frame(parent)
        frm_player.pack(fill=BOTH, expand=True)
        frm_player.columnconfigure(0, weight=1)
        frm_player.columnconfigure(1, weight=1)
        frm_player.rowconfigure(0, weight=1)
        frm_player.rowconfigure(1, weight=2)

        # stat panel
        frm_stat = Frame(frm_player)
        frm_stat.grid(row=0, column=0, sticky=NSEW)
        frm_stat.columnconfigure(0, weight=1)
        frm_stat.columnconfigure(1, weight=1)
        frm_stat.grid_propagate(False)

        self._grid_lbl_ent_seria(frm_stat, L10N().text('GAME_VERSION'), False,
                                 lambda: self.controller.seria.get_attribute('gameVersion'))
        self._grid_lbl_ent_seria(frm_stat, L10N().text('CODENAME'), False,
                                 lambda: self.controller.seria.get_attribute('m_codename'))
        self._grid_lbl_ent_seria(frm_stat, L10N().text('SAVETIME'), False,
                                 lambda: self.controller.seria.get_attribute('m_savetime'))
        self._grid_lbl_ent_seria(frm_stat, L10N().text('SCORES'),
                                 src_callback=self.controller.profile_model.get_bonus,
                                 var_callback=self.controller.profile_model.set_bonus)
        self._grid_lbl_ent_seria(frm_stat, L10N().text('CASH'),
                                 src_callback=self.controller.profile_model.get_money,
                                 var_callback=self.controller.profile_model.set_money)
        self._grid_btn(frm_stat, L10N().text('UNLOCK_SHIPS'),
                       self.controller.profile_model.unlock_all_ships)

        # worldview panel
        frm_worldview = LabelFrame(frm_player, text=L10N().text('WORLDVIEW'))
        frm_worldview.grid(row=1, column=0, sticky=NSEW)
        frm_worldview.columnconfigure(0, weight=1)
        frm_worldview.columnconfigure(1, weight=4)
        frm_worldview.grid_propagate(False)

        self._grid_lbl_sc_seria_worldview(
            frm_worldview, L10N().text('FEAR'), 'fear')
        self._grid_lbl_sc_seria_worldview(
            frm_worldview, L10N().text('GERAT'), 'gerat')
        self._grid_lbl_sc_seria_worldview(
            frm_worldview, L10N().text('ROMANI'), 'romani')
        self._grid_lbl_sc_seria_worldview(
            frm_worldview, L10N().text('FAITH'), 'faith')
        self._grid_lbl_sc_seria_worldview(
            frm_worldview, L10N().text('ORDER'), 'order')
        self._grid_lbl_sc_seria_worldview(
            frm_worldview, L10N().text('FORCE'), 'force')
        self._grid_lbl_sc_seria_worldview(
            frm_worldview, L10N().text('WEALTH'), 'wealth')
        self._grid_lbl_sc_seria_worldview(
            frm_worldview, L10N().text('KINDNESS'), 'kindness')

        # ammo panel
        frm_ammo = LabelFrame(frm_player, text=L10N().text('AMMO_REG'))
        frm_ammo.grid(row=0, column=1, rowspan=2, sticky=NSEW)
        frm_ammo.columnconfigure(0, weight=1)
        frm_ammo.columnconfigure(1, weight=1)
        frm_ammo.rowconfigure(0, weight=1)
        frm_ammo.grid_propagate(False)

        self.tree_ammo = ttk.Treeview(
            frm_ammo, columns=['type', 'count'], selectmode=BROWSE)
        self.tree_ammo.heading('#0', text='')
        self.tree_ammo.heading('type', anchor=CENTER, text=L10N().text('TYPE'))
        self.tree_ammo.heading('count', anchor=CENTER,
                               text=L10N().text('AMOUNT'))
        self.tree_ammo.column('#0', width=0, stretch=False)
        self.tree_ammo.column('type', width=200)
        self.tree_ammo.column('count', anchor=CENTER, width=50)
        self.tree_ammo.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        sb_ammo = ttk.Scrollbar(frm_ammo, orient='vertical',
                                command=self.tree_ammo.yview)
        sb_ammo.grid(row=0, column=2, sticky=NS)
        self.tree_ammo.config(yscrollcommand=sb_ammo.set)
        self.tree_ammo.bind('<<TreeviewSelect>>', self._on_tree_ammo_select)
        self.ent_ammo_amount = self._grid_lbl_ent(frm_ammo, L10N().text(
            'EDIT_AMOUNT'), 'readonly', self.var_ammo_amount, self._on_ammo_amount_change)

        Label(frm_ammo, text=L10N().text('ADD_AMMO')).grid(
            row=2, column=0, sticky=W)
        ammo_types = tuple(Ammo.get_ammo_types())
        var_ammo_type_select = StringVar()
        menu_ammo = OptionMenu(frm_ammo, var_ammo_type_select, *ammo_types)
        menu_ammo.config(width=25)
        menu_ammo.grid(row=3, column=0, sticky=EW)
        btn_add_ammo = Button(frm_ammo, text=L10N().text(
            'ADD'), command=lambda: self._add_ammo(var_ammo_type_select.get()))
        btn_add_ammo.grid(row=3, column=1, sticky=EW)

        return frm_player

    # event handlers

    def _on_viewmode_change(self, *args):
        self.logger.info(f'_on_viewmode_change: {args}')

        for frm in self.frame_list:
            frm.pack_forget()
        view = self.var_viewmode.get()
        self.frame_list[view].pack(fill=BOTH, expand=True)

    def _on_gamepath_change(self, *args):
        self.logger.info(f'_on_gamepath_change: {args}')

        self.controller.set_gamepath(self.var_gamepath.get())
        # if text is None, we assume the gamepath is invalid, thus disable the profile menu
        if self.controller.text is None:
            self.menu_file.entryconfig(1, state=DISABLED)  # OPEN_PROFILE
        else:
            self.menu_file.entryconfig(1, state=NORMAL)

    def _on_ammo_amount_change(self, *args):
        self.logger.info(f'_on_ammo_amount_change: {args}')

        focus = self.tree_ammo.focus()

        ammo_type = self.tree_ammo.item(focus, 'values')[0]

        # update the model
        if ammo_type == '':
            # Treeview will be unfocused if we click on other widget
            return
        if self.controller.profile_model.set_ammo(Ammo.get_ammo_index(ammo_type), self.var_ammo_amount.get()):
            # only update the view if the model update was successful
            self.tree_ammo.item(focus, values=(
                ammo_type, self.var_ammo_amount.get()))

    def _update_view(self):
        self.logger.info('_update_view')

        for entry, variable, editable, callback in self.ent_seria_attributes:
            variable.set(callback())
            if editable:
                entry.config(state=NORMAL)

        for scale, variable, callback in self.sc_seria_attributes:
            variable.set(callback())
            scale.config(state=NORMAL)

        self._update_tree_ammo()
        self.ent_ammo_amount.config(state=NORMAL)

    def _clear_view(self):
        self.logger.info('_clear_view')

        for entry, variable, _, _ in self.ent_seria_attributes:
            entry.config(state='readonly')
            variable.set('')

        for scale, variable, _ in self.sc_seria_attributes:
            scale.config(state=DISABLED)
            variable.set(0)

        self.tree_ammo.delete(*self.tree_ammo.get_children())
        self.ent_ammo_amount.config(state='readonly')

    def _update_tree_ammo(self):
        self.logger.info('_update_tree_ammo')

        self.tree_ammo.delete(*self.tree_ammo.get_children())
        for ammo in self.controller.profile_model.get_ammo_list():
            self.tree_ammo.insert('', 'end', values=(ammo[0], ammo[1]))

    def _on_tree_ammo_select(self, event):
        self.logger.info(f'_on_tree_ammo_select: {event}')

        item_values = self.tree_ammo.item(self.tree_ammo.focus(), 'values')
        if item_values == '':
            return
        self.var_ammo_amount.set(item_values[1])

    def _add_ammo(self, type: str):
        count = self.controller.profile_model.get_ammo_count(
            Ammo.get_ammo_index(type))
        if self.controller.profile_model.set_ammo(
                Ammo.get_ammo_index(type), str(int(count) + 1)):
            self._update_tree_ammo()

    def _open_file(self):
        self.logger.info('open_file')

        path = ask_openfilename('')
        if path == '' or isinstance(path, tuple):
            return
        self.controller.load_seria(path)
        self._update_view()
        self.root.title(f'{path} - SeriaView v{__version__}')

    def _open_profile(self, index: int):
        self.logger.info(f'open_profile: {index}')

        path = self.controller.load_profile(index)
        self._update_view()
        self.root.title(f'{path} - SeriaView v{__version__}')

    def _save_file(self):
        self.logger.info('save_file')

        if self.controller.seria is None:
            return

        path = ask_savefilename('')
        if path == '' or isinstance(path, tuple):
            return
        self.controller.save_seria(path)

    def _close_file(self):
        self.logger.info('close_file')

        self.controller.seria = None
        self._clear_view()
        self.root.title(f'SeriaView v{__version__}')

    def _set_gamepath(self):
        self.logger.info('set_gamepath')

        path = ask_directory(L10N().text('GAME_PATH'))
        if path == '' or isinstance(path, tuple):
            return
        self.var_gamepath.set(path)

    def _about(self):
        self.logger.info('_about')

        show_message('About', f'''SeriaView v{__version__}
Developed by {__author__}
More information at: https://github.com/DKAMX/HighFleet-SeriaView''')


def ask_directory(title: str):
    return filedialog.askdirectory(title=title)


def ask_openfilename(title: str):
    return filedialog.askopenfilename(filetypes=[('Seria files', '*.seria')], title=title)


def ask_savefilename(title: str):
    return filedialog.asksaveasfilename(filetypes=[('Seria files', '*.seria')], title=title)


def show_message(title: str, message: str):
    messagebox.showinfo(title, message)


def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


if __name__ == '__main__':
    SeriaView()
