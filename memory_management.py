from execution_evaluation import Environment, RuntimeError

class MemoryManager:
    """Memory manager for tracking variable lifecycle and garbage collection."""
    def __init__(self):
        self.objects = {}  # Maps object ID to object
        self.reference_counts = {}  # Maps object ID to reference count
        self.deleted_objects = set()  # Set of deleted object IDs
    
    def allocate(self, value):
        """Allocate memory for a value and return a reference."""
        obj_id = id(value)
        
        # If object already exists, increment reference count
        if obj_id in self.reference_counts:
            self.reference_counts[obj_id] += 1
        else:
            # Otherwise, add new object
            self.objects[obj_id] = value
            self.reference_counts[obj_id] = 1
        
        return obj_id
    
    def assign(self, var_id, value):
        """Assign a value to a variable."""
        # Decrease reference count for old value
        if var_id in self.objects:
            old_value_id = id(self.objects[var_id])
            self.reference_counts[old_value_id] -= 1
            
            # Collect if reference count drops to zero
            if self.reference_counts[old_value_id] == 0:
                del self.objects[old_value_id]
                del self.reference_counts[old_value_id]
        
        # Store new value
        self.objects[var_id] = value
        
        # Increment reference count for new value
        value_id = id(value)
        if value_id in self.reference_counts:
            self.reference_counts[value_id] += 1
        else:
            self.reference_counts[value_id] = 1
    
    def delete(self, var_id):
        """Delete a variable."""
        if var_id not in self.objects:
            raise RuntimeError(f"Cannot delete non-existent variable.")
        
        # Get value ID
        value_id = id(self.objects[var_id])
        
        # Decrease reference count
        self.reference_counts[value_id] -= 1
        
        # Collect if reference count drops to zero
        if self.reference_counts[value_id] == 0:
            del self.objects[value_id]
            del self.reference_counts[value_id]
        
        # Mark as deleted
        self.deleted_objects.add(var_id)
        del self.objects[var_id]
    
    def is_deleted(self, var_id):
        """Check if a variable has been deleted."""
        return var_id in self.deleted_objects
    
    def collect_garbage(self):
        """Perform garbage collection to free unreferenced objects."""
        # Find objects with zero references
        to_delete = []
        for obj_id, count in self.reference_counts.items():
            if count <= 0:
                to_delete.append(obj_id)
        
        # Remove them
        for obj_id in to_delete:
            if obj_id in self.objects:
                del self.objects[obj_id]
            del self.reference_counts[obj_id]
        
        return len(to_delete)

class EnhancedEnvironment(Environment):
    """Environment with memory management capabilities."""
    def __init__(self, enclosing=None):
        super().__init__(enclosing)
        self.memory_manager = MemoryManager()
    
    def define(self, name, value):
        """Define a new variable with memory management."""
        # Store the value and track it
        super().define(name, value)
        self.memory_manager.allocate(value)
    
    def assign(self, name, value):
        """Assign a new value with memory management."""
        # Check if variable exists
        if name in self.values:
            # Track the assignment
            self.memory_manager.assign(id(name), value)
            super().assign(name, value)
            return
        
        if self.enclosing is not None:
            if isinstance(self.enclosing, EnhancedEnvironment):
                self.enclosing.assign(name, value)
            else:
                super().assign(name, value)
            return
        
        raise RuntimeError(f"Undefined variable '{name}'.")
    
    def delete(self, name):
        """Delete a variable from the environment."""
        if name in self.values:
            # Remove from memory manager
            self.memory_manager.delete(id(name))
            # Remove from environment
            del self.values[name]
            return
        
        if self.enclosing is not None:
            if isinstance(self.enclosing, EnhancedEnvironment):
                self.enclosing.delete(name)
                return
        
        raise RuntimeError(f"Cannot delete undefined variable '{name}'.")
    
    def get(self, name):
        """Get a variable value with deletion check."""
        # Check if the variable exists and hasn't been deleted
        if name in self.values:
            if not self.memory_manager.is_deleted(id(name)):
                return super().get(name)
            else:
                raise RuntimeError(f"Access to deleted variable '{name}'.")
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise RuntimeError(f"Undefined variable '{name}'.")
    
    def collect_garbage(self):
        """Run garbage collection."""
        return self.memory_manager.collect_garbage()

# Test memory management
def test_memory_management():
    env = EnhancedEnvironment()
    
    # Test 1: Variable Lifecycle
    print("Test 1 - Variable Lifecycle")
    env.define("x", 5)
    print(f"Original value: {env.get('x')}")
    
    env.assign("x", 6)
    print(f"Updated value: {env.get('x')}")
    
    # Test 2: GC / Manual Memory Handling
    print("\nTest 2 - GC / Manual Memory Handling")
    env.define("array", [1, 2, 3])
    print(f"Original array: {env.get('array')}")
    
    env.assign("array", None)  # Set to null
    count = env.collect_garbage()
    print(f"Collected {count} objects during garbage collection")
    
    # Test 3: Access to Deleted Object
    print("\nTest 3 - Access to Deleted Object")
    try:
        env.define("obj", {"data": "test"})
        env.delete("obj")
        print(f"Trying to access deleted object: {env.get('obj')}")
    except RuntimeError as error:
        print(f"Error (expected): {error}")

if __name__ == "__main__":
    test_memory_management()
