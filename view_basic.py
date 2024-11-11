import logging
from tkinter import *
from tkinter import ttk
from localization import L10N
from seria_model import Ammo
from seria_controller import SeriaController
from view import FrameView
from view_utility import *


class BasicFrameView(FrameView):
    def __init__(self, mainview, controller: SeriaController):
        super().__init__(mainview, controller)
        self.logger = logging.getLogger('BasicFrameView')

        self.tree_ammo: ttk.Treeview = None

        # tuple of (entry, variable, editable, callback)
        self.ent_seria_attributes = list()
        # tuple of (scale, variable, callback)
        self.sc_seria_attributes = list()
        self.var_ammo_amount = StringVar()
        self.var_ammo_amount.trace_add('write', self._on_ammo_amount_change)

        self.frame: ttk.Notebook = ttk.Notebook(self.frm_container)
        self.frame.pack(fill=BOTH, expand=True)
        self.frame.add(self._make_player_frame(), text=L10N().text('PLAYER'))

    def enable(self):
        for entry, _, editable, _ in self.ent_seria_attributes:
            if editable:
                entry.config(state=NORMAL)
        for scale, _, _ in self.sc_seria_attributes:
            scale.config(state=NORMAL)
        self.ent_ammo_amount.config(state=NORMAL)

    def disable(self):
        for entry, _, _, _ in self.ent_seria_attributes:
            entry.config(state='readonly')
        for scale, _, _ in self.sc_seria_attributes:
            scale.config(state=DISABLED)
        self.ent_ammo_amount.config(state='readonly')

    def update(self):
        for _, variable, _, callback in self.ent_seria_attributes:
            variable.set(callback())
        for _, variable, callback in self.sc_seria_attributes:
            variable.set(callback())
        self._update_tree_ammo()

    def clear(self):
        for _, variable, _, _ in self.ent_seria_attributes:
            variable.set('')
        for _, variable, _ in self.sc_seria_attributes:
            variable.set(0)
        self._clear_tree_ammo()
        self.var_ammo_amount.set('')

    def _make_player_frame(self) -> Frame:
        frm_player = Frame(self.frame)
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
                                 lambda: self.controller.seria_node.get_attribute('gameVersion'))
        self._grid_lbl_ent_seria(frm_stat, L10N().text('CODENAME'), False,
                                 lambda: self.controller.seria_node.get_attribute('m_codename'))
        self._grid_lbl_ent_seria(frm_stat, L10N().text('SAVETIME'), False,
                                 lambda: self.controller.seria_node.get_attribute('m_savetime'))
        self._grid_lbl_ent_seria(frm_stat, L10N().text('SCORES'),
                                 src_callback=self.controller.profile_model.get_bonus,
                                 var_callback=self.controller.profile_model.set_bonus)
        self._grid_lbl_ent_seria(frm_stat, L10N().text('CASH'),
                                 src_callback=self.controller.profile_model.get_money,
                                 var_callback=self.controller.profile_model.set_money)
        grid_btn(frm_stat, L10N().text('UNLOCK_SHIPS'),
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
        self.ent_ammo_amount = grid_lbl_ent(frm_ammo, L10N().text(
            'EDIT_AMOUNT'), 'readonly', self.var_ammo_amount)

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

    def _grid_lbl_ent_seria(self, parent, text: str, editable: bool = True, src_callback=None, var_callback=None):
        # src_callback: use to get the value from model, triggered by code
        # var_callback: from variable, update the model value, triggered by user input
        var_str = StringVar()
        if var_callback is not None:
            var_str.trace_add(
                'write', lambda *args: var_callback(var_str.get()))
        entry = grid_lbl_ent(parent, text, 'readonly', var_str)
        self.ent_seria_attributes.append(
            (entry, var_str, editable, src_callback))

    def _grid_lbl_sc_seria_worldview(self, parent, text: str, attribute: str):
        var_int = IntVar()
        scale = grid_lbl_sc(parent, text, -3, 3, 0.25, var_int,
                            lambda *args: self.controller.profile_model.set_worldview(attribute, var_int.get()))
        scale.config(state=DISABLED)
        self.sc_seria_attributes.append((scale, var_int,
                                         lambda: self.controller.profile_model.get_worldview(attribute)))

    def _on_tree_ammo_select(self, event):
        self.logger.info(f'_on_tree_ammo_select: {event}')

        item_values = self.tree_ammo.item(self.tree_ammo.focus(), 'values')
        if item_values == '':
            return
        self.var_ammo_amount.set(item_values[1])

    def _on_ammo_amount_change(self, *args):
        self.logger.info(f'_on_ammo_amount_change: {args}')

        focus = self.tree_ammo.focus()

        item_values = self.tree_ammo.item(focus, 'values')

        # update the model
        if item_values == '':
            # Treeview will be unfocused if we click on other widget
            return

        ammo_type = item_values[0]
        if self.controller.profile_model.set_ammo(Ammo.get_ammo_index(ammo_type), self.var_ammo_amount.get()):
            # only update the view if the model update was successful
            self.tree_ammo.item(focus, values=(
                ammo_type, self.var_ammo_amount.get()))

    def _add_ammo(self, type: str):
        self.logger.info(f'_add_ammo: {type}')

        count = self.controller.profile_model.get_ammo_count(
            Ammo.get_ammo_index(type))
        if self.controller.profile_model.set_ammo(
                Ammo.get_ammo_index(type), str(int(count) + 1)):
            self._update_tree_ammo()

    def _update_tree_ammo(self):
        self.logger.info('_update_tree_ammo')

        self._clear_tree_ammo()
        for ammo in self.controller.profile_model.get_ammo_list():
            self.tree_ammo.insert('', 'end', values=(ammo[0], ammo[1]))

    def _clear_tree_ammo(self):
        self.logger.info('_clear_tree_ammo')

        self.tree_ammo.delete(*self.tree_ammo.get_children())
