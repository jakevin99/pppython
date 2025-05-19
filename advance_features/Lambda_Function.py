from execution_evaluation import ToyLambda, ToyCallable, Environment

# This file extends the lambda function capabilities of the language,
# providing more advanced features like closures and higher-order functions.

class ToyClosureLambda(ToyLambda):
    """Lambda with enhanced closure capabilities."""
    def __init__(self, declaration, closure):
        super().__init__(declaration, closure)
        # Capture the variables currently available for closure
        self.captured_vars = {}
        if hasattr(closure, 'values'):
            self.captured_vars = closure.values.copy()
    
    def call(self, interpreter, arguments):
        """Call the lambda with closure support."""
        # Create environment for lambda execution
        environment = Environment(self.closure)
        
        # Add captured variables to the environment
        for name, value in self.captured_vars.items():
            environment.define(name, value)
        
        # Bind arguments to parameters
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        
        # Evaluate the lambda body
        return interpreter.evaluate(self.declaration.body)

class ToyPartialApplication:
    """Support for partial application of functions."""
    @staticmethod
    def partial(func, *fixed_args):
        """Create a new function with some arguments fixed."""
        def new_func(*args):
            # Combine fixed arguments with new arguments
            combined_args = list(fixed_args) + list(args)
            return func.call(None, combined_args)
        
        return new_func

class ToyComposition:
    """Support for function composition."""
    @staticmethod
    def compose(f, g):
        """Compose two functions: f(g(x))."""
        def composed(*args):
            # Apply g, then apply f to the result
            g_result = g.call(None, args)
            return f.call(None, [g_result])
        
        return composed

class ToyHigherOrderFunctions:
    """Collection of common higher-order functions."""
    @staticmethod
    def map(func, items):
        """Apply func to each item in items."""
        return [func.call(None, [item]) for item in items]
    
    @staticmethod
    def filter(func, items):
        """Keep only items for which func returns true."""
        return [item for item in items if func.call(None, [item])]
    
    @staticmethod
    def reduce(func, items, initial):
        """Reduce items to a single value using func and initial value."""
        result = initial
        for item in items:
            result = func.call(None, [result, item])
        return result

# Example of using lambda functions
def test_lambda_functions():
    print("Testing Lambda Functions:")
    
    # Create a simple lambda that adds two numbers
    class SimpleAddLambda(ToyCallable):
        def call(self, interpreter, arguments):
            return arguments[0] + arguments[1]
        
        def arity(self):
            return 2
        
        def __str__(self):
            return "<lambda: add>"
    
    add = SimpleAddLambda()
    print(f"add(2, 3) = {add.call(None, [2, 3])}")
    
    # Demonstrate partial application
    add_five = ToyPartialApplication.partial(add, 5)
    print(f"add_five(10) = {add_five(10)}")
    
    # Demonstrate composition
    class SquareLambda(ToyCallable):
        def call(self, interpreter, arguments):
            return arguments[0] * arguments[0]
        
        def arity(self):
            return 1
        
        def __str__(self):
            return "<lambda: square>"
    
    square = SquareLambda()
    
    # Create a function that squares a number and then adds 5
    square_then_add_five = ToyComposition.compose(
        lambda x: add.call(None, [x, 5]), 
        lambda x: square.call(None, [x])
    )
    
    print(f"square_then_add_five(3) = {square_then_add_five(3)}")  # (3*3) + 5 = 14
    
    # Demonstrate higher-order functions
    numbers = [1, 2, 3, 4, 5]
    
    # Map: square each number
    squared = ToyHigherOrderFunctions.map(square, numbers)
    print(f"map(square, [1,2,3,4,5]) = {squared}")
    
    # Filter: keep only even numbers
    class IsEvenLambda(ToyCallable):
        def call(self, interpreter, arguments):
            return arguments[0] % 2 == 0
        
        def arity(self):
            return 1
        
        def __str__(self):
            return "<lambda: is_even>"
    
    is_even = IsEvenLambda()
    evens = ToyHigherOrderFunctions.filter(is_even, numbers)
    print(f"filter(is_even, [1,2,3,4,5]) = {evens}")
    
    # Reduce: sum all numbers
    sum_result = ToyHigherOrderFunctions.reduce(add, numbers, 0)
    print(f"reduce(add, [1,2,3,4,5], 0) = {sum_result}")

if __name__ == "__main__":
    test_lambda_functions()
