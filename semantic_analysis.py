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
    """Semantic analyzer for the Toy language."""
    def __init__(self):
        self.environment = Environment()
        self.errors = []
        self.current_function = None  # For tracking returns
    
    def analyze(self, statements):
        """Analyze a list of statements for semantic errors."""
        self.errors = []
        
        for stmt in statements:
            try:
                self.analyze_stmt(stmt)
            except SemanticError as error:
                self.errors.append(str(error))
                # Continue analyzing after error
        
        return self.errors
    
    def analyze_stmt(self, stmt):
        """Analyze a statement."""
        if isinstance(stmt, Expression):
            self.analyze_expr(stmt.expression)
        elif isinstance(stmt, Print):
            self.analyze_expr(stmt.expression)
        elif isinstance(stmt, Let):
            self.analyze_let(stmt)
        elif isinstance(stmt, Block):
            # Create a new scope for block statements
            previous_env = self.environment
            self.environment = Environment(previous_env)
            
            for statement in stmt.statements:
                self.analyze_stmt(statement)
            
            # Restore environment
            self.environment = previous_env
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
        elif isinstance(stmt, Parallel):
            # Analyze each statement in the parallel block
            for statement in stmt.body:
                self.analyze_stmt(statement)
        elif isinstance(stmt, Repeat):
            self.analyze_repeat(stmt)
        elif isinstance(stmt, Delete):
            self.analyze_delete(stmt)
    
    def analyze_let(self, stmt):
        """Analyze a variable declaration."""
        # Check for redeclaration in the current scope
        if stmt.name.lexeme in self.environment.values:
            self.errors.append(f"Redeclaration of variable '{stmt.name.lexeme}'.")
        
        # Analyze initializer if present
        if stmt.initializer is not None:
            value_type = self.analyze_expr(stmt.initializer)
        else:
            value_type = Type.UNDEFINED
        
        # Define variable in environment
        self.environment.define(stmt.name.lexeme, value_type)
    
    def analyze_if(self, stmt):
        """Analyze an if statement."""
        # Condition should be a boolean expression
        condition_type = self.analyze_expr(stmt.condition)
        
        # Analyze branches
        self.analyze_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.analyze_stmt(stmt.else_branch)
    
    def analyze_while(self, stmt):
        """Analyze a while statement."""
        # Condition should be a boolean expression
        condition_type = self.analyze_expr(stmt.condition)
        
        # Analyze body
        self.analyze_stmt(stmt.body)
    
    def analyze_function(self, stmt):
        """Analyze a function declaration."""
        # Define function in environment
        self.environment.define(stmt.name.lexeme, Type.FUNCTION)
        
        # Create new environment for function body
        previous_env = self.environment
        self.environment = Environment(previous_env)
        
        # Define parameters in function scope
        for param in stmt.params:
            self.environment.define(param.lexeme, Type.UNDEFINED)
        
        # Track current function for return analysis
        previous_function = self.current_function
        self.current_function = stmt
        
        # Analyze function body
        for statement in stmt.body:
            self.analyze_stmt(statement)
        
        # Restore state
        self.current_function = previous_function
        self.environment = previous_env
    
    def analyze_return(self, stmt):
        """Analyze a return statement."""
        # Check if return is inside a function
        if self.current_function is None:
            raise SemanticError("Cannot return from top-level code.")
        
        # Analyze return value if present
        if stmt.value is not None:
            self.analyze_expr(stmt.value)
    
    def analyze_class(self, stmt):
        """Analyze a class declaration."""
        # Define class in environment
        self.environment.define(stmt.name.lexeme, Type.CLASS)
        
        # Create new environment for method definitions
        previous_env = self.environment
        self.environment = Environment(previous_env)
        
        # Analyze each method
        for method in stmt.methods:
            self.analyze_function(method)
        
        # Restore environment
        self.environment = previous_env
    
    def analyze_repeat(self, stmt):
        """Analyze a repeat statement."""
        # Count should be a number
        count_type = self.analyze_expr(stmt.count)
        if count_type != Type.NUMBER:
            self.errors.append("Repeat count must be a number.")
        
        # Analyze body statements
        for statement in stmt.body:
            self.analyze_stmt(statement)
    
    def analyze_delete(self, stmt):
        """Analyze a delete statement."""
        # Can only delete variables or object properties
        expr_type = self.analyze_expr(stmt.expression)
        
        # Object or array access is valid for deletion
        if not isinstance(stmt.expression, (Variable, Get)):
            self.errors.append("Can only delete variables or object properties.")
    
    def analyze_expr(self, expr):
        """Analyze an expression and return its type."""
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
        
        return Type.UNDEFINED
    
    def analyze_binary(self, expr):
        """Analyze a binary expression."""
        left_type = self.analyze_expr(expr.left)
        right_type = self.analyze_expr(expr.right)
        
        # Check if operation is valid for types
        if not Type.can_operate(expr.operator.type, left_type, right_type):
            self.errors.append(f"Cannot {expr.operator.lexeme} {left_type} and {right_type}.")
            return Type.UNDEFINED
        
        # Determine result type
        if expr.operator.type in [TokenType.GREATER, TokenType.GREATER_EQUAL, 
                                 TokenType.LESS, TokenType.LESS_EQUAL,
                                 TokenType.EQUAL, TokenType.NOT_EQUAL]:
            return Type.BOOLEAN
        
        if expr.operator.type == TokenType.PLUS and left_type == Type.STRING:
            return Type.STRING
        
        return Type.NUMBER
    
    def analyze_unary(self, expr):
        """Analyze a unary expression."""
        right_type = self.analyze_expr(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            if right_type != Type.NUMBER:
                self.errors.append("Operand of negation must be a number.")
                return Type.UNDEFINED
            return Type.NUMBER
        
        if expr.operator.type == TokenType.NOT:
            return Type.BOOLEAN
        
        return Type.UNDEFINED
    
    def analyze_literal(self, expr):
        """Analyze a literal."""
        return Type.of(expr.value)
    
    def analyze_variable(self, expr):
        """Analyze a variable reference."""
        try:
            return self.environment.get(expr.name.lexeme)
        except SemanticError as error:
            self.errors.append(str(error))
            return Type.UNDEFINED
    
    def analyze_assign(self, expr):
        """Analyze an assignment."""
        value_type = self.analyze_expr(expr.value)
        
        try:
            # Check if variable exists
            self.environment.get(expr.name.lexeme)
            # Update variable
            self.environment.assign(expr.name.lexeme, value_type)
        except SemanticError as error:
            self.errors.append(str(error))
        
        return value_type
    
    def analyze_call(self, expr):
        """Analyze a function call."""
        callee_type = self.analyze_expr(expr.callee)
        
        # Check if callee is callable
        if callee_type != Type.FUNCTION and callee_type != Type.CLASS:
            self.errors.append(f"Can only call functions and classes, got {callee_type}.")
            return Type.UNDEFINED
        
        # Analyze arguments
        for arg in expr.arguments:
            self.analyze_expr(arg)
        
        # Function calls return a value, but we don't know the type statically
        return Type.UNDEFINED
    
    def analyze_get(self, expr):
        """Analyze a property access."""
        object_type = self.analyze_expr(expr.object)
        
        # Only objects have properties
        if object_type != Type.OBJECT:
            self.errors.append(f"Only objects have properties, got {object_type}.")
            return Type.UNDEFINED
        
        # Cannot determine property type statically
        return Type.UNDEFINED
    
    def analyze_lambda(self, expr):
        """Analyze a lambda expression."""
        # Create new environment for lambda body
        previous_env = self.environment
        self.environment = Environment(previous_env)
        
        # Define parameters in lambda scope
        for param in expr.params:
            self.environment.define(param.lexeme, Type.UNDEFINED)
        
        # Analyze lambda body
        self.analyze_expr(expr.body)
        
        # Restore environment
        self.environment = previous_env
        
        return Type.FUNCTION

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
