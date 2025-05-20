# Toy Programming Language

A simple, extensible programming language interpreter that demonstrates key concepts of language design and implementation.

## Features

The Toy language includes the following features:

1. **Lexical Analysis**
   - Recognizes valid tokens
   - Provides meaningful error messages
   - Efficiently skips comments and whitespace

2. **Syntax Analysis**
   - Supports standard programming constructs
   - Generates accurate Abstract Syntax Trees
   - Provides helpful syntax error feedback

3. **Semantic Analysis**
   - Tracks variable declarations and scope
   - Performs type checking
   - Detects semantic violations

4. **Execution and Evaluation**
   - Evaluates expressions with correct precedence
   - Supports control structures (if, while, for)
   - Handles function calls and returns
   - Interactive CLI/REPL support

5. **Memory Management**
   - Manages variable lifecycle
   - Supports both automatic and manual memory handling
   - Prevents access to deleted objects

6. **Error Handling and Debugging**
   - Graceful handling of runtime errors
   - Debugging feedback with line information

7. **User Interface / CLI**
   - Clean command-line interface
   - Support for script execution and flags
   - Consistent output format
   - Built-in help documentation

8. **Advanced Features**
   - Object-oriented programming with classes
   - Lambda functions
   - Concurrent execution
   - Extensible design

## Usage

### Running a Toy Program

```bash
python main.py your_program.toy
```

### Interactive Mode

```bash
python main.py
```

### Debug Mode

```bash
python main.py your_program.toy --debug
```

### Verbose Output

```bash
python main.py your_program.toy --verbose
```

## Language Syntax

### Variables

```
let x = 10;
let name = "John";
let isActive = true;
```

### Control Flow

```
if (x > 5) {
    print("x is greater than 5");
} else {
    print("x is not greater than 5");
}

let i = 0;
while (i < 3) {
    print("i = " + i);
    i = i + 1;
}
```

### Functions

```
function add(a, b) {
    return a + b;
}

print(add(5, 3));  // Outputs: 8
```

### Lambda Functions

```
let square = (x) => x * x;
print(square(4));  // Outputs: 16
```

### Object-Oriented Programming

```
class Person {
    greet() {
        print("Hello, my name is " + this.name);
    }
}

let p = new Person();
p.name = "Alice";
p.greet();  // Outputs: Hello, my name is Alice
```

### Concurrency

```
parallel {
    print("This runs in parallel");
    print("With this line");
}
```

### Memory Management

```
let arr = [1, 2, 3];
delete(arr);
// Attempting to access arr would raise an error
```

### Repetition

```
repeat 3 times {
    print("Hi!");
}
```

## Development

To extend or modify the Toy language, the main components are:

- `lexical_analysis.py`: Tokenization and lexical error handling
- `syntax_analysis.py`: Parsing and AST generation
- `semantic_analysis.py`: Type checking and scope management
- `execution_evaluation.py`: Interpreter and runtime environment
- `memory_management.py`: Memory tracking and object lifecycle
- `error_handling_debugging.py`: Error reporting and debugging tools
- `user_interface_CLI.py`: Command-line interface
- `advance_features/`: Advanced language features (OOP, lambdas, etc.)

## Examples

Example Toy programs can be found in:
- `test.toy`
- `simple_test.toy`
- `comprehensive_test.toy`

## License

This project is open source and available for educational purposes. 