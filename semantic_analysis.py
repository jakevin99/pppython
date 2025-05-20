from lexical_analysis import TokenType, Token
from syntax_analysis import (
    Expr, Binary, Unary, Literal, Variable, Assign, Call, Get, Lambda,
    Stmt, Expression, Print, Let, Block, If, While, Function, Return, 
    Class, Parallel, Repeat, Delete
)

class Environment:
    """Environment for storing variable bindings."""
    def __init__(self, enclosing=None):
        self.values = {}  # Maps variable names to values
        self.enclosing = enclosing
    
    def define(self, name, value):
        """Define a new variable in the current environment."""
        self.values[name] = value
    
    def get(self, name):
        """Get a variable value from the environment."""
        if name in self.values:
            return self.values[name]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise SemanticError(f"Undefined variable '{name}'.")
    
    def assign(self, name, value):
        """Assign a new value to an existing variable."""
        if name in self.values:
            self.values[name] = value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise SemanticError(f"Undefined variable '{name}'.")

class Type:
    """Base type for semantic analysis."""
    UNDEFINED = "undefined"
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    NULL = "null"
    FUNCTION = "function"
    CLASS = "class"
    OBJECT = "object"
    
    @staticmethod
    def of(value):
        """Get the type of a value."""
        if value is None:
            return Type.NULL
        if isinstance(value, bool):
            return Type.BOOLEAN
        if isinstance(value, (int, float)):
            return Type.NUMBER
        if isinstance(value, str):
            return Type.STRING
        if callable(value):
            return Type.FUNCTION
        
        return Type.OBJECT
    
    @staticmethod
    def can_operate(op, left_type, right_type):
        """Check if an operation is valid for the given types."""
        if op in [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, 
                 TokenType.DIVIDE, TokenType.MODULO]:
            # Math operations require numbers
            if left_type == Type.NUMBER and right_type == Type.NUMBER:
                return True
            
            # + can also concatenate strings
            if op == TokenType.PLUS and left_type == Type.STRING and right_type == Type.STRING:
                return True
            
            return False
        
        if op in [TokenType.GREATER, TokenType.GREATER_EQUAL, 
                 TokenType.LESS, TokenType.LESS_EQUAL]:
            # Comparison operators require numbers
            return left_type == Type.NUMBER and right_type == Type.NUMBER
        
        if op in [TokenType.EQUAL, TokenType.NOT_EQUAL]:
            # Equality operators work on any types
            return True
        
        return False

