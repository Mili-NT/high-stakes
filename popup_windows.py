import misc_functions
from tkinter import *
from tkinter import ttk

class access_denied_window(object):
    """
    This is the pop-up window for if the program isnt ran with proper permissions
    """
    def __init__(self, master, blackjack_widget):
        self.master = master
        self.blackjack_widget = blackjack_widget
        self.blackjack_widget.hit_button['state'] = DISABLED
        self.blackjack_widget.stand_button['state'] = DISABLED
        top=self.top=Toplevel(master)
        self.top.attributes("-topmost", True)
        self.l = ttk.Label(top,text="Hey now! This ain't being run as admin/root. You aren't trying to\n"
                                    "weasel your way out of paying up are you?")
        self.l.pack()
        self.b = ttk.Button(top, text='Close (Run Script As Admin/Root)', command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        self.top.destroy()
        self.master.destroy()
class file_entry_window(object):
    """
    This class handles the popup that takes the bets.
    A major thank you to u/charity_donut_sales on reddit for helping me get this working
    """
    def __init__(self, master, blackjack_widget):   # Added a parameter to the popup __init__
        top = self.top=Toplevel(master)
        # Make the popup appear on top:
        self.top.attributes("-topmost", True)
        # Create the entry form and button:
        self.l = Label(top,text="Enter number of files you want to bet: ")
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top,text='Proceed',command=self.cleanup)
        self.b.pack()
        self.blackjack_widget = blackjack_widget # Save the parameter as a member variable
        # Disable the hit and stand buttons so the game cant be played
        self.blackjack_widget.hit_button['state'] = DISABLED
        self.blackjack_widget.stand_button['state'] = DISABLED

    def cleanup(self):
        # when clean up is called set file_number of the blackjack_gui widget
        if int(self.e.get()) <= 0:
            exit() #TODO: Make this prompt for reentry
        self.blackjack_widget.file_number.set(self.e.get())
        self.blackjack_widget.announce(f"Files bet: {self.e.get()}") # and run announce
        # Re-enable buttons
        self.blackjack_widget.hit_button['state'] = NORMAL
        self.blackjack_widget.stand_button['state'] = NORMAL
        # Start the game
        self.blackjack_widget.deal()
        # Destroy the popup and lift the main window to top
        self.top.destroy()
        self.blackjack_widget.root.lift()
class outcome_window(object):
    """
    The outcomeWindow class creates and manages the popup window that announces the end of the game.
    It takes the root of the blackjack_gui class and the outcome as parameters
    It destroys() the root window upon closing
    """
    def __init__(self, master, blackjack_widget, outcome, fileno):
        self.master = master
        top=self.top=Toplevel(master)
        self.fileno = int(fileno.get())
        self.blackjack_widget = blackjack_widget
        self.blackjack_widget.hit_button['state'] = DISABLED
        self.blackjack_widget.stand_button['state'] = DISABLED
        if outcome == 'win':
            self.l = ttk.Label(top,text="You won! Your files live another day")
            self.b = ttk.Button(top, text='Close', command=self.cleanup)
            self.b.pack()
        elif outcome == 'tie':
            self.l = ttk.Label(top, text="You tied! Your files live another day")
            self.b = ttk.Button(top, text='Close', command=self.cleanup)
            self.b.pack()
        else:
            self.l = ttk.Label(top, text="Uh oh, you lost! You know what that means.")
            self.l.pack()
            self.defeat()
        self.l.pack()
        self.top.lift()
    def defeat(self):
        self.b = ttk.Button(self.top, text='Pay Up... [This will take about 30s]',
                            command=lambda: misc_functions.listremove(misc_functions.select_files(self.fileno)))
        self.b.pack()
    def cleanup(self):
        self.master.destroy()