# Toy Programming Language

A simple, extensible programming language interpreter built in Python.

## Features

Toy is a simple, dynamically-typed programming language with the following features:

1. **Variables & Arithmetic**: Declare variables with `let` and perform arithmetic operations.
2. **Control Flow**: Use `if/else` statements for conditional logic.
3. **Loops**: Implement loops with `while` statements.
4. **Functions**: Define and call functions with parameters and return values.
5. **Object-Oriented Programming**: Create classes with methods and instantiate objects.
6. **Concurrency**: Execute code in parallel with the `parallel` statement.
7. **Repeat Statements**: Execute code multiple times with the `repeat` statement.
8. **Memory Management**: Handle variable lifecycle with explicit memory management.
9. **Error Handling**: Robust error handling and debugging capabilities.
10. **Extensibility**: Add new features through plugins and extensions.

## Getting Started

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/jakevin99/pppython.git
   cd pppython
   ```

2. Make sure you have Python 3.6+ installed:
   ```
   python --version
   ```

3. No additional dependencies are required to run the basic interpreter.

### Running Your First Toy Program

1. Create a file called `hello.toy` with the following content:
   ```
   // My first Toy program
   print("Hello, Toy World!");
   ```

2. Run the program using the interpreter:
   ```
   python main.py hello.toy
   ```

### Using the Interactive Mode

Start the interactive REPL (Read-Eval-Print Loop) to try out Toy commands directly:
```
python main.py
```

This allows you to type Toy code line by line and see immediate results.

## Language Usage Guide

### Syntax Basics

All statements in Toy end with a semicolon (`;`). Comments start with `//` and continue to the end of the line.

### Variables & Types

Toy is dynamically typed. Variables are declared using the `let` keyword:

```
let name = "Alice";
let age = 30;
let is_student = true;
let gpa = 3.8;
```

Supported types include:
- Strings (enclosed in double quotes)
- Numbers (integers and floats)
- Booleans (`true` and `false`)
- `null` (represents absence of value)

### Operators

Toy supports the following operators:

- **Arithmetic**: `+`, `-`, `*`, `/`, `%` (modulo)
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical**: `and`, `or`, `not`
- **Assignment**: `=`

String concatenation uses the `+` operator:
```
let greeting = "Hello, " + name + "!";
```

### Control Flow

#### If-Else Statements

```
if (condition) {
    // code to execute if condition is true
} else if (another_condition) {
    // code to execute if another_condition is true
} else {
    // code to execute if all conditions are false
}
```

#### While Loops

```
while (condition) {
    // code to execute repeatedly while condition is true
}
```

#### Repeat Statements

Execute a block of code a specific number of times:
```
repeat 5 times {
    // code to execute 5 times
}
```

### Functions

Define functions with the `function` keyword:

```
function add(a, b) {
    return a + b;
}

// Call the function
let result = add(5, 3);
print(result);  // Output: 8
```

Functions without a return statement will return `null`.

### Object-Oriented Programming

Toy supports classes and objects:

```
class Rectangle {
    init(width, height) {
        this.width = width;
        this.height = height;
    }
    
    area() {
        return this.width * this.height;
    }
}

// Create an instance
let rect = new Rectangle(5, 10);
print(rect.area());  // Output: 50
```

Notes on classes:
- The `init` method is called when creating a new instance
- Use `this` to refer to the current instance
- Methods don't need the `function` keyword
- Create instances with the `new` keyword

### Concurrency

Run code blocks in parallel:

```
parallel {
    // These statements run concurrently
    print("Task 1 running");
    print("Task 2 running");
}
```

### Memory Management

Toy handles memory automatically, but you can explicitly delete variables:

```
let temp = "temporary data";
// ... use temp ...
delete temp;  // Explicitly remove the variable
```

## Running the Interpreter

```
python main.py <script_file>
```

### Interactive Mode

```
python main.py
```

### Debugging

```
python main.py --debug <script_file>
```

## Examples

Look at the example files in the repository to see Toy in action:
- `test.toy`: Basic language features
- `simple_test.toy`: Simple examples of each language construct 
- `final_test.toy`: Comprehensive test of all language features

## Extensions

The language can be extended with new features through the extension mechanism. See the `advance_features/` directory for examples.

## File Structure

- `main.py`: Main entry point
- `lexical_analysis.py`: Tokenization of source code
- `syntax_analysis.py`: Parsing tokens into an AST
- `semantic_analysis.py`: Semantic checking
- `execution_evaluation.py`: Interpreter core
- `memory_management.py`: Memory handling
- `error_handling_debugging.py`: Error handling
- `user_interface_CLI.py`: Command-line interface
- `advance_features/`: Extended language features 