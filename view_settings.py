import logging
from tkinter import *
from localization import L10N
from seria_controller import *
from view import FrameView
from view_utility import *


class SettingsFrameView(FrameView):
    def __init__(self, mainview, controller: SeriaController):
        super().__init__(mainview, controller)
        self.logger = logging.getLogger("settings")

        self.frame = Frame(self.frm_container)
        self.frame.pack(fill=BOTH, expand=True)
        self.frame.columnconfigure(1, weight=1)

        self.var_gamepath = StringVar(value=self.controller.get_gamepath())
        self.var_gamepath.trace_add('write', self._on_gamepath_change)

        grid_btn(self.frame, L10N().text('BACK'),
                 lambda: self.mainview.var_viewmode.set(VIEWMODE_BASIC))
        grid_lbl_ent(self.frame, L10N().text(
            'GAME_PATH'), variable=self.var_gamepath)
        Button(self.frame, text=L10N().text('BROWSE'),
               command=self._set_gamepath).grid(row=1, column=2)

    def _on_gamepath_change(self, *args):
        self.logger.info(f'_on_gamepath_change: {args}')

        self.controller.set_gamepath(self.var_gamepath.get())
        self.mainview._set_menu_file_state()
        self.mainview._update_basicview_static()

    def _set_gamepath(self):
        self.logger.info('_set_gamepath')

        dirpath = ask_directory(L10N().text('GAME_PATH'))
        if dirpath == '' or isinstance(dirpath, tuple):
            return
        self.var_gamepath.set(dirpath)
