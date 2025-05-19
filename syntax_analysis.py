from lexical_analysis import TokenType, Token, Lexer

# Abstract Syntax Tree nodes
class Expr:
    """Base class for all expressions."""
    pass

class Binary(Expr):
    """Binary expression with left operand, operator, and right operand."""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"({self.left} {self.operator.lexeme} {self.right})"

class Unary(Expr):
    """Unary expression with operator and right operand."""
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"({self.operator.lexeme}{self.right})"

class Literal(Expr):
    """Literal value."""
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)

class Variable(Expr):
    """Variable reference."""
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name.lexeme

class Assign(Expr):
    """Variable assignment."""
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"{self.name.lexeme} = {self.value}"

class Call(Expr):
    """Function call."""
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren  # Closing parenthesis token for error reporting
        self.arguments = arguments
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.callee}({args_str})"

class Get(Expr):
    """Property access."""
    def __init__(self, object, name):
        self.object = object
        self.name = name
    
    def __str__(self):
        return f"{self.object}.{self.name.lexeme}"

class Set(Expr):
    """Property assignment."""
    def __init__(self, object, name, value):
        self.object = object
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"{self.object}.{self.name.lexeme} = {self.value}"

class Lambda(Expr):
    """Lambda function."""
    def __init__(self, params, body):
        self.params = params
        self.body = body
    
    def __str__(self):
        params_str = ", ".join(param.lexeme for param in self.params)
        return f"({params_str}) => {self.body}"

# Statement types
class Stmt:
    """Base class for all statements."""
    pass

class Expression(Stmt):
    """Expression statement."""
    def __init__(self, expression):
        self.expression = expression

class Print(Stmt):
    """Print statement."""
    def __init__(self, expression):
        self.expression = expression

class Let(Stmt):
    """Variable declaration."""
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

class Block(Stmt):
    """Block statement."""
    def __init__(self, statements):
        self.statements = statements

class If(Stmt):
    """If statement."""
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class While(Stmt):
    """While statement."""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Function(Stmt):
    """Function declaration."""
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Return(Stmt):
    """Return statement."""
    def __init__(self, keyword, value=None):
        self.keyword = keyword
        self.value = value

class Class(Stmt):
    """Class declaration."""
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

class Parallel(Stmt):
    """Parallel execution block."""
    def __init__(self, body):
        self.body = body

class Repeat(Stmt):
    """Repeat statement."""
    def __init__(self, count, body):
        self.count = count
        self.body = body

class Delete(Stmt):
    """Delete statement (for memory management)."""
    def __init__(self, expression):
        self.expression = expression

