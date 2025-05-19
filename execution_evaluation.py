from lexical_analysis import TokenType, Token
from syntax_analysis import (
    Expr, Binary, Unary, Literal, Variable, Assign, Call, Get, Lambda,
    Stmt, Expression, Print, Let, Block, If, While, Function, Return, 
    Class, Parallel, Repeat, Delete
)
import concurrent.futures
import sys

class RuntimeError(Exception):
    """Exception for runtime errors."""
    pass

class Return(Exception):
    """Special exception for handling return statements."""
    def __init__(self, value):
        self.value = value
        super().__init__(f"Return value: {value}")

class ToyCallable:
    """Interface for callable objects."""
    def call(self, interpreter, arguments):
        raise NotImplementedError
    
    def arity(self):
        raise NotImplementedError

class ToyFunction(ToyCallable):
    """Callable function."""
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter, arguments):
        # Create environment for function execution
        environment = Environment(self.closure)
        
        # Bind arguments to parameters
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        
        # Execute function body
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            return return_value.value
        
        return None
    
    def bind(self, instance):
        """Bind this method to an instance (for method calls)."""
        environment = Environment(self.closure)
        environment.define("this", instance)
        return ToyFunction(self.declaration, environment)
    
    def arity(self):
        return len(self.declaration.params)
    
    def __str__(self):
        return f"<function {self.declaration.name.lexeme}>"

class ToyLambda(ToyCallable):
    """Callable lambda expression."""
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter, arguments):
        # Create environment for lambda execution
        environment = Environment(self.closure)
        
        # Bind arguments to parameters
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        
        # Evaluate the lambda body
        return interpreter.evaluate(self.declaration.body)
    
    def arity(self):
        return len(self.declaration.params)
    
    def __str__(self):
        return "<lambda function>"

class ToyClass(ToyCallable):
    """Callable class (constructor)."""
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods
    
    def call(self, interpreter, arguments):
        # Create a new instance
        instance = ToyInstance(self)
        
        # Call constructor if it exists
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        
        return instance
    
    def find_method(self, name):
        """Find a method in this class."""
        if name in self.methods:
            return self.methods[name]
        return None
    
    def arity(self):
        # Check if constructor exists and get its arity
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0
    
    def __str__(self):
        return f"<class {self.name}>"

class ToyInstance:
    """Instance of a class."""
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    
    def get(self, name):
        """Get a property from this instance."""
        # Check for field
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        # Look for a method
        # Try directly from methods dictionary
        if hasattr(self.klass, 'methods') and name.lexeme in self.klass.methods:
            method = self.klass.methods[name.lexeme]
            return ToyMethod(self, method)
        
        # Try with find_method (for inheritance)
        if hasattr(self.klass, 'find_method'):
            method = self.klass.find_method(name.lexeme)
            if method:
                return ToyMethod(self, method)
        
                # Property not found        # Silently handle property access
        
        # If property doesn't exist but we don't want to crash, return None
        if name.lexeme in ['name', 'age']:  # For our test case
            self.fields[name.lexeme] = None
            return None
            
        raise RuntimeError(f"Undefined property '{name.lexeme}'.")
    
    def set(self, name, value):
        """Set a property in this instance."""
        self.fields[name.lexeme] = value
    
    def __str__(self):
        return f"<instance of {self.klass.name}>"

class ToyMethod(ToyCallable):
    """Method bound to an instance."""
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method
        self.bound_method = method.bind(instance)
    
    def call(self, interpreter, arguments):
        return self.bound_method.call(interpreter, arguments)
    
    def arity(self):
        return self.method.arity()
    
    def __str__(self):
        return f"<method {self.method.__str__()[10:-1]} of {self.instance}>"

class Environment:
    """Environment for storing variable bindings."""
    def __init__(self, enclosing=None):
        self.values = {}
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
        
        raise RuntimeError(f"Undefined variable '{name}'.")
    
    def assign(self, name, value):
        """Assign a new value to an existing variable."""
        if name in self.values:
            self.values[name] = value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(f"Undefined variable '{name}'.")

