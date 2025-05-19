from execution_evaluation import ToyInstance, ToyClass, ToyMethod, ToyCallable

# This file extends the OOP capabilities of the language by adding inheritance,
# access modifiers, and other OOP features not in the core implementation.

class ToyInheritance:
    """Utility class for handling inheritance in Toy language."""
    @staticmethod
    def find_method(instance, name):
        """Find a method in the inheritance chain."""
        method = instance.klass.find_method(name)
        if method:
            return method.bind(instance)
        
        # Check superclass if it exists
        if hasattr(instance.klass, 'superclass') and instance.klass.superclass:
            # Create a temporary instance of the superclass
            super_instance = ToyInstance(instance.klass.superclass)
            super_instance.fields = instance.fields  # Share fields
            
            return ToyInheritance.find_method(super_instance, name)
        
        return None

class ToyClassWithInheritance(ToyClass):
    """Extended class definition with inheritance support."""
    def __init__(self, name, methods, superclass=None):
        super().__init__(name, methods)
        self.superclass = superclass
    
    def find_method(self, name):
        """Find a method in this class or its superclass."""
        # Check in this class first
        if name in self.methods:
            return self.methods[name]
        
        # Check superclass if it exists
        if self.superclass:
            return self.superclass.find_method(name)
        
        return None

class ToyInstanceWithAccess(ToyInstance):
    """Extended instance with access control modifiers."""
    def __init__(self, klass):
        super().__init__(klass)
        self.private_fields = {}  # Private fields
        self.protected_fields = {}  # Protected fields
    
    def get(self, name):
        """Get a property with access control."""
        # Check if this is an access to a field
        field_name = name.lexeme
        
        # Public field access
        if field_name in self.fields:
            return self.fields[field_name]
        
        # Private field access (only allowed from methods of the same class)
        if field_name.startswith('_') and field_name in self.private_fields:
            # Would check if access is from the same class here
            # For simplicity, we'll allow access for demonstration
            return self.private_fields[field_name]
        
        # Protected field access (allowed from subclasses)
        if field_name.startswith('_') and field_name in self.protected_fields:
            # Would check if access is from a subclass here
            return self.protected_fields[field_name]
        
        # Look for a method
        method = self.klass.find_method(field_name)
        if method:
            return method.bind(self)
        
        raise RuntimeError(f"Undefined property '{field_name}'.")
    
    def set(self, name, value):
        """Set a property with access control."""
        field_name = name.lexeme
        
        # Private field assignment
        if field_name.startswith('__'):
            self.private_fields[field_name] = value
            return
        
        # Protected field assignment
        if field_name.startswith('_'):
            self.protected_fields[field_name] = value
            return
        
        # Public field assignment
        self.fields[field_name] = value

# Example of using the OOP features
def test_oop():
    # Define a parent class
    parent_methods = {
        "greet": lambda self: print("Hello from parent")
    }
    parent_class = ToyClassWithInheritance("Parent", parent_methods)
    
    # Define a child class that inherits from parent
    child_methods = {
        "greet": lambda self: print("Hello from child")
    }
    child_class = ToyClassWithInheritance("Child", child_methods, parent_class)
    
    # Create instances
    parent_instance = ToyInstanceWithAccess(parent_class)
    child_instance = ToyInstanceWithAccess(child_class)
    
    # Test method calls
    print("Testing OOP features:")
    parent_instance.get("greet")().call(None, [])
    child_instance.get("greet")().call(None, [])
    
    # Test access modifiers
    parent_instance.set("public_field", "Public value")
    parent_instance.set("_protected_field", "Protected value")
    parent_instance.set("__private_field", "Private value")
    
    print(f"Public field: {parent_instance.get('public_field')}")
    print(f"Protected field: {parent_instance.get('_protected_field')}")
    print(f"Private field: {parent_instance.get('__private_field')}")

if __name__ == "__main__":
    test_oop()
