import re

dataTypes = ["int", "double", "float", "char", "string"]
arithmeticOperator = ['+', '-', '*', '/']
assignmentOperator = ['=']

Errors = []

def tokenizer(x: str) -> list:
    token = []
    word = ""

    for i, char in enumerate(x):
        if(char == ' '):
            if word:
                token.append(word)
                word=""
                token.append('_')
        elif(char == ';'):
            if word:
                token.append(word)
                word=""
                token.append(char)
        elif (i == len(x) - 1):
            word = word + char
            token.append(word)
        else:
            word = word + char
    
    return token

def classifier(token: str) -> str:
    if token == "_":
        return "White Space"
    
    elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,29}", token):
        if token in dataTypes:
            return "Data Type"
        
        elif re.fullmatch(r"(int|double|float|char|string)\d+", token):
            return "Syntax Error (keyword followed by digits)"
        
        elif any(substring in token for substring in assignmentOperator):
        #Checks int (x=100+100);
            if any(substring in token for substring in arithmeticOperator):
                return "Identifier, Assignment Operator, & Arithmetic Comparison"
        else:
            return "Identifier"

    elif re.fullmatch(r"[0-9]*", token):
        return "Numeric Literal"
    
    elif any(substring in token for substring in assignmentOperator):
        #Checks int x (=100+100);
        if any(substring in token for substring in arithmeticOperator):
            return "Assignment Operator & Arithmetic Comparison"

        return "Assignment Operator"

    elif any(substring in token for substring in arithmeticOperator):
        return "Arithmetic Comparison"
        
    elif token ==';':
        return "Delimiter"
    
    else:
        Errors.append(token)
        return "Error"


file_path = "/home/allen/School/Programming Languages/Final Proj/Testing.txt"

try:
    with open(file_path, 'r') as file:
        content = file.read() # Read the entire file content into a single string
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except PermissionError:
    print(f"Error: Permission denied for file '{file_path}'.")

Input = tokenizer(content)
print("CALAYAN, Jan Allen O.")
print(Input)

for tok in Input:
    result = classifier(tok)

    print(f"{tok}\t{result}")

if Errors:
    for err in Errors:
        print(f"Error at {err}")

