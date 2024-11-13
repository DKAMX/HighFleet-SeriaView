from tkinter import *
from seria_controller import SeriaController


class FrameView:
    def __init__(self, mainview, controller: SeriaController):
        self.mainview = mainview
        self.controller: SeriaController = controller
        self.frm_container = Frame(mainview.root)

    def show(self):
        self.frm_container.pack(fill=BOTH, expand=True)

    def hide(self):
        self.frm_container.pack_forget()

    def enable(self):
        '''Enable sub widgets such as buttons, entries, etc for interaction.
        Override this method in child classes.'''
        pass

    def disable(self):
        '''Disable sub widgets such as buttons, entries, etc for interaction.
        Override this method in child classes.'''
        pass

    def update(self):
        '''Update view with data from controller.
        Override this method in child classes.'''
        pass

    def clear(self):
        '''Clear view data.
        Override this method in child classes.'''
        pass
