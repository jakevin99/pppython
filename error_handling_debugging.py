from lexical_analysis import Token
import sys
import traceback

class ErrorReporter:
    """Error reporting system for the interpreter."""
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
    
    def reset(self):
        """Reset error flags."""
        self.had_error = False
        self.had_runtime_error = False
    
    def report(self, line, where, message):
        """Report a generic error."""
        error_msg = f"[line {line}] Error {where}: {message}"
        print(error_msg, file=sys.stderr)
        self.had_error = True
    
    def error(self, token, message):
        """Report an error at a specific token."""
        if token.type == "EOF":
            self.report(token.line, "at end", message)
        else:
            self.report(token.line, f"at '{token.lexeme}'", message)
    
    def runtime_error(self, error, line=None):
        """Report a runtime error."""
        if line:
            error_msg = f"[line {line}] Runtime Error: {error}"
        else:
            error_msg = f"Runtime Error: {error}"
        
        print(error_msg, file=sys.stderr)
        self.had_runtime_error = True

class DebugInfo:
    """Debugging information for error reporting."""
    def __init__(self, source=None):
        self.source = source
        self.source_lines = source.split('\n') if source else []
    
    def get_line_content(self, line):
        """Get the content of a specific line."""
        if 0 <= line - 1 < len(self.source_lines):
            return self.source_lines[line - 1]
        return "<line not available>"

class Debugger:
    """Debugger for the language interpreter."""
    def __init__(self, error_reporter):
        self.error_reporter = error_reporter
        self.debug_info = None
        self.debug_mode = False
        self.breakpoints = set()
        self.step_mode = False
        self.call_stack = []
    
    def set_source(self, source):
        """Set the source code for debugging."""
        self.debug_info = DebugInfo(source)
    
    def set_debug_mode(self, enabled):
        """Enable or disable debug mode."""
        self.debug_mode = enabled
    
    def add_breakpoint(self, line):
        """Add a breakpoint at a specific line."""
        self.breakpoints.add(line)
    
    def remove_breakpoint(self, line):
        """Remove a breakpoint from a specific line."""
        if line in self.breakpoints:
            self.breakpoints.remove(line)
    
    def clear_breakpoints(self):
        """Clear all breakpoints."""
        self.breakpoints.clear()
    
    def enter_step_mode(self):
        """Enter step-by-step execution mode."""
        self.step_mode = True
    
    def exit_step_mode(self):
        """Exit step-by-step execution mode."""
        self.step_mode = False
    
    def push_call(self, function_name, line):
        """Push a function call onto the call stack."""
        self.call_stack.append((function_name, line))
    
    def pop_call(self):
        """Pop a function call from the call stack."""
        if self.call_stack:
            return self.call_stack.pop()
        return None
    
    def print_stack_trace(self):
        """Print the current call stack."""
        print("Stack trace:")
        for i, (name, line) in enumerate(reversed(self.call_stack)):
            print(f"  {i}: {name} (line {line})")
    
    def handle_breakpoint(self, line):
        """Handle execution when a breakpoint is hit."""
        if not self.debug_mode:
            return
        
        if line in self.breakpoints or self.step_mode:
            print(f"\nBreakpoint hit at line {line}:")
            if self.debug_info:
                print(f"  {self.debug_info.get_line_content(line)}")
            
            self.print_stack_trace()
            
            # Wait for user input
            while True:
                command = input("Debug [c=continue, s=step, q=quit, p=print stack]: ")
                if command == 'c':
                    self.step_mode = False
                    break
                elif command == 's':
                    self.step_mode = True
                    break
                elif command == 'q':
                    sys.exit(0)
                elif command == 'p':
                    self.print_stack_trace()
                else:
                    print("Unknown command")

class ErrorHandler:
    """Centralized error handling."""
    def __init__(self):
        self.reporter = ErrorReporter()
        self.debugger = Debugger(self.reporter)
    
    def handle_syntax_error(self, token, message):
        """Handle a syntax error."""
        self.reporter.error(token, message)
        
        # Show context in debug mode
        if self.debugger.debug_mode and self.debugger.debug_info:
            print(f"Context: {self.debugger.debug_info.get_line_content(token.line)}")
    
    def handle_runtime_error(self, error, line=None):
        """Handle a runtime error."""
        self.reporter.runtime_error(error, line)
        
        # Show stack trace in debug mode
        if self.debugger.debug_mode:
            self.debugger.print_stack_trace()
    
    def handle_division_by_zero(self, line=None):
        """Handle a division by zero error."""
        self.handle_runtime_error("Division by zero", line)
    
    def handle_type_error(self, expected, got, line=None):
        """Handle a type error."""
        self.handle_runtime_error(f"Type error: expected {expected}, got {got}", line)

def test_error_handling():
    error_handler = ErrorHandler()
    
    # Test 1: Runtime Errors
    print("Test 1 - Runtime Errors")
    try:
        x = 10
        y = 0
        result = x / y  # This will cause a division by zero
    except ZeroDivisionError:
        error_handler.handle_division_by_zero(line=3)
    
    # Test 2: Debugging Feedback
    print("\nTest 2 - Debugging Feedback")
    
    # Create a fake token for testing
    class FakeToken:
        def __init__(self, type, lexeme, line):
            self.type = type
            self.lexeme = lexeme
            self.line = line
    
    token = FakeToken("PLUS", "+", 5)
    error_handler.debugger.set_source("let x = \"hi\" + 5;")
    error_handler.handle_syntax_error(token, "Cannot add string and number")

if __name__ == "__main__":
    test_error_handling()
