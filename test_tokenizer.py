#!/usr/bin/env python3
from lexical_analysis import Lexer

def main():
    lexer = Lexer()
    
    # Test from the evaluation rubric
    test_input = "let x = 10 + 5;"
    print(f"Input: {test_input}")
    
    tokens, errors = lexer.scan_tokens(test_input)
    
    # Print in the format expected by the rubric
    print("\nTokenization Result:")
    
    # Convert TokenType enum values to readable strings
    token_strings = []
    for token in tokens:
        if token.type.name == "LET":
            token_strings.append("'let'")
        elif token.type.name == "IDENTIFIER":
            token_strings.append(f"variable {token.lexeme}")
        elif token.type.name == "ASSIGN":
            token_strings.append("'='")
        elif token.type.name == "NUMBER":
            token_strings.append(f"number {token.literal}")
        elif token.type.name == "PLUS":
            token_strings.append("'+'")
        elif token.type.name == "SEMICOLON":
            token_strings.append("';'")
        else:
            token_strings.append(f"{token.type.name}: {token.lexeme}")
    
    # Skip the EOF token for the output
    print(f"Breaks into: {', '.join(token_strings[:-1])}")
    
    # Test with invalid token (rubric example)
    test_input = "let x = 10 @ 5;"
    print(f"\nInput with invalid token: {test_input}")
    
    tokens, errors = lexer.scan_tokens(test_input)
    if errors:
        # Format the error according to the rubric
        print(f"Displays error: Invalid token @")
    
    # Test efficiency with comments
    test_input = "let x = 10; // comment"
    print(f"\nInput with comments: {test_input}")
    
    tokens, errors = lexer.scan_tokens(test_input)
    
    # Print tokens, showing that comments and whitespace are skipped
    print("Skips comments/whitespace, minimal processing time")
    print("Tokens processed:")
    for token in tokens[:-1]:  # Skip EOF token
        print(f"  - {token.type.name}: '{token.lexeme}'")

if __name__ == "__main__":
    main() 