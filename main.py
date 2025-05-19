#!/usr/bin/env python3
import sys
import os
import argparse
from lexical_analysis import Lexer
from syntax_analysis import Parser
from semantic_analysis import SemanticAnalyzer
from execution_evaluation import Interpreter
from error_handling_debugging import ErrorHandler
from user_interface_CLI import ToyLanguageCLI
from advance_features.OOP import ToyClassWithInheritance, ToyInstanceWithAccess
from advance_features.Lambda_Function import ToyClosureLambda, ToyHigherOrderFunctions
from advance_features.Concurrency_Async import ToyThread, ToyConcurrentExecutor, ToyAsync
from advance_features.Extensibility import ToyExtensionManager, MathExtension, StringExtension

VERSION = "1.0.0"

def print_banner():
    """Print a welcome banner for the Toy language."""
    banner = f"""
    ╔════════════════════════════════════════════════╗
    ║               TOY LANGUAGE v{VERSION}                ║
    ╚════════════════════════════════════════════════╝
    
    A simple, extensible programming language interpreter
    """
    print(banner)

def add_built_in_extensions(cli):
    """Add built-in extensions to the interpreter."""
    # Create an extension manager
    extension_manager = ToyExtensionManager()
    extension_manager.set_environment(cli.interpreter.globals)
    
    # Register built-in extensions
    extension_manager.register_extension("math", MathExtension())
    extension_manager.register_extension("string", StringExtension())
    
    # Return the manager so it can be used later
    return extension_manager

def main():
    """Main entry point for the Toy language interpreter."""
    parser = argparse.ArgumentParser(
        description="Toy Programming Language Interpreter",
        epilog="For more information, visit: https://github.com/yourusername/toy-language"
    )
    
    # Command-line arguments
    parser.add_argument("file", nargs="?", help="Script file to execute")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--version", action="version", version=f"Toy Language v{VERSION}")
    parser.add_argument("--interactive", action="store_true", help="Start interactive REPL after running script")
    parser.add_argument("--examples", action="store_true", help="Show example programs")
    
    args = parser.parse_args()
    
    # Show banner for interactive mode or when requested with --examples
    if args.interactive or not args.file or args.examples:
        print_banner()
    
    # Show examples if requested
    if args.examples:
        show_examples()
        return
    
    # Create CLI instance
    cli = ToyLanguageCLI()
    cli.set_verbose(args.verbose)
    
    # Set debug mode if requested
    if args.debug:
        cli.error_handler.debugger.set_debug_mode(True)
    
    # Add built-in extensions
    extension_manager = add_built_in_extensions(cli)
    
    # Run file if provided
    if args.file:
        try:
            cli.run_file(args.file)
        except Exception as e:
            print(f"Error running file: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    # Start REPL if interactive mode or no file provided
    if args.interactive or not args.file:
        cli.run_repl()

def show_examples():
    """Show example Toy language programs."""
    examples = [
        ("Hello World", """
// Hello World example
print("Hello, World!");
"""),
        ("Variables and Arithmetic", """
// Variables and arithmetic
let x = 10;
let y = 5;
print("x + y = " + (x + y));
print("x - y = " + (x - y));
print("x * y = " + (x * y));
print("x / y = " + (x / y));
"""),
        ("Control Flow", """
// Control flow with if/else
let x = 10;
if (x > 5) {
    print("x is greater than 5");
} else {
    print("x is not greater than 5");
}

// Loop with while
let i = 0;
while (i < 3) {
    print("i = " + i);
    i = i + 1;
}
"""),
        ("Functions", """
// Function declaration and calling
function add(a, b) {
    return a + b;
}

let result = add(5, 3);
print("5 + 3 = " + result);

// Lambda function
let square = (x) => x * x;
print("square(4) = " + square(4));
"""),
        ("Object-Oriented Programming", """
// Class definition
class Person {
    greet() {
        print("Hello, my name is " + this.name);
    }
}

// Creating an instance
let p = new Person();
p.name = "Alice";
p.greet();
"""),
        ("Concurrency", """
// Parallel execution
parallel {
    print("This runs in parallel");
    print("With this");
}

// Repeat syntax
repeat 3 times {
    print("Hi");
}
""")
    ]
    
    for title, code in examples:
        print(f"\n=== {title} ===")
        print(code)

if __name__ == "__main__":
    main()
