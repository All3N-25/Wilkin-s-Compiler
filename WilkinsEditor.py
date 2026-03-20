from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename

import WilkinsCompiler as CMP
import os
import subprocess
import sys
import tempfile

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

        if not CMP.semanticAnalysis(tokens):
            return

        python_code = CMP.codeGeneration(tokens)
        
        # FOR DEBUGGING - print the generated Python code before execution
        print("\n--- Generated Python Code ---")
        print(python_code)
        print("-----------------------------\n")

        runInNewTerminal(python_code)
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
    
def runInNewTerminal(python_code: str):
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_gen.py")
    
    with open(output_path, "w") as f:
        f.write(python_code)

    # Windows
    if sys.platform == "win32": 
        subprocess.Popen(
            f'start cmd /k python "{output_path}"',
            shell=True
        )

    # macOS
    elif sys.platform == "darwin":
        script = f'tell app "Terminal" to do script "python3 \\"{output_path}\\"; echo; echo \\"--- Program finished ---\\"; read"'
        subprocess.Popen(["osascript", "-e", script])

    # Linux
    else:
        subprocess.Popen([
            "x-terminal-emulator", "-e",
            f'bash -c "python3 \\"{output_path}\\"; echo; echo \\"--- Program finished ---\\"; read"'
        ])

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
