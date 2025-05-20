import re
from enum import Enum, auto

class TokenType(Enum):
    # Keywords
    LET = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    FUNCTION = auto()
    RETURN = auto()
    CLASS = auto()
    NEW = auto()
    NULL = auto()
    PARALLEL = auto()
    REPEAT = auto()
    TIMES = auto()
    DELETE = auto()
    THIS = auto()
    PRINT = auto()
    
    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER = auto()
    LESS = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Punctuation
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()
    ARROW = auto()
    
    # Special
    EOF = auto()

class Token:
    def __init__(self, token_type, lexeme, literal=None, line=1):
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __str__(self):
        return f"Token({self.type}, '{self.lexeme}', {self.literal}, line {self.line})"

class Lexer:
    """Lexer for the Toy programming language."""
    def __init__(self):
        # Keywords mapping
        self.keywords = {
            "let": TokenType.LET,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "function": TokenType.FUNCTION,
            "return": TokenType.RETURN,
            "class": TokenType.CLASS,
            "new": TokenType.NEW,
            "null": TokenType.NULL,
            "parallel": TokenType.PARALLEL,
            "repeat": TokenType.REPEAT,
            "times": TokenType.TIMES,
            "delete": TokenType.DELETE,
            "this": TokenType.THIS,
            "print": TokenType.PRINT
        }
        
        # Initialize state
        self.source = ""
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.errors = []

    def scan_tokens(self, source):
        """Scan the source code and return list of tokens."""
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.errors = []
        
        while not self.is_at_end():
            # Beginning of the next lexeme
            self.start = self.current
            self.scan_token()
            
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens, self.errors
    
    def is_at_end(self):
        """Check if we've reached the end of the source."""
        return self.current >= len(self.source)
    
    def scan_token(self):
        """Scan a single token."""
        c = self.advance()
        
        # Handle whitespace
        if c in [' ', '\r', '\t']:
            return
        elif c == '\n':
            self.line += 1
            return
        
        # Handle comments
        elif c == '/' and self.match('/'):
            # A comment goes until the end of the line
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()
            return
        
        # Handle operators and punctuation
        elif c == '(': self.add_token(TokenType.LEFT_PAREN)
        elif c == ')': self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{': self.add_token(TokenType.LEFT_BRACE)
        elif c == '}': self.add_token(TokenType.RIGHT_BRACE)
        elif c == '[': self.add_token(TokenType.LEFT_BRACKET)
        elif c == ']': self.add_token(TokenType.RIGHT_BRACKET)
        elif c == ',': self.add_token(TokenType.COMMA)
        elif c == '.': self.add_token(TokenType.DOT)
        elif c == ';': self.add_token(TokenType.SEMICOLON)
        elif c == '+': self.add_token(TokenType.PLUS)
        elif c == '-': 
            if self.match('>'):
                self.add_token(TokenType.ARROW)
            else:
                self.add_token(TokenType.MINUS)
        elif c == '*': self.add_token(TokenType.MULTIPLY)
        elif c == '/': self.add_token(TokenType.DIVIDE)
        elif c == '%': self.add_token(TokenType.MODULO)
        
        # Operators with potential second character
        elif c == '=':
            if self.match('='):
                self.add_token(TokenType.EQUAL)
            elif self.match('>'):
                self.add_token(TokenType.ARROW)
            else:
                self.add_token(TokenType.ASSIGN)
        elif c == '!':
            if self.match('='):
                self.add_token(TokenType.NOT_EQUAL)
            else:
                self.add_token(TokenType.NOT)
        elif c == '<':
            if self.match('='):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
        elif c == '>':
            if self.match('='):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
        
        # String literals
        elif c == '"':
            self.string()
        
        # Number literals
        elif c.isdigit():
            self.number()
        
        # Identifiers and keywords
        elif self.is_alpha(c):
            self.identifier()
        
        # Invalid token
        else:
            error_msg = f"Invalid token '{c}' @ line {self.line}"
            self.errors.append(error_msg)
    
    def advance(self):
        """Consume the next character and return it."""
        char = self.source[self.current]
        self.current += 1
        return char
    
    def match(self, expected):
        """Check if the current character matches expected."""
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        return True
    
    def peek(self):
        """Return the current character without consuming it."""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self):
        """Return the next character without consuming it."""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def string(self):
        """Process a string literal."""
        # Keep consuming until closing quote
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        # Unterminated string
        if self.is_at_end():
            self.errors.append(f"Unterminated string @ line {self.line}")
            return
        
        # Consume the closing "
        self.advance()
        
        # Get the string value (without the quotes)
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)
    
    def number(self):
        """Process a number literal."""
        # Consume digits
        while self.peek().isdigit():
            self.advance()
        
        # Look for decimal part
        if self.peek() == '.' and self.peek_next().isdigit():
            # Consume the '.'
            self.advance()
            
            # Consume decimal digits
            while self.peek().isdigit():
                self.advance()
        
        # Convert to number
        value = float(self.source[self.start:self.current])
        # Store as integer if it's a whole number
        if value.is_integer():
            value = int(value)
        
        self.add_token(TokenType.NUMBER, value)
    
    def identifier(self):
        """Process an identifier or keyword."""
        while self.is_alphanumeric(self.peek()):
            self.advance()
        
        # See if it's a keyword
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        
        self.add_token(token_type)
    
    def is_alpha(self, c):
        """Check if character is alphabetic or underscore."""
        return c.isalpha() or c == '_'
    
    def is_alphanumeric(self, c):
        """Check if character is alphanumeric or underscore."""
        return c.isalnum() or c == '_'
    
    def add_token(self, token_type, literal=None):
        """Add a token to the list."""
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

# For testing the lexer
def test_lexer():
    lexer = Lexer()
    
    # Test 1: Tokenizer Correctness
    test_input = "let x = 10 + 5;"
    tokens, errors = lexer.scan_tokens(test_input)
    print(f"Test 1 - Input: {test_input}")
    for token in tokens:
        print(f"  {token}")
    
    # Test 2: Error Handling
    test_input = "let x = 10 @ 5;"
    tokens, errors = lexer.scan_tokens(test_input)
    print(f"\nTest 2 - Input: {test_input}")
    for error in errors:
        print(f"  Error: {error}")
    
    # Test 3: Efficiency (comments/whitespace)
    test_input = "let x = 10; // comment"
    tokens, errors = lexer.scan_tokens(test_input)
    print(f"\nTest 3 - Input: {test_input}")
    for token in tokens:
        print(f"  {token}")

if __name__ == "__main__":
    test_lexer()
