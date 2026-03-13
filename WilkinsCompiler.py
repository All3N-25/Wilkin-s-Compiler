import re

keywords = ["var", "input", "output"]
arithmeticOperator = ['+', '-', '*', '/']
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

    # D naman ata nito need
    # if lexemes == "_":
    #     return "White Space"

    #DataType
    if lexemes in keywords:
        dataType = lexemes
        return "Keyword"

    #Syntax
    if re.fullmatch(r"(var|input|output)\d+", lexemes):
        Errors.append(lexemes)
        return "Syntax Error"

    #Identifier
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,29}", lexemes):
        return "Identifier"

    #Numeric Literal
    if re.fullmatch(r"[0-9]+", lexemes):
        return "Numeric Literal"

    #Assignment Operator
    if lexemes in assignmentOperator:
        return "Assignment Operator"

    #Arithmetic Operator
    if lexemes in arithmeticOperator:
        return "Arithmetic Operation"

    #Delimiter
    if lexemes == ';':
        return "Delimiter"
    
    if lexemes == '(':
        return "Left Parenthesis"

    if lexemes == ')':
        return "Right Parenthesis"
    
    #Default
    Errors.append(lexemes)
    return "Error"