from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename

import WilkinsCompiler as CMP
import os

root = Tk()
root.title("WilkinsEditor")
root.geometry("900x600")

filePath = None

"""
Bug List
1. Nag aadd ng new line kada open.
"""

def closeApp(event):
    print("Closing...")
    root.destroy()

def checkFileExtension(filePath, allowedExtension=".wil"):
    ext = os.path.splitext(filePath)[1].lower()

    if ext in allowedExtension:
        return True
    else:
        return False

def saveFile():
    global filePath

    if not filePath:
        filePath = asksaveasfilename(defaultextension=".wil")

    with open(filePath, "w") as outputFile:
        text = text_box.get(1.0, END)
        outputFile.write(text)

def openFile():
    global filePath

    filePath = askopenfilename()

    if not filePath:
        return
    with open(filePath, "r") as inputFile:
        text = inputFile.read()
        text_box.delete(1.0, END)
        text_box.insert(1.0, text)

def compileCode():
    saveFile()

    #Read File Contents Before Tokenizer
    if (checkFileExtension(filePath)):
        with open(filePath, "r") as inputFile:
            text = inputFile.read()

        LA = lexicalAnalysis(text)
        for i in LA:
            print(i)
    else:
        print("Unsupported file.")

def lexicalAnalysis(fileContents: str) -> dict:
    collectionOfLexemes = list(CMP.tokenizer(fileContents))

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
file_menu.add_command(label="Open", command=openFile)
file_menu.add_command(label="Save", command=saveFile)
file_menu_button.config(menu=file_menu)
file_menu_button.pack(side=LEFT, padx=6, pady=2)

compile_button = Button(top_bar, text="Compile", command=compileCode)
compile_button.pack(side=RIGHT, padx=8, pady=2)

text_box = Text(root)
text_box.pack(fill=BOTH, expand=True)

root.bind('<Escape>', closeApp)

# Focus the root window to ensure it captures key presses
root.focus_set()


root.mainloop()
