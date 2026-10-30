# ProCalc

A clean, keyboard-friendly scientific desktop calculator built with Python and
Tkinter. The calculation engine is separate from the desktop interface and uses
a restricted expression parser rather than Python's `eval()`.

## Run the app

Requirements: Python 3.10 or newer with Tkinter enabled.

```powershell
python main.py
```

## Run tests

```powershell
python -m unittest discover -v
```

## Project structure

```text
calculator/
  engine.py    Safe expression parsing, math functions, and result formatting
  history.py   Local history persistence
  ui.py        Tkinter window, display, keypad, and keyboard input
main.py        Desktop app entry point
tests/
  test_engine.py
```

## Features

- Arithmetic, parentheses, percentages, and operator precedence
- Scientific functions: trigonometry, square root, logarithms, and factorial
- Degree/radian mode, `pi`, and Euler's number
- Keyboard support, backspace, clear, and persistent recent calculations
- Clear error messages for invalid expressions and unsupported operations

Recent calculations are saved to the user's application data folder under
`ProCalc/history.json`.
