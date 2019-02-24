from tkinter import *
import threading
from time import sleep

class Window:
    def __init__(self):
        self.flg = False
        self.root = Tk()
        self.txt = StringVar()
        Button(self.root, text="test", command=self.changeLabel ).pack()
        self.txt.set("hoge")
        Label(self.root, textvariable=self.txt).pack()

    def changeLabel(self):
        self.txt.set("Start...")
        t = threading.Thread(target=FunctionThatTakeALotOfTime, args=(self,))
        t.start()

def FunctionThatTakeALotOfTime(w):
    sleep(2)
    w.txt.set("Finished!")

if __name__ == '__main__':
    w = Window()
    w.root.mainloop()