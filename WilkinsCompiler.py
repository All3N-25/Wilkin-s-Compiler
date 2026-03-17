import re

keywords = ["var", "input", "output"]
arithmeticOperator = ['+', '-', '*', '/', '^']
assignmentOperator = ['=']
Errors = []

"""
Lexical Analyzer Phase
- Gets the lexemes from the file
- Identifies the property of the lexemes
"""

# Returns a list of list
def tokenizer(x: str) -> list:
    collections = []
    lexemes = []
    word = ""

    for char in x:
        #White Space
        if char == " ":
            if word:
                lexemes.append(word)
                word = ""
            #lexemes.append('_')    #D naman na ata need to

        #Operators and Delimiter
        elif char == ";":
            if word:
                lexemes.append(word)
                word = ""
            lexemes.append(char)
            collections.append(lexemes.copy())

            lexemes.clear()

        elif char == "(":
            if word:
                lexemes.append(word)
                word = ""
            lexemes.append(char)

        elif char == ")":
            if word:
                lexemes.append(word)
                word = ""
            lexemes.append(char)

        elif char in arithmeticOperator or char in assignmentOperator:
            if word:
                lexemes.append(word)
                word = ""
            lexemes.append(char)
        
        #Whitespace
        elif char == "\n":
            continue

        else:
            word += char

    if word:
        lexemes.append(word)
    
    if lexemes:
        collections.append(lexemes.copy())

    return collections

def Classifier(lexemes: str) -> str:
    global dataType
    
    #DataType
    if lexemes in keywords:
        dataType = lexemes
        return "KEYWORD"

    #Syntax
    if re.fullmatch(r"(var|input|output)\d+", lexemes):
        Errors.append(lexemes)
        return "SYNTAX_ERROR"

    #Identifier/Variable Name
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,29}", lexemes):
        return "IDENTIFIER"

    #Numeric Literal
    if re.fullmatch(r"[0-9]+", lexemes):
        return "NUMBER"

    #Arithmetic and Assignment Operator
    if lexemes == '+':
        return "PLUS"
    if lexemes == '-':
        return "MINUS"
    if lexemes == '*':
        return "MULT"
    if lexemes == '/':
        return "DIV"
    if lexemes == "^":
        return "POW"
    if lexemes == '=':
        return "ASSIGN"

    #Delimiters
    if lexemes == ';':
        return "SEMICOLON"
    if lexemes == '(':
        return "LPAREN"
    if lexemes == ')':
        return "RPAREN"

    #Default
    Errors.append(lexemes)
    return "Error"