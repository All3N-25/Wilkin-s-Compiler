from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename

import WilkinsCompiler as CMP
import os

root = Tk()
root.title("WilkinsEditor")
root.geometry("900x600")

# Bottom panel
terminal_frame = Frame(root, height=150)
terminal_frame.pack(side=BOTTOM, fill=X)

terminal = Text(terminal_frame, height=10, bg="black", fg="white")
terminal.pack(fill=BOTH, expand=True)

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
    CMP.Errors.clear()  # reset lexical errors before each compile

    if checkFileExtension(filePath):
        with open(filePath, "r") as inputFile:
            text = inputFile.read()

        tokens = list(lexicalAnalysis(text))
        for tok in tokens:
            print(tok)

        if CMP.Errors:
            print(f"Lexical Errors: {CMP.Errors}")
            return

        if not CMP.syntaxAnalysis(tokens):
            return

        CMP.semanticAnalysis(tokens)
    else:
        print("Unsupported file.")

# 3/17 - converted output from dictionary to list
def lexicalAnalysis(fileContents: str) -> list:
    collectionOfLexemes = list(CMP.tokenizer(fileContents))

    collectionOfTokens = []
    for lexemes in collectionOfLexemes:
        tokens = []

        for i in lexemes:
            tokens.append((i, CMP.Classifier(i)))  # store as list (lexeme, token)

        collectionOfTokens.extend(tokens)
    return collectionOfTokens

is_waiting_input = False
input_start_index = None
input_value = None

def terminal_print(message):
    terminal.insert(END, message + "\n")
    terminal.see(END)

def handle_enter(event):
    global is_waiting_input, input_value, input_start_index

    if not is_waiting_input:
        return "break"  # ignore Enter if not expecting input

    # Get user input from where they started typing
    end_index = terminal.index(END + "-1c")
    user_input = terminal.get(input_start_index, end_index).strip()

    input_value = user_input
    is_waiting_input = False

    terminal.insert(END, "\n")
    terminal.see(END)

    return "break"


def wait_for_input():
    global is_waiting_input, input_start_index, input_value

    is_waiting_input = True
    input_value = None

    terminal.insert(END, "> ")
    terminal.see(END)

    input_start_index = terminal.index(END)

    # Wait until user presses Enter
    while input_value is None:
        root.update()

    return input_value

def prevent_edit(event):
    if not is_waiting_input:
        return "break"

terminal.bind("<Key>", prevent_edit)

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
