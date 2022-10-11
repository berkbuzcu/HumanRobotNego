from Tkinter import *


class GUISettings(Tk):
    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        w = 350  # width for the Tk root
        h = 600  # height for the Tk root
        # get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        # set the dimensions of the screen
        # and where it is placed
        self.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.initialize()
        self.update_idletasks()

    def initialize(self):
        # Create negotiation scenarion label.
        self.set_human_sentence()
        # Configure grid column figure.
        self.grid_rowconfigure(1, weight=1)

    def set_human_sentence(self):
        self.var = StringVar()
        self.var.set("hello")
        # Negotiation domain label
        self.negotiation_label = Label(self, textvariable=self.var)
        self.negotiation_label.grid(column=1, row=1)

    def finish_settings(self):
        self.destroy()

    def update_sentence(self, msg):
        self.var.set(msg)
        self.update_idletasks()
        self.update()
