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

## Language Syntax Examples

### Variables & Arithmetic

```
let x = 10;
let y = 5;
print("x + y = " + (x + y));  // 15
```

### Control Flow

```
if (x > y) {
    print("x is greater than y");
} else {
    print("x is not greater than y");
}
```

### Loops

```
let i = 0;
while (i < 3) {
    print("Count: " + i);
    i = i + 1;
}
```

### Functions

```
function greet(name) {
    print("Hello, " + name + "!");
}

greet("World");  // Hello, World!
```

### Classes & OOP

```
class Person {
    greet() {
        print("My name is " + this.name);
    }
}

let person = new Person();
person.name = "Alice";
person.greet();  // My name is Alice
```

### Repeat Statement

```
repeat 3 times {
    print("Hello!");
}
```

### Parallel Execution

```
parallel {
    print("This runs in parallel");
    print("With this");
}
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