import logging
from tkinter import *
from tkinter import ttk
from localization import L10N
from seria_model import *
from seria_controller import SeriaController
from view import FrameView
from view_utility import *


class BasicFrameView(FrameView):
    def __init__(self, mainview, controller: SeriaController):
        super().__init__(mainview, controller)
        self.logger = logging.getLogger('BasicFrameView')

        self.tree_ammo: ttk.Treeview = None
        self.tree_ship: ttk.Treeview = None
        self.tree_parts: ttk.Treeview = None
        self.tree_escadra: ttk.Treeview = None
        self.tree_hold: ttk.Treeview = None

        # tuple of (entry, variable, editable, callback)
        self.ent_seria_attributes = list()
        # tuple of (scale, variable, callback)
        self.sc_seria_attributes = list()
        self.ent_ammo_amount: Entry = None
        self.var_ammo_amount = StringVar()
        self.var_ammo_amount.trace_add('write', self._on_ammo_amount_change)

        self.ent_part_amount: Entry = None
        self.var_part_amount = StringVar()
        self.var_part_amount.trace_add('write', self._on_part_amount_change)

        # tuple of (type (ship/part), name/oid), used for adding ship/part to squadron/ship hold
        self.select_obj: tuple = None
        self.select_escadra_index: int = None

        self.frame: ttk.Notebook = ttk.Notebook(self.frm_container)
        self.frame.pack(fill=BOTH, expand=True)
        self.frame.add(self._make_player_frame(), text=L10N().text('PLAYER'))
        self.frame.add(self._make_fleet_frame(), text=L10N().text('FLEET'))

    def enable(self):
        if not self.controller.is_profile():
            return

        for entry, _, editable, _ in self.ent_seria_attributes:
            if editable:
                entry.config(state=NORMAL)
        for scale, _, _ in self.sc_seria_attributes:
            scale.config(state=NORMAL)
        self.ent_ammo_amount.config(state=NORMAL)
        self.ent_part_amount.config(state=NORMAL)

    def disable(self):
        for entry, _, _, _ in self.ent_seria_attributes:
            entry.config(state='readonly')
        for scale, _, _ in self.sc_seria_attributes:
            scale.config(state=DISABLED)
        self.ent_ammo_amount.config(state='readonly')
        self.ent_part_amount.config(state='readonly')

    def update(self):
        if not self.controller.is_profile():
            return

        for _, variable, _, callback in self.ent_seria_attributes:
            variable.set(callback())
        for _, variable, callback in self.sc_seria_attributes:
            variable.set(callback())
        self._update_tree_ammo()
        self._update_tree_escadra()

    def clear(self):
        for _, variable, _, _ in self.ent_seria_attributes:
            variable.set('')
        for _, variable, _ in self.sc_seria_attributes:
            variable.set(0)
        self._clear_tree_ammo()
        self.var_ammo_amount.set('')
        self._clear_tree_escadra()
        self.var_part_amount.set('')
        self._clear_tree_hold()
        self.select_obj = None
        self.select_escadra_index = None

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

    def _make_fleet_frame(self) -> Frame:
        frm_fleet = Frame(self.frame)
        frm_fleet.pack(fill=BOTH, expand=True)

        frm_fleet.columnconfigure(0, weight=1)
        frm_fleet.columnconfigure(1, weight=1)
        frm_fleet.columnconfigure(2, weight=1)
        frm_fleet.rowconfigure(0, weight=1)
        frm_fleet.rowconfigure(1, weight=1)

        # ship panel
        frm_ship = LabelFrame(frm_fleet, text=L10N().text('SHIP_DESIGN'))
        frm_ship.grid(row=0, column=0, sticky=NSEW)
        frm_ship.propagate(False)

        self.tree_ship = ttk.Treeview(frm_ship, selectmode=BROWSE, show='tree')
        self.tree_ship.pack(expand=True, fill=BOTH, side=LEFT)

        sb_ship = ttk.Scrollbar(frm_ship, orient='vertical',
                                command=self.tree_ship.yview)
        sb_ship.pack(fill=Y, side=RIGHT)
        self.tree_ship.config(yscrollcommand=sb_ship.set)
        self.tree_ship.bind('<<TreeviewSelect>>', self._on_tree_ship_select)
        self.tree_ship.bind('<Button-1>', self._deselect_tree_parts)

        # item panel
        frm_parts = LabelFrame(frm_fleet, text=L10N().text('ITEM'))
        frm_parts.grid(row=1, column=0, sticky=NSEW)
        frm_parts.propagate(False)

        self.tree_parts = ttk.Treeview(frm_parts, selectmode=BROWSE,
                                       show='tree')
        self.tree_parts.pack(expand=True, fill=BOTH, side=LEFT)

        sb_parts = ttk.Scrollbar(frm_parts, orient='vertical',
                                 command=self.tree_parts.yview)
        sb_parts.pack(fill=Y, side=RIGHT)
        self.tree_parts.config(yscrollcommand=sb_parts.set)
        self.tree_parts.bind('<<TreeviewSelect>>', self._on_tree_parts_select)
        self.tree_parts.bind('<Button-1>', self._deselect_tree_ship)

        # squadron panel
        frm_escadra = LabelFrame(frm_fleet, text=L10N().text('ESCADRA'))
        frm_escadra.grid(row=0, column=1, rowspan=2, sticky=NSEW)
        frm_escadra.columnconfigure(0, weight=1)
        frm_escadra.rowconfigure(0, weight=1)
        frm_escadra.grid_propagate(False)

        frm_escadra_tree = Frame(frm_escadra)
        frm_escadra_tree.grid(row=0, column=0, sticky=NSEW)

        self.tree_escadra = ttk.Treeview(frm_escadra_tree, selectmode=BROWSE,
                                         show='tree')
        self.tree_escadra.pack(expand=True, fill=BOTH, side=LEFT)

        sb_escadra = ttk.Scrollbar(frm_escadra_tree, orient='vertical',
                                   command=self.tree_escadra.yview)
        sb_escadra.pack(fill=Y, side=RIGHT)
        self.tree_escadra.config(yscrollcommand=sb_escadra.set)
        self.tree_escadra.bind('<ButtonRelease-1>',
                               self._on_tree_escadra_select)

        Label(frm_escadra, text=L10N().text('TIP_BASIC_FLEET_ADD')).grid(
            column=0, row=1, sticky=W)
        grid_btn(frm_escadra, L10N().text('ADD'), self._add_node)

        # shiphold panel
        frm_hold = LabelFrame(frm_fleet, text=L10N().text('SHIPHOLD'))
        frm_hold.grid(row=0, column=2, rowspan=2, sticky=NSEW)
        frm_hold.columnconfigure(0, weight=1)
        frm_hold.rowconfigure(0, weight=1)
        frm_hold.grid_propagate(False)

        frm_hold_tree = Frame(frm_hold)
        frm_hold_tree.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        self.tree_hold = ttk.Treeview(frm_hold_tree, selectmode=BROWSE,
                                      show='headings',
                                      columns=['name', 'count'])
        self.tree_hold.heading('#0', text='')
        self.tree_hold.heading('name', text=L10N().text('NAME'))
        self.tree_hold.heading('count', text=L10N().text('AMOUNT'))
        self.tree_hold.column('#0', width=0, stretch=False)
        self.tree_hold.column('name', width=125)
        self.tree_hold.column('count', width=5)
        self.tree_hold.pack(expand=True, fill=BOTH, side=LEFT)

        sb_hold = ttk.Scrollbar(frm_hold_tree, orient='vertical',
                                command=self.tree_hold.yview)
        sb_hold.pack(fill=Y, side=RIGHT)
        self.tree_hold.config(yscrollcommand=sb_hold.set)
        self.tree_hold.bind('<<TreeviewSelect>>', self._on_tree_hold_select)

        self.ent_part_amount = grid_lbl_ent(frm_hold, L10N().text('EDIT_AMOUNT'),
                                            'readonly', self.var_part_amount)

        return frm_fleet

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

    def _on_tree_ship_select(self, event):
        self.logger.info(f'_on_tree_ship_select: {event}')

        focus = self.tree_ship.focus()
        if focus == '':
            return
        self.select_obj = ('ship', self.tree_ship.item(focus, 'text'))

    def _on_tree_parts_select(self, event):
        self.logger.info(f'_on_tree_parts_select: {event}')

        focus = self.tree_parts.focus()
        if focus == '':
            return
        self.select_obj = ('part', self.tree_parts.item(focus, 'values')[0])

    def _on_tree_escadra_select(self, event):
        self.logger.info(f'_on_tree_escadra_select: {event}')

        focus = self.tree_escadra.focus()
        if focus == '':
            return

        parent = self.tree_escadra.parent(focus)
        if parent:
            # only select the parent squadron (highlight)
            self.tree_escadra.selection_set(parent)
            self.select_escadra_index = self.tree_escadra.index(parent)
        else:
            self.select_escadra_index = self.tree_escadra.index(focus)

        self._update_tree_hold()

    def _on_tree_hold_select(self, event):
        self.logger.info(f'_on_tree_hold_select: {event}')

        focus = self.tree_hold.focus()
        if focus == '':
            return
        item_values = self.tree_hold.item(focus, 'values')
        self.var_part_amount.set(item_values[1])

    def _deselect_tree_ship(self, event):
        self.logger.info(f'_deselect_tree_ship: {event}')

        self.tree_ship.selection_remove(self.tree_ship.selection())

    def _deselect_tree_parts(self, event):
        self.logger.info(f'_deselect_tree_parts: {event}')

        self.tree_parts.selection_remove(self.tree_parts.selection())

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
            self.tree_ammo.item(focus,
                                values=(ammo_type, self.var_ammo_amount.get()))

    def _on_part_amount_change(self, *args):
        self.logger.info(f'_on_part_amount_change: {args}')

        focus = self.tree_hold.focus()

        item_values = self.tree_hold.item(focus, 'values')
        if item_values == '':
            return

        index = self.tree_hold.index(focus)
        if self.controller.profile_model.get_squadron(self.select_escadra_index).set_item(index, self.var_part_amount.get()):
            self.tree_hold.item(focus,
                                values=(item_values[0], self.var_part_amount.get()))

    def _add_ammo(self, type: str):
        self.logger.info(f'_add_ammo: {type}')

        count = self.controller.profile_model.get_ammo_count(
            Ammo.get_ammo_index(type))
        if self.controller.profile_model.set_ammo(
                Ammo.get_ammo_index(type), str(int(count) + 1)):
            self._update_tree_ammo()

    def _add_node(self):
        self.logger.info('_add_node')

        if self.select_obj is None:
            return
        type = self.select_obj[0]
        value = self.select_obj[1]
        if type == 'ship':
            # self.controller.profile_model.add_ship(value)
            pass
        elif type == 'part':
            squadron = self.controller.profile_model.get_squadron(
                self.select_escadra_index)
            squadron.add_item(self.controller.profile_model.unique_ids,
                              self.controller.parts[value], 1)
            self._update_tree_hold()

    def _update_tree_ammo(self):
        self.logger.info('_update_tree_ammo')

        self._clear_tree_ammo()
        for ammo in self.controller.profile_model.get_ammo_list():
            self.tree_ammo.insert('', 'end', values=(ammo[0], ammo[1]))

    def _clear_tree_ammo(self):
        self.logger.info('_clear_tree_ammo')

        self.tree_ammo.delete(*self.tree_ammo.get_children())

    def _clear_tree_ship(self):
        self.logger.info('_clear_tree_ship')

    def _update_tree_escadra(self):
        self.logger.info('_update_tree_escadra')

        self._clear_tree_escadra()
        for squadron in self.controller.profile_model.player_squadrons:
            iid = self.tree_escadra.insert('', 'end', text=squadron.name)
            for ship in squadron.ships:
                self.tree_escadra.insert(iid, 'end', text=get_ship_name(ship))

        # expand tree root by default
        for child in self.tree_escadra.get_children():
            self.tree_escadra.item(child, open=True)

    def _clear_tree_escadra(self):
        self.logger.info('_clear_tree_escadra')

        self.tree_escadra.delete(*self.tree_escadra.get_children())

    def _update_tree_hold(self):
        self.logger.info('_update_tree_hold')

        self._clear_tree_hold()

        squadron = self.controller.profile_model.get_squadron(
            self.select_escadra_index)
        for item in squadron.get_items():
            self.tree_hold.insert('', 'end',
                                  values=(self.controller.get_oid_text(item[0]),
                                          item[1]))  # count

    def _clear_tree_hold(self):
        self.logger.info('_clear_tree_hold')

        self.tree_hold.delete(*self.tree_hold.get_children())

    def update_tree_ship(self):
        self.logger.info('update_tree_ship')

        ship_designs = self.controller.ship_designs
        if ship_designs is None:
            return
        for name in ship_designs.keys():
            self.tree_ship.insert('', 'end', text=name)

    def update_tree_parts(self):
        self.logger.info('update_tree_parts')

        oid_set = self.controller.oid_set
        if oid_set is None:
            return
        for oid in sorted(oid_set):
            self.tree_parts.insert('', 'end',
                                   text=self.controller.get_oid_text(oid),
                                   values=(oid))
