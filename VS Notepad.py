from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename

root = Tk()
root.title("WilkinsEditor")

text_box = Text(root)
text_box.pack()

menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)

def save_file():
    file_path = asksaveasfilename(defaultextension=".txt")
    if not file_path:
        return
    with open(file_path, "w") as output_file:
        text = text_box.get(1.0, END)
        output_file.write(text)
    
file_menu.add_command(label="Save", command=save_file)

def open_file():
    file_path = askopenfilename()
    if not file_path:
        return
    with open(file_path, "r") as input_file:
        text = input_file.read()
        text_box.delete(1.0, END)
        text_box.insert(1.0, text)

file_menu.add_command(label="Open", command=open_file)

menu_bar.add_cascade(label="file", menu=file_menu)

root.config(menu=menu_bar)

root.mainloop()