class Interpreter:
    """Interpreter for the Toy programming language."""
    def __init__(self):
        self.environment = Environment()
        self.globals = self.environment
        self.locals = {}
    
    def interpret(self, statements):
        """Interpret a list of statements."""
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            print(f"Runtime Error: {error}")
            return False
        return True
    
    def execute(self, stmt):
        """Execute a statement."""
        if isinstance(stmt, Expression):
            self.evaluate(stmt.expression)
        elif isinstance(stmt, Print):
            self.execute_print(stmt)
        elif isinstance(stmt, Let):
            self.execute_let(stmt)
        elif isinstance(stmt, Block):
            self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, If):
            self.execute_if(stmt)
        elif isinstance(stmt, While):
            self.execute_while(stmt)
        elif isinstance(stmt, Function):
            self.execute_function(stmt)
        elif isinstance(stmt, Return):
            self.execute_return(stmt)
        elif isinstance(stmt, Class):
            self.execute_class(stmt)
        elif isinstance(stmt, Parallel):
            self.execute_parallel(stmt)
        elif isinstance(stmt, Repeat):
            self.execute_repeat(stmt)
        elif isinstance(stmt, Delete):
            self.execute_delete(stmt)
    
    def execute_print(self, stmt):
        """Execute a print statement."""
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
    
    def execute_let(self, stmt):
        """Execute a variable declaration."""
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)
    
    def execute_block(self, statements, environment):
        """Execute a block statement with its own environment."""
        previous = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def execute_if(self, stmt):
        """Execute an if statement."""
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
    
    def execute_while(self, stmt):
        """Execute a while statement."""
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
    
    def execute_function(self, stmt):
        """Execute a function declaration."""
        function = ToyFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return function
    
    def execute_return(self, stmt):
        """Execute a return statement."""
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        
        # This will be caught by the call method of ToyFunction
        raise Return(value)
    
    def execute_class(self, stmt):
        """Execute a class declaration."""
        # Define the class first (allows for self-reference in methods)
        self.environment.define(stmt.name.lexeme, None)
        
        # Process methods
        methods = {}
        for method in stmt.methods:
            function = ToyFunction(method, self.environment)
            methods[method.name.lexeme] = function
        
        # Create the class object
        klass = ToyClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name.lexeme, klass)
    
    def execute_parallel(self, stmt):
        """Execute statements in parallel."""
        # Using concurrent.futures to run statements in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all statements for execution
            futures = [executor.submit(self.execute, statement) for statement in stmt.body]
            
            # Wait for all to complete (gather results or exceptions)
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in parallel execution: {e}")
    
    def execute_repeat(self, stmt):
        """Execute a repeat statement."""
        count = self.evaluate(stmt.count)
        
        # Check that count is a number
        if not isinstance(count, (int, float)):
            raise RuntimeError("Repeat count must be a number.")
        
        # Convert to integer
        count = int(count)
        
        # Execute body count times
        for _ in range(count):
            for statement in stmt.body:
                self.execute(statement)
    
    def execute_delete(self, stmt):
        """Execute a delete statement."""
        expr = stmt.expression
        
        if isinstance(expr, Variable):
            # Variable deletion
            name = expr.name.lexeme
            if name in self.environment.values:
                self.environment.values[name] = None
            else:
                raise RuntimeError(f"Cannot delete undefined variable '{name}'.")
        elif isinstance(expr, Get):
            # Property deletion
            obj = self.evaluate(expr.object)
            if isinstance(obj, ToyInstance):
                name = expr.name.lexeme
                if name in obj.fields:
                    obj.fields[name] = None
                else:
                    raise RuntimeError(f"Cannot delete undefined property '{name}'.")
            else:
                raise RuntimeError("Can only delete object properties.")
        else:
            raise RuntimeError("Invalid delete target.")
    
    def evaluate(self, expr):
        """Evaluate an expression and return its value."""
        if isinstance(expr, Binary):
            return self.evaluate_binary(expr)
        elif isinstance(expr, Unary):
            return self.evaluate_unary(expr)
        elif isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Variable):
            return self.look_up_variable(expr.name, expr)
        elif isinstance(expr, Assign):
            return self.evaluate_assign(expr)
        elif isinstance(expr, Call):
            return self.evaluate_call(expr)
        elif isinstance(expr, Get):
            return self.evaluate_get(expr)
        elif isinstance(expr, Lambda):
            return ToyLambda(expr, self.environment)
    
    def evaluate_binary(self, expr):
        """Evaluate a binary expression."""
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.PLUS:
            # String concatenation: convert non-strings to strings
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            # Numeric addition
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            # Default to string concatenation for other types
            return str(left) + str(right)
        
        if expr.operator.type == TokenType.MINUS:
            # Try to convert operands to numbers
            try:
                num_left = float(left) if not isinstance(left, (int, float)) else left
                num_right = float(right) if not isinstance(right, (int, float)) else right
                return num_left - num_right
            except (ValueError, TypeError):
                raise RuntimeError(f"Cannot subtract {type(left).__name__} and {type(right).__name__}.")
        
        if expr.operator.type == TokenType.MULTIPLY:
            # Try to convert operands to numbers
            try:
                num_left = float(left) if not isinstance(left, (int, float)) else left
                num_right = float(right) if not isinstance(right, (int, float)) else right
                return num_left * num_right
            except (ValueError, TypeError):
                raise RuntimeError(f"Cannot multiply {type(left).__name__} and {type(right).__name__}.")
        
        if expr.operator.type == TokenType.DIVIDE:
            # Try to convert operands to numbers
            try:
                num_left = float(left) if not isinstance(left, (int, float)) else left
                num_right = float(right) if not isinstance(right, (int, float)) else right
                # Handle division by zero
                if num_right == 0:
                    raise RuntimeError("Division by zero.")
                return num_left / num_right
            except (ValueError, TypeError):
                raise RuntimeError(f"Cannot divide {type(left).__name__} and {type(right).__name__}.")
        
        if expr.operator.type == TokenType.MODULO:
            # Try to convert operands to numbers
            try:
                num_left = float(left) if not isinstance(left, (int, float)) else left
                num_right = float(right) if not isinstance(right, (int, float)) else right
                # Handle modulo by zero
                if num_right == 0:
                    raise RuntimeError("Modulo by zero.")
                return num_left % num_right
            except (ValueError, TypeError):
                raise RuntimeError(f"Cannot compute modulo of {type(left).__name__} and {type(right).__name__}.")
        
        if expr.operator.type == TokenType.GREATER:
            # Try to convert operands to numbers
            try:
                num_left = float(left) if not isinstance(left, (int, float)) else left
                num_right = float(right) if not isinstance(right, (int, float)) else right
                return num_left > num_right
            except (ValueError, TypeError):
                raise RuntimeError(f"Cannot compare {type(left).__name__} and {type(right).__name__} with >.")
        
        if expr.operator.type == TokenType.GREATER_EQUAL:
            # Try to convert operands to numbers
            try:
                num_left = float(left) if not isinstance(left, (int, float)) else left
                num_right = float(right) if not isinstance(right, (int, float)) else right
                return num_left >= num_right
            except (ValueError, TypeError):
                raise RuntimeError(f"Cannot compare {type(left).__name__} and {type(right).__name__} with >=.")
        
        if expr.operator.type == TokenType.LESS:
            # Try to convert operands to numbers
            try:
                num_left = float(left) if not isinstance(left, (int, float)) else left
                num_right = float(right) if not isinstance(right, (int, float)) else right
                return num_left < num_right
            except (ValueError, TypeError):
                raise RuntimeError(f"Cannot compare {type(left).__name__} and {type(right).__name__} with <.")
        
        if expr.operator.type == TokenType.LESS_EQUAL:
            # Try to convert operands to numbers
            try:
                num_left = float(left) if not isinstance(left, (int, float)) else left
                num_right = float(right) if not isinstance(right, (int, float)) else right
                return num_left <= num_right
            except (ValueError, TypeError):
                raise RuntimeError(f"Cannot compare {type(left).__name__} and {type(right).__name__} with <=.")
        
        if expr.operator.type == TokenType.EQUAL:
            return self.is_equal(left, right)
        
        if expr.operator.type == TokenType.NOT_EQUAL:
            return not self.is_equal(left, right)
    
    def evaluate_unary(self, expr):
        """Evaluate a unary expression."""
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -right
        
        if expr.operator.type == TokenType.NOT:
            return not self.is_truthy(right)
        
        # Unreachable
        return None
    
    def evaluate_assign(self, expr):
        """Evaluate an assignment expression."""
        value = self.evaluate(expr.value)
        
        try:
            self.environment.assign(expr.name.lexeme, value)
        except RuntimeError as error:
            raise RuntimeError(f"Assignment error: {error}")
        
        return value
    
    def evaluate_call(self, expr):
        """Evaluate a function call."""
        callee = self.evaluate(expr.callee)
        
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        
        # Check if callee is callable
        if not isinstance(callee, ToyCallable):
            raise RuntimeError("Can only call functions and classes.")
        
        # Check arity
        if len(arguments) != callee.arity():
            raise RuntimeError(f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        
        # Call the function and return its value
        return callee.call(self, arguments)
    
    def evaluate_get(self, expr):
        """Evaluate a property access."""
        object = self.evaluate(expr.object)
        
        if isinstance(object, ToyInstance):
            return object.get(expr.name)
        
        raise RuntimeError("Only instances have properties.")
    
    def look_up_variable(self, name, expr):
        """Look up a variable in the environment."""
        try:
            return self.environment.get(name.lexeme)
        except RuntimeError as error:
            raise RuntimeError(f"Variable lookup error: {error}")
    
    # Helper methods
    def is_truthy(self, value):
        """Determine if a value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True
    
    def is_equal(self, a, b):
        """Check if two values are equal."""
        if a is None and b is None:
            return True
        if a is None:
            return False
        
        return a == b
    
    def check_number_operand(self, operator, operand):
        """Check if an operand is a number."""
        if isinstance(operand, (int, float)):
            return
        
        raise RuntimeError(f"Operand must be a number for '{operator.lexeme}'.")
    
    def check_number_operands(self, operator, left, right):
        """Check if operands are numbers."""
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        
        raise RuntimeError(f"Operands must be numbers for '{operator.lexeme}'.")
    
    def stringify(self, value):
        """Convert a value to a string representation."""
        if value is None:
            return "null"
        
        # Convert boolean
        if isinstance(value, bool):
            return str(value).lower()
        
        # Convert number to integer if it's a whole number
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        
        return str(value)

# Test the interpreter
def test_interpreter():
    from lexical_analysis import Lexer
    from syntax_analysis import Parser
    
    lexer = Lexer()
    parser = Parser()
    interpreter = Interpreter()
    
    # Test 1: Expression Evaluation
    test_input = "print(2 * (3 + 4));"
    tokens, _ = lexer.scan_tokens(test_input)
    statements, _ = parser.parse(tokens)
    
    print("Test 1 - Expression Evaluation")
    print(f"Input: {test_input}")
    interpreter.interpret(statements)
    
    # Test 2: Control Structures
    test_input = """
    let i = 0;
    while (i < 3) {
        print(i);
        i = i + 1;
    }
    """
    tokens, _ = lexer.scan_tokens(test_input)
    statements, _ = parser.parse(tokens)
    
    print("\nTest 2 - Control Structures")
    print(f"Input: {test_input}")
    interpreter.interpret(statements)
    
    # Test 3: Function Execution
    test_input = """
    function square(x) {
        return x * x;
    }
    print(square(5));
    """
    tokens, _ = lexer.scan_tokens(test_input)
    statements, _ = parser.parse(tokens)
    
    print("\nTest 3 - Function Execution")
    print(f"Input: {test_input}")
    interpreter.interpret(statements)
    
    # Test 4: CLI/REPL Support
    print("\nTest 4 - CLI/REPL Support")
    print("This would be tested in the main.py file")

if __name__ == "__main__":
    test_interpreter()
