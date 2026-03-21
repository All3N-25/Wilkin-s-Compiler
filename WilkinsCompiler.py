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

comments = {
    "/*": "SComment",
    "*/": "EComment"
}
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
    isComment = False
    i = 0
    
    while i < len(x):
        com = x[i:i+2]
        char = x[i]

        #Ignore Comments
        if isComment:
            if com == "*/":
                isComment = False
                i += 2
                continue
            i += 1
            continue

        if com == "/*":
            if word:
                lexemes.append(word)
                word = ""
            isComment = True
            i += 2
            continue

        if char in " \n\t":
            if word:
                lexemes.append(word)
                word = ""

        elif char in delimiters:
            if word:
                lexemes.append(word)
                word = ""
            lexemes.append(char)
            if char == ";":
                collections.append(lexemes.copy())
                lexemes.clear()

        elif char in operators:
            if word:
                lexemes.append(word)
                word = ""
            lexemes.append(char)

        else:
            word += char

        i += 1

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
    
    # Statement rules
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
        #print("STACK:", stack, "INPUT:", tokens[index:]) # FOR DEBUGGING - output to trace the parsing process
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
            print(f"Syntax Error: expected {top}, got {current}")
            return False

    print("Syntax Analysis Successful")
    return True

def syntaxAnalysis(tokens: list) -> bool:
    FIRST = compute_first(grammar)
    FOLLOW = compute_follow(grammar, FIRST)
    parsing_table = build_parsing_table(grammar, FIRST, FOLLOW)

    token_stream = extract_token_types(tokens)
    return parse(token_stream, parsing_table, "Program", grammar)


"""
Semenatic Analysis Phase
- Tracks declared variables in a symbol table
- Detects: duplicate declarations, use-before-declaration
"""
def semanticAnalysis(tokens: list) -> bool:
    symbol_table = set() 
    errors = []

    # Turns each delimiter into a line of code
    statements = []
    current_stmt = []
    for token in tokens:
        current_stmt.append(token)
        if token[1] == "SEMICOLON":
            statements.append(current_stmt)
            current_stmt = []

    for stmt in statements:
        if not stmt:
            continue

        types  = [t[1] for t in stmt]   #Values
        lexems = [t[0] for t in stmt]   #Keys
        
        # VarDecl
        if types[0] == "VAR":
            if len(stmt) >= 2 and types[1] == "IDENTIFIER":
                var_name = lexems[1]
                if var_name in symbol_table:
                    errors.append(f"Semantic Error: '{var_name}' is already declared.")
                else:
                    symbol_table.add(var_name)
                for i in range(3, len(stmt) - 1):
                    if types[i] == "IDENTIFIER" and lexems[i] not in symbol_table:
                        errors.append(f"Semantic Error: '{lexems[i]}' used before declaration.")

        # AssignStmt
        elif types[0] == "IDENTIFIER":
            if lexems[0] not in symbol_table:
                errors.append(f"Semantic Error: '{lexems[0]}' assigned before declaration.")
            for i in range(2, len(stmt) - 1):
                if types[i] == "IDENTIFIER" and lexems[i] not in symbol_table:
                    errors.append(f"Semantic Error: '{lexems[i]}' used before declaration.")

        # InputStmt
        elif types[0] == "INPUT":
            if len(stmt) >= 3 and types[2] == "IDENTIFIER":
                if lexems[2] not in symbol_table:
                    errors.append(f"Semantic Error: '{lexems[2]}' in input() is not declared.")

        # OutputStmt
        elif types[0] == "OUTPUT":
            if len(stmt) >= 3 and types[2] == "IDENTIFIER":
                if lexems[2] not in symbol_table:
                    errors.append(f"Semantic Error: '{lexems[2]}' in output() is not declared.")

    if errors:
        for err in errors:
            print(err)
        return False

    print("Semantic Analysis Successful")
    return True


"""
CODE GENERATION PHASE
- Translates the token stream into Python code
"""
def codeGeneration(tokens: list) -> str:
    statements = []
    current_stmt = []
    for token in tokens:
        current_stmt.append(token)
        if token[1] == "SEMICOLON":
            statements.append(current_stmt)
            current_stmt = []

    lines = []

    for stmt in statements:
        types  = [t[1] for t in stmt]
        lexems = [t[0] for t in stmt]

        # VarDecl
        if types[0] == "VAR":
            var_name = lexems[1]
            expr = buildExpr(lexems[3:-1])
            lines.append(f"{var_name} = {expr}")

        # AssignStmt
        elif types[0] == "IDENTIFIER" and types[1] == "ASSIGN":
            var_name = lexems[0]
            expr = buildExpr(lexems[2:-1])
            lines.append(f"{var_name} = {expr}")

        # InputStmt
        elif types[0] == "INPUT":
            var_name = lexems[2]
            lines.append(f'{var_name} = int(input("Enter {var_name}: "))')

        # OutputStmt
        elif types[0] == "OUTPUT":
            var_name = lexems[2]
            lines.append(f'print("{var_name} =", {var_name})')

    return "\n".join(lines)


def buildExpr(lexems: list) -> str:
    result = []
    for lex in lexems:
        if lex == "^": # converts ^ to ** for exponentiation in python
            result.append("**")
        else:
            result.append(lex)
    return " ".join(result)