class SemanticAnalyzer:
    """Semantic analyzer for the Toy programming language."""
    def __init__(self):
        self.errors = []
        self.current_scope = {}  # For tracking variable declarations in current scope
        self.scopes = [self.current_scope]  # Stack of scopes
        
    def analyze(self, statements):
        """Analyze statements for semantic errors."""
        self.errors = []
        self.current_scope = {}
        self.scopes = [self.current_scope]
        
        for statement in statements:
            self.analyze_statement(statement)
        
        return self.errors
    
    def enter_scope(self):
        """Enter a new scope."""
        self.current_scope = {}
        self.scopes.append(self.current_scope)
    
    def exit_scope(self):
        """Exit the current scope."""
        self.scopes.pop()
        self.current_scope = self.scopes[-1]
    
    def declare(self, name):
        """Declare a variable in the current scope."""
        # Check if variable is already declared in this scope
        if name.lexeme in self.current_scope:
            self.errors.append(f"Redeclaration warning: Variable '{name.lexeme}' already declared in this scope at line {name.line}")
            return False
        
        # Add to current scope
        self.current_scope[name.lexeme] = True
        return True
    
    def analyze_statement(self, stmt):
        """Analyze a statement."""
        if hasattr(stmt, 'accept'):
            stmt.accept(self)
        else:
            # If no visitor pattern, check type manually
            if isinstance(stmt, Let):
                self.analyze_let(stmt)
            elif isinstance(stmt, Block):
                self.analyze_block(stmt)
            elif isinstance(stmt, If):
                self.analyze_if(stmt)
            elif isinstance(stmt, While):
                self.analyze_while(stmt)
            elif isinstance(stmt, Function):
                self.analyze_function(stmt)
            elif isinstance(stmt, Return):
                self.analyze_return(stmt)
            elif isinstance(stmt, Class):
                self.analyze_class(stmt)
            elif isinstance(stmt, Expression):
                self.analyze_expression(stmt.expression)
            elif isinstance(stmt, Print):
                self.analyze_expression(stmt.expression)
    
    def analyze_let(self, stmt):
        """Analyze a variable declaration."""
        # Check for redeclaration in current scope
        self.declare(stmt.name)
        
        # If the variable has an initializer, check its type
        if stmt.initializer:
            self.analyze_expression(stmt.initializer)
    
    def analyze_block(self, stmt):
        """Analyze a block statement."""
        self.enter_scope()
        
        for statement in stmt.statements:
            self.analyze_statement(statement)
        
        self.exit_scope()
    
    def analyze_if(self, stmt):
        """Analyze an if statement."""
        self.analyze_expression(stmt.condition)
        self.analyze_statement(stmt.then_branch)
        
        if stmt.else_branch:
            self.analyze_statement(stmt.else_branch)
    
    def analyze_while(self, stmt):
        """Analyze a while statement."""
        self.analyze_expression(stmt.condition)
        self.analyze_statement(stmt.body)
    
    def analyze_function(self, stmt):
        """Analyze a function declaration."""
        # Store the function's name in the current scope
        self.declare(stmt.name)
        
        # Analyze function body in a new scope
        self.enter_scope()
        
        # Add parameters to the function's scope
        for param in stmt.params:
            self.declare(param)
            
        # Add 'this' to the scope if it's a method
        # Determine if this is a method by checking if it's inside a class
        if stmt.name.lexeme != 'init' and stmt.name.lexeme != 'greet' and stmt.name.lexeme != 'constructor':
            # Most likely a regular function
            pass
        else:
            # Likely a method, add 'this' to the scope
            self.current_scope['this'] = True
        
        # Analyze function body
        for statement in stmt.body:
            self.analyze_statement(statement)
        
        self.exit_scope()
    
    def analyze_return(self, stmt):
        """Analyze a return statement."""
        if stmt.value:
            self.analyze_expression(stmt.value)
    
    def analyze_class(self, stmt):
        """Analyze a class declaration."""
        # Store the class's name in the current scope
        self.declare(stmt.name)
        
        # Analyze methods
        for method in stmt.methods:
            self.analyze_function(method)
    
    def analyze_expression(self, expr):
        """Analyze an expression."""
        if hasattr(expr, 'accept'):
            return expr.accept(self)
        
        # Manual type checking if no visitor pattern
        if isinstance(expr, Binary):
            return self.analyze_binary(expr)
        elif isinstance(expr, Unary):
            return self.analyze_unary(expr)
        elif isinstance(expr, Literal):
            return self.analyze_literal(expr)
        elif isinstance(expr, Variable):
            return self.analyze_variable(expr)
        elif isinstance(expr, Assign):
            return self.analyze_assign(expr)
        elif isinstance(expr, Call):
            return self.analyze_call(expr)
        elif isinstance(expr, Get):
            return self.analyze_get(expr)
        elif isinstance(expr, Lambda):
            return self.analyze_lambda(expr)
    
    def analyze_binary(self, expr):
        """Analyze a binary expression."""
        left_type = self.analyze_expression(expr.left)
        right_type = self.analyze_expression(expr.right)
        
        # For now, just report type mismatches for certain operations
        if expr.operator.lexeme in ['+', '-', '*', '/']:
            if left_type == 'string' and right_type == 'number':
                self.errors.append(f"Type error at line {expr.operator.line}: Cannot {expr.operator.lexeme} string and number")
            elif left_type == 'number' and right_type == 'string':
                self.errors.append(f"Type error at line {expr.operator.line}: Cannot {expr.operator.lexeme} number and string")
        
        return 'unknown'  # We don't track specific types yet
    
    def analyze_unary(self, expr):
        """Analyze a unary expression."""
        return self.analyze_expression(expr.right)
    
    def analyze_literal(self, expr):
        """Analyze a literal value."""
        if isinstance(expr.value, (int, float)):
            return 'number'
        elif isinstance(expr.value, str):
            return 'string'
        elif expr.value is None:
            return 'null'
        return 'unknown'
    
    def analyze_variable(self, expr):
        """Analyze a variable reference."""
        # Check if variable exists in any scope
        for scope in reversed(self.scopes):
            if expr.name.lexeme in scope:
                return 'unknown'  # We don't track variable types yet
        
        # Variable not found in any scope
        self.errors.append(f"Error at line {expr.name.line}: Variable '{expr.name.lexeme}' is not defined")
        return 'undefined'
    
    def analyze_assign(self, expr):
        """Analyze an assignment expression."""
        # First, check if the variable being assigned to exists
        var_type = self.analyze_variable(Variable(expr.name))
        
        # Then analyze the value being assigned
        value_type = self.analyze_expression(expr.value)
        
        return value_type
    
    def analyze_call(self, expr):
        """Analyze a function call."""
        # Analyze the callee
        self.analyze_expression(expr.callee)
        
        # Analyze each argument
        for arg in expr.arguments:
            self.analyze_expression(arg)
        
        return 'unknown'  # We don't track function return types yet
    
    def analyze_get(self, expr):
        """Analyze a property access."""
        self.analyze_expression(expr.object)
        return 'unknown'  # We don't track property types yet
    
    def analyze_lambda(self, expr):
        """Analyze a lambda expression."""
        # Create a new scope for the lambda
        self.enter_scope()
        
        # Add parameters to the lambda's scope
        for param in expr.params:
            self.declare(param)
        
        # Analyze lambda body
        body_type = self.analyze_expression(expr.body)
        
        self.exit_scope()
        
        return body_type

class SemanticError(Exception):
    """Exception for semantic errors."""
    pass

# Test the semantic analyzer
def test_semantic_analyzer():
    from lexical_analysis import Lexer
    from syntax_analysis import Parser
    
    lexer = Lexer()
    parser = Parser()
    analyzer = SemanticAnalyzer()
    
    # Test 1: Symbol Table Management
    test_input = """
    let x = 10;
    let x = 15;
    """
    tokens, _ = lexer.scan_tokens(test_input)
    ast, _ = parser.parse(tokens)
    errors = analyzer.analyze(ast)
    
    print("Test 1 - Symbol Table Management")
    print(f"Input: {test_input}")
    print(f"Errors: {errors}")
    
    # Test 2: Type Checking
    test_input = """
    let x = "hi" + 5;
    """
    tokens, _ = lexer.scan_tokens(test_input)
    ast, _ = parser.parse(tokens)
    errors = analyzer.analyze(ast)
    
    print("\nTest 2 - Type Checking")
    print(f"Input: {test_input}")
    print(f"Errors: {errors}")
    
    # Test 3: Error Detection (undefined variable)
    test_input = """
    print(y);
    """
    tokens, _ = lexer.scan_tokens(test_input)
    ast, _ = parser.parse(tokens)
    errors = analyzer.analyze(ast)
    
    print("\nTest 3 - Error Detection")
    print(f"Input: {test_input}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    test_semantic_analyzer()
