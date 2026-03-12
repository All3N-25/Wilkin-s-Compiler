from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename

import WilkinsCompiler as CMP

root = Tk()
root.title("WilkinsEditor")
root.geometry("900x600")

file_path = None

"""
Bug List
1. Nag aadd ng new line kada open.
2. Hindi pa na totokenize maayos kapag hindi seperated by space.
"""

def save_file():
    global file_path

    if not file_path:
        file_path = asksaveasfilename(defaultextension=".txt")

    with open(file_path, "w") as output_file:
        text = text_box.get(1.0, END)
        output_file.write(text)


def open_file():
    global file_path

    file_path = askopenfilename()
    if not file_path:
        return
    with open(file_path, "r") as input_file:
        text = input_file.read()
        text_box.delete(1.0, END)
        text_box.insert(1.0, text)

def compile_code():
    save_file()

    #Read File Contents Before Tokenizer
    with open(file_path, "r") as input_file:
        text = input_file.read()

    LA = lexicalAnalysis(text)
    for i in LA:
        print(i)

def lexicalAnalysis(fileContents: str) -> dict:
    collectionOfLexemes = list(CMP.tokenizer(fileContents))
    print(collectionOfLexemes)

    collectionOfTokens = []
    for lexemes in collectionOfLexemes:
        tokens = []

        for i in lexemes:
            tokens.append(CMP.Classifier(i))

        collectionOfTokens.append(tokens)
    
    dictionaries = []

    for i, j in zip(collectionOfLexemes, collectionOfTokens):
        dictionaries.append(dict(zip(i, j)))
    
    return dictionaries
    

# Custom top bar: left side behaves like menu, right side has Compile button.
top_bar = Frame(root, bd=1, relief=RAISED)
top_bar.pack(side=TOP, fill=X)

file_menu_button = Menubutton(top_bar, text="File", underline=0, relief=FLAT)
file_menu = Menu(file_menu_button, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu_button.config(menu=file_menu)
file_menu_button.pack(side=LEFT, padx=6, pady=2)

compile_button = Button(top_bar, text="Compile", command=compile_code)
compile_button.pack(side=RIGHT, padx=8, pady=2)

text_box = Text(root)
text_box.pack(fill=BOTH, expand=True)

root.mainloop()
