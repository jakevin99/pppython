import importlib
import inspect
import pkgutil
import sys
from execution_evaluation import ToyCallable, Environment

# This file implements extensibility features that allow adding new functionality
# to the language through plugins and external libraries.

class ToyExtensionManager:
    """Manager for language extensions and plugins."""
    def __init__(self):
        self.extensions = {}  # Map of extension name to extension object
        self.global_environment = None  # Reference to global environment
    
    def set_environment(self, env):
        """Set the global environment for the extensions."""
        self.global_environment = env
    
    def register_extension(self, name, extension):
        """Register an extension with the language."""
        self.extensions[name] = extension
        
        # If we have a global environment, add functions to it
        if self.global_environment and hasattr(extension, 'get_functions'):
            for func_name, func in extension.get_functions().items():
                # Wrap the function in a ToyCallable
                toy_func = ToyExtensionFunction(func_name, func)
                self.global_environment.define(func_name, toy_func)
    
    def load_extension_from_module(self, module_name):
        """Load an extension from a Python module."""
        try:
            module = importlib.import_module(module_name)
            
            # Look for a class that implements ToyExtension
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'get_functions'):
                    extension = obj()
                    self.register_extension(name, extension)
                    return extension
            
            raise ValueError(f"No valid extension found in module {module_name}")
        
        except ImportError as e:
            print(f"Error loading extension {module_name}: {e}")
            return None
    
    def discover_extensions(self, package_name):
        """Discover all extensions in a package."""
        try:
            package = importlib.import_module(package_name)
            count = 0
            
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                if not is_pkg:  # Only process modules, not sub-packages
                    extension = self.load_extension_from_module(name)
                    if extension:
                        count += 1
            
            return count
        except ImportError as e:
            print(f"Error discovering extensions in {package_name}: {e}")
            return 0
    
    def get_extension(self, name):
        """Get an extension by name."""
        return self.extensions.get(name)
    
    def list_extensions(self):
        """List all registered extensions."""
        return list(self.extensions.keys())

class ToyExtension:
    """Base class for Toy language extensions."""
    def get_functions(self):
        """Get a dictionary of functions provided by this extension."""
        return {}
    
    def get_name(self):
        """Get the name of this extension."""
        return self.__class__.__name__

class ToyExtensionFunction(ToyCallable):
    """Wrapper for functions provided by extensions."""
    def __init__(self, name, func):
        self.name = name
        self.func = func
        # Get the number of required arguments
        signature = inspect.signature(func)
        self.required_args = len([p for p in signature.parameters.values() 
                               if p.default == inspect.Parameter.empty])
    
    def call(self, interpreter, arguments):
        """Call the wrapped function."""
        return self.func(*arguments)
    
    def arity(self):
        """Get the number of required arguments."""
        return self.required_args
    
    def __str__(self):
        return f"<extension function {self.name}>"

# Example extension implementation
class MathExtension(ToyExtension):
    """Example extension that provides math functions."""
    def get_functions(self):
        return {
            "math_pow": self.pow,
            "math_sqrt": self.sqrt,
            "math_abs": self.abs
        }
    
    def pow(self, base, exponent):
        """Calculate base raised to the power of exponent."""
        return base ** exponent
    
    def sqrt(self, x):
        """Calculate the square root of x."""
        return x ** 0.5
    
    def abs(self, x):
        """Calculate the absolute value of x."""
        return abs(x)

class StringExtension(ToyExtension):
    """Example extension that provides string functions."""
    def get_functions(self):
        return {
            "string_length": self.length,
            "string_contains": self.contains,
            "string_replace": self.replace
        }
    
    def length(self, s):
        """Get the length of a string."""
        return len(s)
    
    def contains(self, s, substr):
        """Check if a string contains a substring."""
        return substr in s
    
    def replace(self, s, old, new):
        """Replace occurrences of old with new in s."""
        return s.replace(old, new)

# Example of using extensions
def test_extensibility():
    print("Testing Extensibility Features:")
    
    # Create environment and extension manager
    env = Environment()
    manager = ToyExtensionManager()
    manager.set_environment(env)
    
    # Register extensions
    math_ext = MathExtension()
    string_ext = StringExtension()
    
    manager.register_extension("math", math_ext)
    manager.register_extension("string", string_ext)
    
    # List extensions
    print(f"Registered extensions: {manager.list_extensions()}")
    
    # Test extension functions
    if "math" in manager.list_extensions():
        math_pow = env.get("math_pow")
        print(f"math_pow(2, 3) = {math_pow.call(None, [2, 3])}")
    
    if "string" in manager.list_extensions():
        string_length = env.get("string_length")
        string_contains = env.get("string_contains")
        
        print(f"string_length(\"hello\") = {string_length.call(None, ['hello'])}")
        print(f"string_contains(\"hello world\", \"world\") = {string_contains.call(None, ['hello world', 'world'])}")
    
    # Repeat syntax example
    print("\nRepeat syntax example:")
    print("repeat 3 times {")
    print("  print(\"Hi\");")
    print("}")
    
    # Simulate output
    for _ in range(3):
        print("Hi")

if __name__ == "__main__":
    test_extensibility()
