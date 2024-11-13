import logging
from tkinter import *
from localization import L10N
from seria_controller import *
from view import FrameView
from view_settings import SettingsFrameView
from view_basic import BasicFrameView
from view_tree import TreeFrameView
from view_utility import *

__author__ = 'Max'
__version__ = '0.3.0'

logging.basicConfig(level=logging.INFO)


class SeriaView:
    def __init__(self, controller: SeriaController):
        self.logger = logging.getLogger('SeriaView')

        self.controller: SeriaController = controller

        self.root = Tk()
        self.root.title(f'SeriaView v{__version__}')
        self.root.geometry('720x480')
        self.root.minsize(720, 480)

        # UI components
        self.menu_file: Menu = None
        self.frameview_list = list()  # list of FrameView

        # Variables
        self.var_viewmode = IntVar(value=VIEWMODE_BASIC)
        self.var_viewmode.trace_add('write', self._on_viewmode_change)

        self._make_menu()
        self.frameview_list.append(SettingsFrameView(self, self.controller))
        self.frameview_list.append(BasicFrameView(self, self.controller))
        self.frameview_list.append(FrameView(self, self.controller))
        self.frameview_list.append(TreeFrameView(self, self.controller))

        if self.controller.get_gamepath() == '':
            self.var_viewmode.set(VIEWMODE_SETTINGS)
        self._on_viewmode_change()  # set the initial view
        self._set_menu_file_state()
        self._update_basicview_static()

        mainloop()

    def _make_menu(self):
        self.logger.info('_make_menu')

        menu = Menu(self.root)
        self.root.config(menu=menu)

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
            'SETTINGS'), command=lambda: self.var_viewmode.set(VIEWMODE_SETTINGS))
        menu.add_cascade(label=L10N().text('FILE'),
                         menu=self.menu_file)

        menu_view = Menu(menu, tearoff=False)
        menu_view.add_radiobutton(label=L10N().text(
            'VIEW_BASIC'), value=VIEWMODE_BASIC, variable=self.var_viewmode)
        # menu_view.add_radiobutton(label=L10N().text(
        #     'VIEW_MAP'), value=VIEWMODE_MAP, variable=self.var_viewmode)
        menu_view.add_radiobutton(label=L10N().text(
            'VIEW_TREE'), value=VIEWMODE_TREE, variable=self.var_viewmode)
        menu.add_cascade(label=L10N().text('VIEW'), menu=menu_view)

        menu.add_command(label=L10N().text('ABOUT'), command=self._about)

    def _on_viewmode_change(self, *args):
        self.logger.info(f'_on_viewmode_change: {args}')

        for view in self.frameview_list:
            view.hide()
        self.frameview_list[self.var_viewmode.get()].show()

    def _set_menu_file_state(self):
        self.logger.info('_set_menu_file_state')

        if self.controller.text is None:
            self.menu_file.entryconfig(1, state=DISABLED)
        else:
            self.menu_file.entryconfig(1, state=NORMAL)

    def _update_basicview_static(self):
        self.logger.info('_update_basicview_static')

        self.frameview_list[VIEWMODE_BASIC].update_tree_ship()
        self.frameview_list[VIEWMODE_BASIC].update_tree_parts()

    def _open_file(self):
        self.logger.info('_open_file')

        filepath = ask_openfilename('')
        if filepath == '' or isinstance(filepath, tuple):
            return

        is_success = self.controller.load_seria(filepath)
        if not is_success:
            return

        self.root.title(f'{filepath} - SeriaView v{__version__}')

        self._update_view()
        if self.controller.is_profile():
            self.var_viewmode.set(VIEWMODE_BASIC)
        else:
            self.var_viewmode.set(VIEWMODE_TREE)

    def _open_profile(self, index):
        self.logger.info(f'_open_profile: {index}')

        filepath = self.controller.load_profile(index)
        if filepath is None:
            return

        self.root.title(f'{filepath} - SeriaView v{__version__}')

        self._update_view()
        self.var_viewmode.set(VIEWMODE_BASIC)

    def _save_file(self):
        self.logger.info('_save_file')

        if self.controller.seria_node is None:
            return

        path = ask_savefilename('')
        if path == '' or isinstance(path, tuple):
            return

        self.controller.save_seria(path)

    def _close_file(self):
        self.logger.info('_close_file')

        self.controller.seria_node = None
        self.controller.profile_model.clear()
        self.root.title(f'SeriaView v{__version__}')

        self._clear_view()

    def _about(self):
        self.logger.info('_about')

        show_message('About', f'''SeriaView v{__version__}
Developed by {__author__}
More information at: https://github.com/DKAMX/HighFleet-SeriaView''')

    def _update_view(self):
        for view in self.frameview_list:
            view.enable()
            view.update()

    def _clear_view(self):
        for view in self.frameview_list:
            view.disable()
            view.clear()


if __name__ == '__main__':
    SeriaView(SeriaController())
