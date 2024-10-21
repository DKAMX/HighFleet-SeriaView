import json
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext, ttk
import seria

__author__ = 'Max'
__version__ = '0.2.1'

_TIP_FILE = 'Open a file to view details'
_TIP_NODE = 'Click on an item to view details'
_CFG_PATH = 'config.json'
_CFG_SET = ('gamepath', 'oid_text')


class SeriaController:
    def __init__(self):
        self.root = Tk()
        self.root.title(f'SeriaView v{__version__}')
        self.root.geometry('640x480')
        self.root.minsize(640, 480)

        self.config: dict = dict()

        # Data model
        self.var_viewmode = IntVar(value=0)
        self.seria: seria.SeriaNode = None
        # reference to seria node, easy to modify
        self.var_bonus: str = StringVar()
        self.var_cash: str = StringVar()
        self.squadron_nodes = list()
        self.squadron_hold_nodes = list()
        self.ammo_nodes = list()

        # Base view
        self.entry_cash: Entry = None
        self.entry_bonus: Entry = None
        self.frm_baseview: Frame = None
        self.tree_squadron: ttk.Treeview = None
        self.tree_hold: ttk.Treeview = None
        self.tree_ammo: ttk.Treeview = None

        # TODO Map view
        # self.frm_map: Frame = None

        # Tree view
        self.frm_treeview: Frame = None
        self.tree_seria: ttk.Treeview = None
        self.text_treeview_detail: scrolledtext.ScrolledText = None

        self._make_menu()
        self._make_baseview()
        self._make_treeview()
        # TODO make map view
        self._on_view_change()

        self.root.after(0, self._load_config)
        self.root.mainloop()

    def _load_config(self):
        try:
            file = open(_CFG_PATH, 'r')

            config = json.load(file)
            if tuple(config.keys()) != _CFG_SET:
                messagebox.showerror(
                    'Config', 'Invalid config file, please delete it')
                return

            self.config = config
        except FileNotFoundError:
            gamepath = filedialog.askdirectory(
                title='Select HighFleet game folder')

            if gamepath == '' or isinstance(gamepath, tuple):
                messagebox.showwarning('Config', 'Game folder not selected')
                return

            self.config['gamepath'] = gamepath

            oid_text = load_text(gamepath)
            if oid_text is None:
                messagebox.showerror(
                    'Config', 'Failed to load dialog file')
                return

            self.config['oid_text'] = oid_text

            json.dump(self.config, open(_CFG_PATH, 'w'))

    def _make_menu(self):
        def show_about():
            messagebox.showinfo(
                'About', f'''SeriaView v{__version__}
Developed by {__author__}
More information at: https://github.com/DKAMX/HighFleet-SeriaView''')

        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        menu_file = Menu(menubar, tearoff=False)
        menu_file.add_command(label='Open', command=self.open_file)
        menu_file.add_command(label='Save', command=self.save_file)
        menu_file.add_command(label='Close', command=self.close_file)
        menubar.add_cascade(label='File', menu=menu_file)

        menu_view = Menu(menubar, tearoff=False)
        menu_view.add_radiobutton(label='Base view', command=self._on_view_change,
                                  value=0, variable=self.var_viewmode)
        # menu_view.add_radiobutton(label='Map view', command=self._on_view_change,
        #                           value=1, variable=self.view_mode)
        menu_view.add_radiobutton(label='Tree view', command=self._on_view_change,
                                  value=2, variable=self.var_viewmode)
        menubar.add_cascade(label='View', menu=menu_view)

        menubar.add_command(label='About', command=show_about)

    def _on_view_change(self):
        if self.var_viewmode.get() == 0:
            self.frm_baseview.pack(expand=True, fill=BOTH)
            # self.frm_map.pack_forget()
            self.frm_treeview.pack_forget()
        elif self.var_viewmode.get() == 1:
            pass
            # TODO
            # self.frm_base.pack_forget()
            # self.frm_map.pack(expand=True, fill=BOTH)
            # self.frm_tree.pack_forget()
        elif self.var_viewmode.get() == 2:
            self.frm_baseview.pack_forget()
            # self.frm_map.pack_forget()
            self.frm_treeview.pack(expand=True, fill=BOTH)

    def _make_baseview(self):
        self.frm_baseview = Frame(self.root)
        self.frm_baseview.columnconfigure(0, weight=1)
        self.frm_baseview.columnconfigure(1, weight=1)
        self.frm_baseview.rowconfigure(1, weight=1)
        self.frm_baseview.rowconfigure(2, weight=1)

        # basic information panel
        frm_info = Frame(self.frm_baseview)
        frm_info.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        label_bonus = Label(frm_info, text='Bonus')
        label_bonus.pack(side=LEFT)
        self.entry_bonus = Entry(
            frm_info, textvariable=self.var_bonus, width=10)
        self.entry_bonus.config(state=DISABLED)
        self.entry_bonus.pack(side=LEFT)

        label_cash = Label(frm_info, text='Cash')
        label_cash.pack(side=LEFT)
        self.entry_cash = Entry(frm_info, textvariable=self.var_cash, width=10)
        self.entry_cash.config(state=DISABLED)
        self.entry_cash.pack(side=LEFT)

        self.var_bonus.trace('w', self._on_bonus_change)
        self.var_cash.trace('w', self._on_cash_change)

        # player's squadron panel
        frm_squadron = LabelFrame(self.frm_baseview, text='Squadron')
        frm_squadron.grid(row=1, column=0, sticky=NSEW)
        frm_squadron.propagate(False)

        self.tree_squadron = ttk.Treeview(frm_squadron, selectmode=BROWSE,
                                          show='tree')
        self.tree_squadron.pack(expand=True, fill=BOTH, side=LEFT)

        sb_squadron = ttk.Scrollbar(frm_squadron, orient='vertical',
                                    command=self.tree_squadron.yview)
        sb_squadron.pack(fill=Y, side=RIGHT)
        self.tree_squadron.config(yscrollcommand=sb_squadron.set)

        #  ship hold panel
        frm_hold = LabelFrame(self.frm_baseview, text='Ship Hold')
        frm_hold.grid(row=1, column=1, sticky=NSEW)
        frm_hold.propagate(False)

        self.tree_hold = ttk.Treeview(frm_hold, columns=['type', 'count'],
                                      selectmode=BROWSE)
        self.tree_hold.heading('#0', text='')
        self.tree_hold.heading('type', anchor=CENTER, text='NAME')
        self.tree_hold.heading('count', anchor=CENTER, text='AMT')
        self.tree_hold.column('#0', width=20, stretch=False)
        self.tree_hold.column('type', width=200)
        self.tree_hold.column('count', anchor=CENTER, width=50)
        self.tree_hold.pack(expand=True, fill=BOTH, side=LEFT)

        sb_parts = ttk.Scrollbar(frm_hold, orient='vertical',
                                 command=self.tree_hold.yview)
        sb_parts.pack(fill=Y, side=RIGHT)
        self.tree_hold.config(yscrollcommand=sb_parts.set)

        self.tree_hold.bind('<<TreeviewSelect>>', self._on_tree_hold_select)

        # special ammunition register panel
        frm_ammo = LabelFrame(self.frm_baseview, text='Ammunition')
        frm_ammo.grid(row=2, column=0, sticky=NSEW)
        frm_ammo.propagate(False)

        self.tree_ammo = ttk.Treeview(frm_ammo, columns=['type', 'count'],
                                      selectmode=BROWSE)
        self.tree_ammo.heading('#0', text='')
        self.tree_ammo.heading('type', anchor=CENTER, text='TYPE')
        self.tree_ammo.heading('count', anchor=CENTER, text='PCS')
        self.tree_ammo.column('#0', width=0, stretch=False)
        self.tree_ammo.column('type', width=200)
        self.tree_ammo.column('count', anchor=CENTER, width=50)
        self.tree_ammo.pack(expand=True, fill=BOTH, side=LEFT)

        sb_ammo = ttk.Scrollbar(frm_ammo, orient='vertical',
                                command=self.tree_ammo.yview)
        sb_ammo.pack(fill=Y, side=RIGHT)
        self.tree_ammo.config(yscrollcommand=sb_ammo.set)

        self.tree_ammo.bind('<<TreeviewSelect>>', self._on_tree_ammo_select)

        # control panel
        frm_control = LabelFrame(self.frm_baseview, text='Control')
        frm_control.grid(row=2, column=1, sticky=NSEW)
        frm_control.propagate(False)

        self.frm_hold_control = Frame(frm_control)
        btn_hold_add_100 = Button(self.frm_hold_control, text='+ 10',
                                  command=self._add_part_10)
        btn_hold_add_500 = Button(self.frm_hold_control, text='+ 50',
                                  command=self._add_part_50)
        btn_hold_add_100.pack(side=LEFT)
        btn_hold_add_500.pack(side=LEFT)

        self.frm_ammo_control = Frame(frm_control)
        btn_ammo_add_100 = Button(self.frm_ammo_control, text='+ 100',
                                  command=self._add_ammo_100)
        btn_ammo_add_500 = Button(self.frm_ammo_control, text='+ 500',
                                  command=self._add_ammo_500)
        btn_ammo_add_100.pack(side=LEFT)
        btn_ammo_add_500.pack(side=LEFT)

    def _update_baseview(self):
        self.entry_bonus.config(state=NORMAL)
        self.entry_cash.config(state=NORMAL)

        self._update_tree_squadron()
        self._update_tree_hold()
        self._update_tree_ammo()

    def _update_tree_squadron(self):
        self.tree_squadron.delete(*self.tree_squadron.get_children())

        for squadron in self.squadron_nodes:
            name = squadron.get_attribute('m_name')

            # squadron treeview
            squadron_iid = self.tree_squadron.insert('', 'end', text=name)
            for ship in squadron.filter_nodes(lambda n: n.header == 'm_children=7'):
                self.tree_squadron.insert(squadron_iid, 'end',
                                          text=self.get_ship_name(ship))

        # expand tree root by default
        for child in self.tree_squadron.get_children():
            self.tree_squadron.item(child, open=True)

    def _update_tree_hold(self):
        self.tree_hold.delete(*self.tree_hold.get_children())

        squadron_node_index = 0
        for squadron in self.squadron_nodes:
            name = squadron.get_attribute('m_name')

            # ship hold treeview
            hold_iid = self.tree_hold.insert('', 'end', values=(name, ''))

            for item in self.squadron_hold_nodes[squadron_node_index].get_nodes():
                oid = item.get_attribute('m_oid')
                count = item.get_attribute('m_count') or 1
                self.tree_hold.insert(hold_iid, 'end',
                                      values=(self.get_item_name(oid), count))

            squadron_node_index += 1

        # expand tree root by default
        for child in self.tree_hold.get_children():
            self.tree_hold.item(child, open=True)

    def _update_tree_ammo(self):
        self.tree_ammo.delete(*self.tree_ammo.get_children())

        for node_index, ammo in enumerate(self.ammo_nodes):
            index = ammo.get_attribute('m_index')
            ammo_type = self.get_ammo_type(index)
            if ammo_type:
                count = ammo.get_attribute('m_count') or 1
                self.tree_ammo.insert('', 'end',
                                      iid=node_index, values=(ammo_type, count))

    def _add_part_amount(self, amount: int):
        iid = self.tree_hold.focus()
        parent_iid = self.tree_hold.parent(iid)

        if parent_iid == '':
            return

        index = self.tree_hold.index(iid)
        parent_index = self.tree_hold.index(parent_iid)
        item = self.squadron_hold_nodes[parent_index].get_node(index)

        item_count = item.get_attribute('m_count')
        new_count = (int(item_count) if item_count else 1) + amount
        item.set_attribute('m_count', str(new_count))

        self._update_tree_hold()

    def _add_part_10(self):
        self._add_part_amount(10)

    def _add_part_50(self):
        self._add_part_amount(50)

    def _add_ammo_amount(self, amount: int):
        index = self.tree_ammo.focus()

        if not index:
            return

        ammo = self.ammo_nodes[int(index)]
        ammo_count = ammo.get_attribute('m_count')
        new_count = (int(ammo_count) if ammo_count else 1) + amount
        ammo.set_attribute('m_count', str(new_count))

        self._update_tree_ammo()

    def _add_ammo_100(self):
        self._add_ammo_amount(100)

    def _add_ammo_500(self):
        self._add_ammo_amount(500)

    def _make_treeview(self):
        self.frm_treeview = Frame(self.root)
        self.frm_treeview.columnconfigure(0, weight=1)
        self.frm_treeview.columnconfigure(1, weight=1)
        self.frm_treeview.rowconfigure(0, weight=1)

        # seria tree panel
        frm_tree = Frame(self.frm_treeview)
        frm_tree.grid(row=0, column=0, sticky=NSEW)
        frm_tree.propagate(False)

        self.tree_seria = ttk.Treeview(frm_tree, selectmode=BROWSE,
                                       show='tree')
        self.tree_seria.pack(expand=True, fill=BOTH, side=LEFT)

        sb_tree = ttk.Scrollbar(frm_tree, orient='vertical',
                                command=self.tree_seria.yview)
        sb_tree.pack(fill=Y, side=RIGHT)
        self.tree_seria.config(yscrollcommand=sb_tree.set)

        # seria node detail panel
        frm_detail = Frame(self.frm_treeview)
        frm_detail.grid(row=0, column=1, sticky=NSEW)
        frm_detail.propagate(False)

        self.text_treeview_detail = scrolledtext.ScrolledText(
            frm_detail, width=40)
        self.text_treeview_detail.insert('end', _TIP_FILE)
        self.text_treeview_detail.config(state=DISABLED)
        self.text_treeview_detail.pack(expand=True, fill=BOTH)

        self.tree_seria.bind('<<TreeviewSelect>>', self._on_tree_seria_select)

    def _update_treeview(self):
        def get_node_summary(node: seria.SeriaNode):
            classname = node.get_attribute('m_classname')
            name = node.get_attribute('m_name')
            codename = node.get_attribute('m_codename')
            fullname = node.get_attribute('m_fullname')

            if classname == 'Escadra':
                return f'Squadron {name}'
            if classname == 'Location':
                return f'City {name} ({codename})'
            if classname == 'NPC':
                return f'{classname} {fullname}' if str.isalpha(name) and fullname else classname
            if classname == 'Node':
                ship_name = self.get_ship_name(node)
                return classname if ship_name is None else f'{classname} {ship_name}'
            if classname == 'Body':
                return f'{classname} {name}' if name else classname
            return classname

        def append_children(node: seria.SeriaNode, parent_id: str):
            node_id = self.tree_seria.insert(
                parent_id, 'end', text=get_node_summary(node))
            for child in node.get_nodes():
                append_children(child, node_id)

        self.tree_seria.delete(*self.tree_seria.get_children())

        # populate tree with seria nodes
        root_id = self.tree_seria.insert(
            '', 'end', text=get_node_summary(self.seria))

        for node in self.seria.get_nodes():
            append_children(node, root_id)

        self.tree_seria.item(root_id, open=True)

        self.text_treeview_detail.config(state=NORMAL)
        self.text_treeview_detail.delete(1.0, END)
        self.text_treeview_detail.insert(
            'end', _TIP_NODE)
        self.text_treeview_detail.config(state=DISABLED)

    def _on_bonus_change(self, *args):
        try:
            bonus = int(self.var_bonus.get())
            if bonus <= 0:
                raise ValueError
            self.seria.set_attribute('m_scores', str(bonus))
        except ValueError:
            self.var_bonus.set(self.seria.get_attribute('m_scores'))

    def _on_cash_change(self, *args):
        try:
            cash = int(self.var_cash.get())
            if cash < 0:
                raise ValueError
            self.seria.set_attribute('m_cash', str(cash))
        except ValueError:
            self.var_cash.set(self.seria.get_attribute('m_cash'))

    def _on_tree_squadron_select(self, event):
        pass

    def _on_tree_hold_select(self, event):
        self.frm_ammo_control.pack_forget()
        self.frm_hold_control.pack(expand=True, fill=BOTH)

    def _on_tree_ammo_select(self, event):
        self.frm_hold_control.pack_forget()
        self.frm_ammo_control.pack(expand=True, fill=BOTH)

    def _on_tree_seria_select(self, event):
        def print_key_value(k, v):
            return f'{k}: {v}\n' if not k.startswith('_') else f'{v}\n'

        def print_node_attributes(node: seria.SeriaNode):
            self.text_treeview_detail.config(state=NORMAL)
            self.text_treeview_detail.delete(1.0, END)
            for key, value in node.get_attributes().items():
                if isinstance(value, list):
                    for v in value:
                        self.text_treeview_detail.insert(
                            'end', print_key_value(key, v))
                else:
                    self.text_treeview_detail.insert(
                        'end', print_key_value(key, value))
            self.text_treeview_detail.config(state=DISABLED)

        iid = event.widget.focus()
        parent_iid = self.tree_seria.parent(iid)

        if parent_iid == '':
            print_node_attributes(self.seria)
            return

        # node index sequence (from root to selected node)
        index_sequence = []
        while parent_iid != '':
            index_sequence.insert(0, self.tree_seria.index(iid))
            iid = parent_iid
            parent_iid = self.tree_seria.parent(iid)

        node = self.seria
        for index in index_sequence:
            node = node.get_node(index)

        print_node_attributes(node)

    def get_ship_name(self, node: seria.SeriaNode):
        try:
            frame = node.get_node_by_class('Frame')
            body = frame.get_node_if(
                lambda n: n.get_attribute('m_name') == 'COMBRIDGE')
            creature = body.get_node_by_class('Creature')
            return creature.get_attribute('m_ship_name')
        except:
            return None

    def get_item_name(self, oid: str):
        if self.config is None:
            return oid
        desc = self.config["oid_text"].get(f"{oid}_SDESC", "")
        return f'{self.config["oid_text"].get(oid, oid)} {desc if desc == "" else f"({desc})"}'

    def get_ammo_type(self, index: str):
        ammo_types = {
            '8': '122mm Unguided rocket',
            '13': '340mm Unguided rocket',
            '14': '37mm Incendiary',
            '15': '57mm Incendiary',
            '16': '100mm Armor piercing',
            '17': '100mm Proximity fuze',
            '18': '100mm Incendiary',
            '19': '130mm Armor piercing',
            '20': '130mm Proximity fuze',
            '21': '130mm Incendiary',
            '22': '130mm Laser guided',
            '23': '180mm Armor piercing',
            '24': '180mm Proximity fuze',
            '25': '180mm Incendiary',
            '26': '180mm Laser guided',
            '27': '220mm Incendiary',
            '28': '300mm Incendiary',
            '30': '100 kg General purpose bomb',
            '31': '250 kg General purpose bomb',
            '35': 'Air-to-air missile'
        }

        return ammo_types.get(index, None)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Seria files', '*.seria')])

        if file_path:
            self.seria = seria.load(file_path)

            self.var_bonus.set(self.seria.get_attribute('m_scores'))
            self.var_cash.set(self.seria.get_attribute('m_cash'))

            self.ammo_nodes = self.seria.get_nodes_by_class('Item')
            self.squadron_nodes = self.seria.filter_nodes(
                lambda n: n.header == 'm_escadras=327' and n.get_attribute('m_name') in {'MARK', 'DETACHMENT'})
            for squadron in self.squadron_nodes:
                self.squadron_hold_nodes.append(
                    squadron.get_node_if(lambda n: n.header == 'm_inventory=7'))

            self._update_baseview()
            self._update_treeview()

            self.root.title(f'SeriaView v{__version__} - {file_path}')

    def save_file(self):
        if self.seria is None:
            return

        filepath = filedialog.asksaveasfilename(
            filetypes=[('Seria files', '*.seria')])

        if filepath:
            seria.dump(self.seria, filepath)
            messagebox.showinfo('Save', f'File saved to: {filepath}')

    def close_file(self):
        if self.seria is None:
            return
        self.seria = None

        # clear base view
        self.entry_bonus.config(state=DISABLED)
        self.entry_cash.config(state=DISABLED)
        self.tree_squadron.delete(*self.tree_squadron.get_children())
        self.tree_hold.delete(*self.tree_hold.get_children())
        self.tree_ammo.delete(*self.tree_ammo.get_children())

        # clear tree view
        self.tree_seria.delete(*self.tree_seria.get_children())
        self.text_treeview_detail.config(state=NORMAL)
        self.text_treeview_detail.delete(1.0, END)
        self.text_treeview_detail.insert('end', _TIP_FILE)
        self.text_treeview_detail.config(state=DISABLED)

        self.root.title(f'SeriaView v{__version__}')


def load_text(gamepath):
    '''Load in-game text from resource file, return as a dictionary
    @return: key(oid), value(text)'''

    lines = dec_seria(gamepath)

    if lines is None:
        return None

    text_map = dict()
    for line in lines:
        if line.startswith('#ITEM') or line.startswith('#CRAFT') or line.startswith('#MDL'):
            key, value = line.split('\t', 1)
            text_map[key[1:]] = value
    return text_map


def dec_seria(filepath):
    try:
        dialog_path = filepath + '/Data/Dialogs/english.seria_enc'
        file = open(dialog_path, 'rb')
        data = list(file.read())
        a = 0
        b = 2531011
        while a < len(data):
            data[a] = (b ^ (b >> 15) ^ data[a]) & 0xff
            b += 214013
            b &= 0xffffffff
            a += 1
        return bytes(data).decode('cp1251').split('\n')
    except:
        print(f'Error: cannot open file {dialog_path}')
        return None


if __name__ == '__main__':
    SeriaController()
