from tkinter import *
from tkinter import messagebox

def callback():
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        root.destroy()

root = Tk()
root.protocol("WM_DELETE_WINDOW", callback)

root.mainloop()
