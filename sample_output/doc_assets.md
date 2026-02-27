# pkgsample Documentation

## Overview

`pkgsample` is a simple Python package that demonstrates basic package structure and functionality. It includes a version number, a basic arithmetic function, and a command-line interface (CLI) for executing the function.

## Installation

To install the package, you can clone the repository and install it using pip:

```bash
git clone https://github.com/nedbat/pkgsample.git
cd pkgsample
pip install .
```

## Package Structure

The package consists of the following files:

- `src/pkgsample/__init__.py`: Initializes the package and defines the version number.
- `src/pkgsample/add.py`: Contains the `add` function, which computes the sum of two numbers.
- `src/pkgsample/add_cli.py`: Implements a command-line interface for the `add` function.

## Usage

### Versioning

The version of the package is defined in `__init__.py`:

```python
__version__ = "0.1.1"
```

### Adding Numbers

The core functionality of the package is provided by the `add` function located in `add.py`:

```python
def add(x, y):
    """Compute the sum of two numbers."""
    return x + y
```

You can use this function in your Python code as follows:

```python
from pkgsample.add import add

result = add(3, 5)
print(result)  # Output: 8
```

### Command-Line Interface

The package also includes a command-line interface that allows you to add numbers directly from the terminal. You can run the CLI using the following command:

```bash
pkgsample_add 1 2 3
```

This will output:

```
Your numbers are: [bold][1, 2, 3][/bold]
They add up to: [bold]6[/bold]
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.