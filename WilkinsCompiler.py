import re

keywords = ["var", "input", "output"]
operators = {
    '+': "PLUS",
    '-': "MINUS",
    '*': "MULT",
    '/': "DIV",
    '^': "POW",
    '=': "ASSIGN"
}
delimiters = {
    ';': "SEMICOLON",
    '(': "LPAREN",
    ')': "RPAREN"
}
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

        #Delimiters
        elif char in delimiters:
            if delimiters[char] == "SEMICOLON":
                if word:
                    lexemes.append(word)
                    word = ""
                lexemes.append(char)
                collections.append(lexemes.copy())

                lexemes.clear()
            else:
                if word:
                    lexemes.append(word)
                    word = ""
                lexemes.append(char)

        #Operators
        elif char in operators:
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
    
    #Keywords
    if lexemes == "var":
        return "VAR"
    elif lexemes == "input":
        return "INPUT"
    elif lexemes == "output":
        return "OUTPUT"

    #Identifier/Variable Name
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,29}", lexemes):
        return "IDENTIFIER"

    #Numeric Literal
    if re.fullmatch(r"[0-9]+", lexemes):
        return "NUMBER"

    #Arithmetic and Assignment Operator
    if lexemes in operators:
        return operators[lexemes]
    
    #Delimiters
    if lexemes in delimiters:
        return delimiters[lexemes]

    #Default
    Errors.append(lexemes)
    return "ERROR"



"""
Syntax Analyzer Phase
- determines if the sequence of tokens is correct according to the grammar rules using LL(1) parsing method
- gets the token from lexical, removes the lexeme and only keeps the token type for syntax analysis
- gets FIRST and FOLLOW of grammar rules, builds parsing table, and parses the token stream
"""

grammar = { # Rules
    "Program": [["StmtList"]],
    "StmtList": [["Stmt", "StmtList"], ["ε"]],
    "Stmt": [["VarDecl"], ["AssignStmt"], ["InputStmt"], ["OutputStmt"]],
    "AssignStmt": [["IDENTIFIER", "ASSIGN", "Expr", "SEMICOLON"]],

    "VarDecl": [["VAR", "IDENTIFIER", "ASSIGN", "Expr", "SEMICOLON"]],
    "InputStmt": [["INPUT", "LPAREN", "IDENTIFIER", "RPAREN", "SEMICOLON"]],
    "OutputStmt": [["OUTPUT", "LPAREN", "IDENTIFIER", "RPAREN", "SEMICOLON"]],

    # Expression rules
    "Expr": [["Term", "ExprPrime"]],

    "ExprPrime": [
        ["PLUS", "Term", "ExprPrime"],
        ["MINUS", "Term", "ExprPrime"],
        ["ε"]
    ],

    "Term": [["Factor", "TermPrime"]],

    "TermPrime": [
        ["MULT", "Factor", "TermPrime"],
        ["DIV", "Factor", "TermPrime"],
        ["POW", "Factor", "TermPrime"],  # power
        ["ε"]
    ],

    "Factor": [
        ["NUMBER"],
        ["IDENTIFIER"],
        ["LPAREN", "Expr", "RPAREN"]
    ]
}

def extract_token_types(tokens: list) -> list:
    return [tok_type for _, tok_type in tokens] + ['$']

def compute_first(grammar: dict) -> dict:
    FIRST = {}
    for nt in grammar:
        FIRST[nt] = set()

    changed = True

    while changed:
        changed = False

        for nt in grammar:
            for production in grammar[nt]:

                add_epsilon = True

                for symbol in production:

                    if symbol not in grammar:  # terminal
                        if symbol not in FIRST[nt]:
                            FIRST[nt].add(symbol)
                            changed = True
                        add_epsilon = False
                        break

                    before = len(FIRST[nt])
                    FIRST[nt] |= (FIRST[symbol] - {"ε"})
                    if len(FIRST[nt]) > before:
                        changed = True

                    if "ε" not in FIRST[symbol]:
                        add_epsilon = False
                        break

                if add_epsilon:
                    if "ε" not in FIRST[nt]:
                        FIRST[nt].add("ε")
                        changed = True

    return FIRST

def compute_follow(grammar: dict, FIRST: dict) -> dict:
    FOLLOW = {}
    for nt in grammar:
        FOLLOW[nt] = set()

    start_symbol = next(iter(grammar)) # get start symbol
    FOLLOW[start_symbol].add("$")

    changed = True

    while changed:
        changed = False

        for nt in grammar:
            for production in grammar[nt]:

                for i, symbol in enumerate(production):

                    if symbol in grammar:

                        beta = production[i+1:]

                        first_beta = set()
                        epsilon_in_all = True

                        for b in beta:

                            if b not in grammar:
                                first_beta.add(b)
                                epsilon_in_all = False
                                break

                            first_beta |= (FIRST[b] - {"ε"})

                            if "ε" not in FIRST[b]:
                                epsilon_in_all = False
                                break

                        before = len(FOLLOW[symbol])
                        FOLLOW[symbol] |= first_beta

                        if epsilon_in_all:
                            FOLLOW[symbol] |= FOLLOW[nt]

                        if len(FOLLOW[symbol]) > before:
                            changed = True

    return FOLLOW

def first_of_string(symbols: list, FIRST: dict, grammar: dict) -> set:
    result = set()

    for sym in symbols:
        if sym not in grammar:  # terminal
            result.add(sym)
            return result

        result |= (FIRST[sym] - {"ε"})

        if "ε" not in FIRST[sym]:
            return result

    result.add("ε")
    return result

def build_parsing_table(grammar: dict, FIRST: dict, FOLLOW: dict) -> dict:
    table = {}

    for A in grammar:
        for production in grammar[A]:

            first_alpha = first_of_string(production, FIRST, grammar)

            for terminal in (first_alpha - {"ε"}):
                table[(A, terminal)] = production

            if "ε" in first_alpha:
                for terminal in FOLLOW[A]:
                    table[(A, terminal)] = production

    return table

def parse(tokens: list, table: dict, start_symbol: str, grammar: dict) -> bool:

    stack = ["$", start_symbol]
    index = 0

    while stack:
        top = stack.pop()
        current = tokens[index]

        #print("STACK:", stack, "INPUT:", tokens[index:]) # Debugging output to trace the parsing process

        if top == current:
            index += 1

        elif top == "ε":
            continue

        elif top not in grammar:
            print(f"Syntax Error: expected {top}, got {current}")
            return False

        elif (top, current) in table:
            production = table[(top, current)]
            stack.extend(reversed(production))

        else:
            print(f"Syntax Error at token {current}")
            return False

    print("Syntax Analysis Successful")
    return True

def syntaxAnalysis(tokens: list) -> bool:
    FIRST = compute_first(grammar)
    FOLLOW = compute_follow(grammar, FIRST)
    parsing_table = build_parsing_table(grammar, FIRST, FOLLOW)

    token_stream = extract_token_types(tokens)
    return parse(token_stream, parsing_table, "Program", grammar)