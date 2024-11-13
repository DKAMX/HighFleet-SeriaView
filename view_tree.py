import logging
from tkinter import *
from tkinter import scrolledtext, ttk
from localization import L10N
from seria_model import *
from seria_controller import *
from view import FrameView
from view_utility import *


class TreeFrameView(FrameView):
    def __init__(self, mainview, controller: SeriaController):
        super().__init__(mainview, controller)
        self.logger = logging.getLogger('TreeFrameView')

        self.tree_seria: ttk.Treeview = None
        self.text_detail: scrolledtext.ScrolledText = None

        self._make_treeview()

    def update(self):
        def append_children(node: SeriaNode, parent_id: str):
            node_id = self.tree_seria.insert(
                parent_id, 'end', text=self.controller.get_node_text(node))
            for child in node.get_nodes():
                append_children(child, node_id)

        self.clear()

        # populate tree with seria nodes
        root_node = self.controller.seria_node
        root_id = self.tree_seria.insert(
            '', 'end', text=self.controller.get_node_text(root_node))
        for node in root_node.get_nodes():
            append_children(node, root_id)

        self.tree_seria.item(root_id, open=True)

        self._update_text_detail(L10N().text('TIP_TREE_DETAIL_NODE'))

    def clear(self):
        self.tree_seria.delete(*self.tree_seria.get_children())
        self._update_text_detail(L10N().text('TIP_TREE_DETAIL_FILE'))

    def _make_treeview(self):
        self.logger.info('_make_treeview')

        frame = Frame(self.frm_container)
        frame.pack(fill=BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        # seria tree panel (left)
        frm_tree = Frame(frame)
        frm_tree.grid(row=0, column=0, sticky=NSEW)
        frm_tree.propagate(False)

        self.tree_seria = ttk.Treeview(
            frm_tree, selectmode=BROWSE, show='tree')
        self.tree_seria.pack(expand=True, fill=BOTH, side=LEFT)

        sb_tree = ttk.Scrollbar(frm_tree, orient='vertical',
                                command=self.tree_seria.yview)
        sb_tree.pack(fill=Y, side=RIGHT)
        self.tree_seria.config(yscrollcommand=sb_tree.set)

        # seria attributes panel (right)
        frm_detail = Frame(frame)
        frm_detail.grid(row=0, column=1, sticky=NSEW)
        frm_detail.propagate(False)

        self.text_detail = scrolledtext.ScrolledText(frm_detail, width=40)
        self.text_detail.pack(expand=True, fill=BOTH)
        self._update_text_detail(L10N().text('TIP_TREE_DETAIL_FILE'))

        self.tree_seria.bind('<<TreeviewSelect>>', self._on_tree_select)

    def _on_tree_select(self, event):
        self.logger.info(f'_on_tree_select: {event}')

        # get parent id of selected node
        iid = event.widget.focus()
        parent_iid = self.tree_seria.parent(iid)

        node = self.controller.seria_node

        # fix for _on_tree_select triggered after clear
        if node is None:
            return

        # if selected node is root
        if parent_iid == '':
            self._update_text_detail(get_node_attr_text(node))
            return

        # node index sequence (from root to selected node)
        index_sequence = []
        while parent_iid != '':
            index_sequence.insert(0, self.tree_seria.index(iid))
            iid = parent_iid
            parent_iid = self.tree_seria.parent(iid)

        for index in index_sequence:
            node = node.get_node(index)

        self._update_text_detail(get_node_attr_text(node))

    def _update_text_detail(self, text: str):
        self.text_detail.config(state=NORMAL)
        self.text_detail.delete(1.0, END)
        self.text_detail.insert('end', text)
        self.text_detail.config(state=DISABLED)