class Parser:
    """Parser for the Toy programming language."""
    def __init__(self):
        self.tokens = []
        self.current = 0
        self.errors = []
    
    def parse(self, tokens):
        """Parse tokens into abstract syntax tree."""
        self.tokens = tokens
        self.current = 0
        self.errors = []
        
        # Program is a series of statements
        statements = []
        while not self.is_at_end():
            try:
                statements.append(self.declaration())
            except ParseError as error:
                self.errors.append(str(error))
                self.synchronize()
        
        return statements, self.errors
    
    # Recursive descent parsing methods
    def declaration(self):
        """Parse a declaration statement."""
        if self.match(TokenType.LET):
            return self.let_declaration()
        if self.match(TokenType.FUNCTION):
            return self.function_declaration("function")
        if self.match(TokenType.CLASS):
            return self.class_declaration()
        
        return self.statement()
    
    def let_declaration(self):
        """Parse a variable declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Let(name, initializer)
    
    def function_declaration(self, kind):
        """Parse a function declaration."""
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        
        return Function(name, parameters, body)
    
    def class_declaration(self):
        """Parse a class declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function_declaration("method"))
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        
        return Class(name, methods)
    
    def statement(self):
        """Parse a statement."""
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.PARALLEL):
            return self.parallel_statement()
        if self.match(TokenType.REPEAT):
            return self.repeat_statement()
        if self.match(TokenType.DELETE):
            return self.delete_statement()
        
        return self.expression_statement()
    
    def print_statement(self):
        """Parse a print statement."""
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)
    
    def block(self):
        """Parse a block of statements."""
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def if_statement(self):
        """Parse an if statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return If(condition, then_branch, else_branch)
    
    def while_statement(self):
        """Parse a while statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        
        body = self.statement()
        
        return While(condition, body)
    
    def return_statement(self):
        """Parse a return statement."""
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)
    
    def parallel_statement(self):
        """Parse a parallel execution block."""
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after 'parallel'.")
        body = self.block()
        return Parallel(body)
    
    def repeat_statement(self):
        """Parse a repeat statement."""
        count = self.expression()
        self.consume(TokenType.TIMES, "Expect 'times' after repeat count.")
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after 'times'.")
        body = self.block()
        
        return Repeat(count, body)
    
    def delete_statement(self):
        """Parse a delete statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'delete'.")
        expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after delete statement.")
        
        return Delete(expr)
    
    def expression_statement(self):
        """Parse an expression statement."""
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)
    
    def expression(self):
        """Parse an expression."""
        # Check for lambda expressions
        if self.check(TokenType.LEFT_PAREN) and self.check_next(TokenType.IDENTIFIER):
            return self.lambda_expr()
        
        return self.assignment()
    
    def lambda_expr(self):
        """Parse a lambda expression: (params) => expr"""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' for lambda parameters.")
        
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after lambda parameters.")
        self.consume(TokenType.ARROW, "Expect '=>' after lambda parameters.")
        
        body = self.expression()
        
        return Lambda(parameters, body)
    
    def assignment(self):
        """Parse an assignment expression."""
        expr = self.equality()
        
        if self.match(TokenType.ASSIGN):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expr
    
    def equality(self):
        """Parse equality expressions."""
        expr = self.comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparison(self):
        """Parse comparison expressions."""
        expr = self.term()
        
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, 
                          TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def term(self):
        """Parse terms (addition/subtraction)."""
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def factor(self):
        """Parse factors (multiplication/division)."""
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def unary(self):
        """Parse unary expressions."""
        if self.match(TokenType.MINUS, TokenType.NOT):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.call()
    
    def call(self):
        """Parse call expressions."""
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        
        return expr
    
    def finish_call(self, callee):
        """Parse the arguments to a function call."""
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        
        return Call(callee, paren, arguments)
    
    def primary(self):
        """Parse primary expressions."""
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr
        if self.match(TokenType.NEW):
            return self.new_expression()
        if self.match(TokenType.NULL):
            return Literal(None)
        if self.match(TokenType.THIS):
            return Variable(self.previous())
        
        raise self.error(self.peek(), "Expect expression.")
    
    def new_expression(self):
        """Parse a 'new' expression for instantiating classes."""
        class_name = self.consume(TokenType.IDENTIFIER, "Expect class name after 'new'.")
        
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after class name.")
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        
        return Call(Variable(class_name), paren, arguments)
    
    # Helper methods
    def match(self, *types):
        """Check if current token matches any of the given types."""
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def check(self, type):
        """Check if current token is of the given type."""
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def check_next(self, type):
        """Check if the next token is of the given type."""
        if self.is_at_end() or self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == type
    
    def advance(self):
        """Advance to the next token."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self):
        """Check if we've reached the end of the tokens."""
        return self.peek().type == TokenType.EOF
    
    def peek(self):
        """Return the current token."""
        return self.tokens[self.current]
    
    def previous(self):
        """Return the previous token."""
        return self.tokens[self.current - 1]
    
    def consume(self, type, message):
        """Consume the current token if it's of the given type."""
        if self.check(type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    def error(self, token, message):
        """Report a parsing error."""
        if token.type == TokenType.EOF:
            error_msg = f"Error at end: {message}"
        else:
            error_msg = f"Error at '{token.lexeme}': {message}"
        
        self.errors.append(error_msg)
        return ParseError(error_msg)
    
    def synchronize(self):
        """Recover from a parsing error."""
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [
                TokenType.CLASS, TokenType.FUNCTION, TokenType.LET,
                TokenType.FOR, TokenType.IF, TokenType.WHILE, TokenType.PRINT,
                TokenType.RETURN
            ]:
                return
            
            self.advance()

class ParseError(Exception):
    """Exception for parsing errors."""
    pass

# Testing the parser
def test_parser():
    lexer = Lexer()
    parser = Parser()
    
    # Test 1: Parser Correctness
    test_input = "if (x > 5) { print(\"hi\"); }"
    tokens, _ = lexer.scan_tokens(test_input)
    ast, errors = parser.parse(tokens)
    
    print(f"Test 1 - Input: {test_input}")
    if errors:
        print(f"  Errors: {errors}")
    else:
        print("  Parsed successfully")
    
    # Test 2: AST Generation
    test_input = "x = a + b * c;"
    tokens, _ = lexer.scan_tokens(test_input)
    ast, errors = parser.parse(tokens)
    
    print(f"\nTest 2 - Input: {test_input}")
    if errors:
        print(f"  Errors: {errors}")
    else:
        # We should have an Expression(Assign) statement
        expr_stmt = ast[0]
        print(f"  AST: {expr_stmt.expression}")
    
    # Test 3: Error Handling
    test_input = "if x > 5 { print(\"missing parentheses\"); }"
    tokens, _ = lexer.scan_tokens(test_input)
    ast, errors = parser.parse(tokens)
    
    print(f"\nTest 3 - Input: {test_input}")
    print(f"  Errors: {errors}")

if __name__ == "__main__":
    test_parser()
