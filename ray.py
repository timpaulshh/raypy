from Tkinter import *

master = Tk()

canvas = Canvas(master, width=200, height=200)
canvas.pack()

img = PhotoImage(width=200, height=200)

canvas.create_image((100, 100), image=img, state="normal")

img.put("#ffffff", (10, 10))

mainloop()
