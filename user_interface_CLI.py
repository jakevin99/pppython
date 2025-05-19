import os
import sys
import argparse
from lexical_analysis import Lexer
from syntax_analysis import Parser
from semantic_analysis import SemanticAnalyzer
from execution_evaluation import Interpreter
from error_handling_debugging import ErrorHandler

class ToyLanguageCLI:
    """Command-line interface for the Toy programming language."""
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()
        self.analyzer = SemanticAnalyzer()
        self.interpreter = Interpreter()
        self.error_handler = ErrorHandler()
        self.verbose_mode = False
    
    def set_verbose(self, verbose):
        """Set verbose mode."""
        self.verbose_mode = verbose
    
    def run_file(self, file_path):
        """Run a Toy program from a file."""
        try:
            with open(file_path, 'r') as file:
                source = file.read()
            
            # Run the source code
            exit_code = self.run(source, file_path)
            
            # Exit with the proper code
            if exit_code != 0:
                sys.exit(exit_code)
        
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
    
    def run_repl(self):
        """Run an interactive REPL (Read-Eval-Print Loop)."""
        print("Toy Language REPL (Interactive Mode)")
        print("Type 'exit' or 'quit' to exit, 'help' for help.")
        
        while True:
            try:
                line = input("> ")
                if line.strip() in ["exit", "quit"]:
                    break
                elif line.strip() == "help":
                    self.print_help()
                    continue
                
                # Run the input
                self.run(line)
                
                # Reset error state for the next input
                self.error_handler.reporter.reset()
            
            except KeyboardInterrupt:
                print("\nExiting REPL.")
                break
            except EOFError:
                print("\nExiting REPL.")
                break
    
    def run(self, source, source_name="<stdin>"):
        """Run Toy language source code."""
        # Set source for debugging
        self.error_handler.debugger.set_source(source)
        
        # Lexical analysis
        tokens, lex_errors = self.lexer.scan_tokens(source)
        
        if lex_errors:
            print("Lexical errors:")
            for error in lex_errors:
                print(f"  {error}")
            return 65  # EX_DATAERR
        
        if self.verbose_mode:
            print("Tokens:")
            for token in tokens:
                print(f"  {token}")
        
        # Syntax analysis
        statements, parse_errors = self.parser.parse(tokens)
        
        if parse_errors:
            print("Syntax errors:")
            for error in parse_errors:
                print(f"  {error}")
            return 65  # EX_DATAERR
        
        if self.verbose_mode and statements:
            print("Syntax tree created successfully")
        
        # Skip semantic analysis for now
        if self.verbose_mode:
            print("Skipping semantic analysis")
        
        # Execution
        success = self.interpreter.interpret(statements)
        
        if not success:
            return 70  # EX_SOFTWARE
        
        return 0
    
    def print_help(self):
        """Print help information for the REPL."""
        print("Toy Language Help:")
        print("  - Type any valid Toy language code to execute it")
        print("  - Type 'exit' or 'quit' to exit the REPL")
        print("  - Type 'help' to display this help message")
        print("\nExample commands:")
        print("  let x = 10;")
        print("  print(x + 5);")
        print("  if (x > 5) { print(\"x is greater than 5\"); }")

def main():
    """Main entry point for the Toy language CLI."""
    parser = argparse.ArgumentParser(description="Toy Programming Language Interpreter")
    
    # Command-line arguments
    parser.add_argument("file", nargs="?", help="Script file to execute")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = ToyLanguageCLI()
    cli.set_verbose(args.verbose)
    
    # Set debug mode if requested
    if args.debug:
        cli.error_handler.debugger.set_debug_mode(True)
    
    # Run file or REPL
    if args.file:
        cli.run_file(args.file)
    else:
        cli.run_repl()

if __name__ == "__main__":
    main()
