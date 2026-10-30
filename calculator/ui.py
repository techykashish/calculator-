"""Tkinter interface for ProCalc."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from .engine import CalculationError, evaluate_expression, format_result
from .history import HistoryStore


class CalculatorApp:
    BACKGROUND = "#0b1020"
    PANEL = "#111a2e"
    BUTTON = "#1a2540"
    BUTTON_HOVER = "#263453"
    TEXT = "#f4f7ff"
    MUTED = "#91a0bb"
    ACCENT = "#6c8cff"
    OPERATOR = "#25375d"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ProCalc")
        self.root.geometry("440x760")
        self.root.minsize(360, 640)
        self.root.configure(bg=self.BACKGROUND)

        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.angle_mode = tk.StringVar(value="DEG")
        self.history_store = HistoryStore()
        self.history: list[dict[str, str]] = []
        self.history_visible = False

        self._build_layout()
        self._bind_keyboard()
        self._load_history()

    def _build_layout(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self.root, bg=self.BACKGROUND)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.grid_columnconfigure(1, weight=1)
        tk.Label(
            header,
            text="◈",
            font=("Segoe UI", 20, "bold"),
            fg=self.ACCENT,
            bg=self.BACKGROUND,
        ).grid(row=0, column=0, rowspan=2, padx=(0, 10))
        tk.Label(
            header,
            text="ProCalc",
            font=("Segoe UI", 16, "bold"),
            fg=self.TEXT,
            bg=self.BACKGROUND,
        ).grid(row=0, column=1, sticky="w")
        tk.Label(
            header,
            text="SCIENTIFIC CALCULATOR",
            font=("Segoe UI", 8, "bold"),
            fg=self.MUTED,
            bg=self.BACKGROUND,
        ).grid(row=1, column=1, sticky="w")
        self.history_button = tk.Button(
            header,
            text="History",
            command=self._toggle_history,
            font=("Segoe UI", 9, "bold"),
            fg=self.MUTED,
            bg=self.PANEL,
            activebackground=self.BUTTON_HOVER,
            activeforeground=self.TEXT,
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        )
        self.history_button.grid(row=0, column=2, rowspan=2, sticky="e")

        content = tk.Frame(self.root, bg=self.BACKGROUND)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=8)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        display = tk.Frame(content, bg=self.PANEL, padx=20, pady=16)
        display.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        display.grid_columnconfigure(0, weight=1)
        mode = tk.Button(
            display,
            textvariable=self.angle_mode,
            command=self._toggle_angle_mode,
            font=("Segoe UI", 9, "bold"),
            fg=self.ACCENT,
            bg="#1c2a48",
            activebackground="#26385e",
            activeforeground=self.TEXT,
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
        )
        mode.grid(row=0, column=0, sticky="w", pady=(0, 13))
        tk.Label(
            display,
            textvariable=self.expression,
            font=("Segoe UI", 13),
            fg=self.MUTED,
            bg=self.PANEL,
            anchor="e",
        ).grid(row=1, column=0, sticky="ew", pady=(2, 6))
        tk.Label(
            display,
            textvariable=self.result,
            font=("Segoe UI", 34, "bold"),
            fg=self.TEXT,
            bg=self.PANEL,
            anchor="e",
        ).grid(row=2, column=0, sticky="ew")

        self.keypad = tk.Frame(content, bg=self.BACKGROUND)
        self.keypad.grid(row=1, column=0, sticky="nsew")
        for column in range(5):
            self.keypad.grid_columnconfigure(column, weight=1, uniform="key")
        for row in range(6):
            self.keypad.grid_rowconfigure(row, weight=1, uniform="key")

        keys: list[list[tuple[str, str, Callable[[], None] | None]]] = [
            [
                ("sin", "function", lambda: self._insert_function("sin")),
                ("cos", "function", lambda: self._insert_function("cos")),
                ("tan", "function", lambda: self._insert_function("tan")),
                ("(", "function", None),
                (")", "function", None),
            ],
            [
                ("√", "function", lambda: self._insert_function("sqrt")),
                ("x²", "function", lambda: self._append("**2")),
                ("π", "function", None),
                ("e", "function", None),
                ("⌫", "utility", self._backspace),
            ],
            [
                ("AC", "utility", self._clear),
                ("±", "utility", self._toggle_sign),
                ("%", "function", None),
                ("÷", "operator", None),
                ("×", "operator", None),
            ],
            [
                ("7", "number", None),
                ("8", "number", None),
                ("9", "number", None),
                ("−", "operator", None),
                ("+", "operator", None),
            ],
            [
                ("4", "number", None),
                ("5", "number", None),
                ("6", "number", None),
                ("log", "function", lambda: self._insert_function("log")),
                ("ln", "function", lambda: self._insert_function("ln")),
            ],
            [
                ("1", "number", None),
                ("2", "number", None),
                ("3", "number", None),
                ("=", "equals", self._calculate),
                ("0", "number", None),
            ],
        ]
        for row, row_keys in enumerate(keys):
            for column, (label, style, action) in enumerate(row_keys):
                button = self._make_key(label, style, action)
                button.grid(
                    row=row,
                    column=column,
                    sticky="nsew",
                    padx=4,
                    pady=4,
                )

        footer = tk.Label(
            content,
            text="Keyboard ready  ·  Enter to calculate  ·  Esc to clear",
            font=("Segoe UI", 8),
            fg=self.MUTED,
            bg=self.BACKGROUND,
        )
        footer.grid(row=2, column=0, sticky="ew", pady=(8, 2))
        self.history_panel = tk.Frame(self.root, bg=self.PANEL, padx=18, pady=14)

    def _make_key(
        self, label: str, style: str, action: Callable[[], None] | None
    ) -> tk.Button:
        colors = {
            "number": (self.BUTTON, self.TEXT),
            "function": (self.PANEL, self.MUTED),
            "operator": (self.OPERATOR, self.TEXT),
            "utility": ("#283047", self.TEXT),
            "equals": (self.ACCENT, "#ffffff"),
        }
        background, foreground = colors[style]

        def invoke() -> None:
            if action is not None:
                action()
            elif label == "(" or label == ")":
                self._append(label)
            else:
                self._append(label)

        button = tk.Button(
            self.keypad,
            text=label,
            command=invoke,
            font=("Segoe UI", 12 if style == "function" else 15, "bold"),
            fg=foreground,
            bg=background,
            activeforeground=self.TEXT,
            activebackground=self.BUTTON_HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            takefocus=True,
        )
        if style in {"number", "function"}:
            button.bind("<Enter>", lambda _event: button.configure(bg=self.BUTTON_HOVER))
            button.bind("<Leave>", lambda _event: button.configure(bg=background))
        return button

    def _append(self, value: str) -> None:
        self.expression.set(self.expression.get() + value)
        self.result.set("…")

    def _insert_function(self, name: str) -> None:
        self._append(f"{name}(")

    def _clear(self) -> None:
        self.expression.set("")
        self.result.set("0")

    def _backspace(self) -> None:
        self.expression.set(self.expression.get()[:-1])
        self.result.set("0" if not self.expression.get() else "…")

    def _toggle_sign(self) -> None:
        current = self.expression.get()
        if current:
            self.expression.set(f"-({current})")
            self.result.set("…")

    def _toggle_angle_mode(self) -> None:
        self.angle_mode.set("RAD" if self.angle_mode.get() == "DEG" else "DEG")

    def _calculate(self) -> None:
        expression = self.expression.get().strip()
        try:
            answer = format_result(evaluate_expression(expression, self.angle_mode.get()))
        except CalculationError as error:
            self.result.set("Error")
            messagebox.showerror("Could not calculate", str(error), parent=self.root)
            return

        self.result.set(answer)
        self.history.insert(0, {"expression": expression, "result": answer})
        self.history = self.history[:100]
        try:
            self.history_store.save(self.history)
        except OSError as error:
            messagebox.showerror(
                "History could not be saved",
                f"The result is correct, but history could not be saved:\n{error}",
                parent=self.root,
            )

    def _load_history(self) -> None:
        try:
            self.history = self.history_store.load()
        except (OSError, ValueError) as error:
            messagebox.showwarning(
                "History unavailable",
                f"Saved history could not be loaded:\n{error}",
                parent=self.root,
            )
            self.history = []

    def _toggle_history(self) -> None:
        if self.history_visible:
            self.history_panel.grid_remove()
            self.history_visible = False
            return

        for child in self.history_panel.winfo_children():
            child.destroy()
        heading = tk.Frame(self.history_panel, bg=self.PANEL)
        heading.pack(fill="x")
        tk.Label(
            heading,
            text="Recent calculations",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT,
            bg=self.PANEL,
        ).pack(side="left")
        tk.Button(
            heading,
            text="Clear",
            command=self._clear_history,
            font=("Segoe UI", 9, "bold"),
            fg=self.MUTED,
            bg=self.PANEL,
            activebackground=self.BUTTON_HOVER,
            activeforeground=self.TEXT,
            relief="flat",
            cursor="hand2",
        ).pack(side="right")

        if not self.history:
            tk.Label(
                self.history_panel,
                text="Your calculations will appear here.",
                font=("Segoe UI", 9),
                fg=self.MUTED,
                bg=self.PANEL,
            ).pack(anchor="w", pady=(12, 0))
        else:
            for entry in self.history[:5]:
                row = tk.Frame(self.history_panel, bg=self.PANEL)
                row.pack(fill="x", pady=(10, 0))
                tk.Label(
                    row,
                    text=entry["expression"],
                    font=("Segoe UI", 9),
                    fg=self.MUTED,
                    bg=self.PANEL,
                    anchor="w",
                ).pack(fill="x")
                tk.Label(
                    row,
                    text=entry["result"],
                    font=("Segoe UI", 12, "bold"),
                    fg=self.TEXT,
                    bg=self.PANEL,
                    anchor="w",
                ).pack(fill="x")
        self.history_panel.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 14))
        self.history_visible = True

    def _clear_history(self) -> None:
        self.history = []
        try:
            self.history_store.save(self.history)
        except OSError as error:
            messagebox.showerror(
                "History could not be cleared",
                str(error),
                parent=self.root,
            )
            return
        self.history_panel.grid_remove()
        self.history_visible = False
        self._toggle_history()

    def _bind_keyboard(self) -> None:
        self.root.bind("<Key>", self._handle_key)

    def _handle_key(self, event: tk.Event) -> str | None:
        if event.keysym in {"Return", "KP_Enter"}:
            self._calculate()
            return "break"
        if event.keysym == "Escape":
            self._clear()
            return "break"
        if event.keysym == "BackSpace":
            self._backspace()
            return "break"
        if event.char and event.char in "0123456789.+-*/()%":
            self._append(event.char)
            return "break"
        return None


def run_app() -> None:
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()
