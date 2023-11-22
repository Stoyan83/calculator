import tkinter as tk
import re
from math import sqrt
import platform
from decimal import Decimal, getcontext

# solvs decimal precision problem have to call normalize() in result
getcontext().prec = 15

class WindowUtils:
    @staticmethod
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")


class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Calculator")

        self.text = tk.StringVar()
        self.text.set(0)

        self.memory = 0
        self.memory_var = tk.StringVar()
        self.memory_var.set("M")
        self.operator = ''

        self.ram = []
        self.ram_text = tk.StringVar()

        self.mr_button_state = tk.StringVar()
        self.mr_button_state.set('normal')

        self.buttons = [
            'mc', 'm-', 'm+', 'mr',
            'n!', 'x\u00B2', '\u221A', '\u2190',
            '%', 'ce', 'c', '\u00F7',
            '7', '8', '9', 'x',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '\u00B1', '0', '.', '='
        ]

        self.function_map = {
            'mc': self.memory_clear,
            'm-': self.memory_subtract,
            'm+': self.memory_add,
            'mr': self.memory_recall,
            'n!': self.factorial,
            'x²': self.square,
            '√': self.square_root,
            '÷': self.divide,
            '%': self.percent,
            'ce': self.clear_entry,
            'c': self.clear_all,
            '←': self.backspace,
            'x': self.multiply,
            '-': self.subtract,
            '+': self.add,
            '±': self.change_sign,
            '.': self.add_decimal,
            '=': self.calculate,
        }

        master.resizable(False, False)

        self.display()
        self.load_keypad()

    def load_keypad(self):
        keypad_frame = tk.Frame(self.master)
        keypad_frame.grid(row=2, column=0)

        bg_color = "#1E1E1E"
        fg_color = "#FFFFFF"
        blue_color = "#0074D9"
        red_color = "#FF4136"

        for index, button in enumerate(self.buttons):
            if button == 'mr':
                self.mr_button = tk.Button(
                    keypad_frame,
                    text=button,
                    font=('sans-serif', 12),
                    width=7,
                    height=3,
                    command=lambda b=button: self.button_click(b),
                    state='disabled',
                    bg=bg_color,
                    fg=fg_color,
                    activebackground=bg_color,
                    activeforeground=fg_color
                )
                self.mr_button.grid(
                    row=index // 4, column=index % 4, padx=5, pady=5)
            elif button == '=':
                tk.Button(
                    keypad_frame,
                    text=button,
                    font=('sans-serif', 12),
                    width=7,
                    height=3,
                    command=lambda b=button: self.button_click(b),
                    state='normal',
                    bg=blue_color,
                    fg=fg_color,
                    activebackground=blue_color,
                    activeforeground=fg_color
                ).grid(row=index // 4, column=index % 4, padx=5, pady=5)
            elif button in ['ce', 'c']:
                tk.Button(
                    keypad_frame,
                    text=button.upper(),
                    font=('sans-serif', 12),
                    width=7,
                    height=3,
                    command=lambda b=button: self.button_click(b),
                    state='normal',
                    bg=red_color,
                    fg=fg_color,
                    activebackground=red_color,
                    activeforeground=fg_color
                ).grid(row=index // 4, column=index % 4, padx=5, pady=5)
            else:
                tk.Button(
                    keypad_frame,
                    text=button,
                    font=('sans-serif', 12),
                    width=7,
                    height=3,
                    command=lambda b=button: self.button_click(b),
                    bg=bg_color,
                    fg=fg_color,
                    activebackground=bg_color,
                    activeforeground=fg_color
                ).grid(row=index // 4, column=index % 4, padx=5, pady=5)

        self.memory_label = tk.Label(
            self.master, textvariable=self.memory_var, bg=bg_color, fg=fg_color)
        self.memory_label.grid(row=1, column=0)


    def update_ram_text(self):
        ram_formatted = ' '.join(self.ram)
        ram_formatted = ram_formatted.replace('*', 'x')
        ram_formatted = ram_formatted.replace('/', '\u00F7')
        self.ram_text.set(ram_formatted)


    def display(self):

        bg_color = "#1E1E1E"
        fg_color = "#FFFFFF"

        self.master.config(bg=bg_color)
        self.input_frame = tk.LabelFrame(self.master, borderwidth=6, relief="groove", font=(
            'sans-serif', 10, 'bold'), width=300, height=100, bg=bg_color, fg=fg_color)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10)

        self.ram_display = tk.Label(self.input_frame, textvariable=self.ram_text, font=(
            'sans-serif', 10, 'bold'), justify='right', anchor='e', width=30, height=1, bg=bg_color, fg=fg_color)
        self.ram_display.grid(row=0, column=0, padx=5, pady=2)

        self.text_display = tk.Label(self.input_frame, textvariable=self.text, font=(
            'sans-serif', 16, 'bold'), justify='right', anchor='e', width=18, height=1, bg=bg_color, fg=fg_color)
        self.text_display.grid(row=1, column=0, padx=5, pady=2)

        self.load_keypad()


    def insert_operator(self, value):
        current_input = self.operator
        if current_input == '0' and value.isdigit():
            self.operator = value
        else:
            if len(self.operator) < 17:
                self.operator += value
        self.text.set(self.operator)


    def button_click(self, button):

        if button in self.function_map:
            self.function_map[button]()
        else:
            self.insert_operator(button)


    def change_sign(self):
        sign = self.text.get()
        if sign[0] == '-':
            temp = sign[1:]
        elif sign[0] in "*/":
            if sign[1] == "-":
                temp = sign[0] + sign[2:]
            else:
                temp = sign[0] + '-' + sign[1:]
        else:
            temp = '-' + sign
        self.operator = temp
        self.text.set(self.operator)


    def clear_entry(self):
        self.text.set(0)
        self.ram_text.set("")
        self.operator = ''


    def clear_all(self):
        self.text.set(0)
        self.ram_text.set("")
        self.operator = ''
        self.ram = []


    def memory_clear(self):
        self.memory_var.set("")
        self.memory = 0
        self.mr_button.config(state='disabled')
        self.memory_var.set("M")


    def memory_add(self):
        self.memory += float(self.text.get())
        self.format_memory_label()
        self.mr_button.config(state='normal')


    def memory_subtract(self):
        self.memory -= float(self.text.get())
        self.format_memory_label()
        self.mr_button.config(state='normal')


    def memory_recall(self):
        memory_decimal = Decimal(self.memory)
        formatted_memory = memory_decimal.normalize()
        self.text.set(str(formatted_memory))


    def format_memory_label(self):
        memory_decimal = Decimal(self.memory)
        formatted_memory = '{:.15f}'.format(memory_decimal.normalize()).rstrip('0').rstrip('.')

        self.memory_var.set(f"M: {formatted_memory}")
        self.mr_button.config(state='normal')


    def add(self):
        self.update_ram_text()
        current_value = self.text.get()
        if current_value:
            self.ram.append(current_value)
            expression = "".join(self.ram)
            result = self.evaluate_expression(expression)
            self.text.set(result)

        self.update_ram_text()
        self.ram.append("+")
        self.operator = ""
        self.update_ram_text()


    def subtract(self):
        self.update_ram_text()
        current_value = self.text.get()
        if current_value:
            self.ram.append(current_value)
            expression = "".join(str(item) for item in self.ram)
            result = self.evaluate_expression(expression)
            self.text.set(result)

        self.update_ram_text()
        self.ram.append("-")
        self.operator = ""
        self.update_ram_text()


    def multiply(self):
        self.update_ram_text()
        current_value = self.text.get()

        if current_value:
            self.ram.append(current_value)
            expression = "".join(str(item) for item in self.ram)
            result = self.evaluate_expression(expression)
            self.text.set(result)

        self.update_ram_text()
        self.ram.append("*")
        self.operator = ""
        self.update_ram_text()


    def divide(self):
        self.update_ram_text()
        current_value = self.text.get()
        if current_value:
            self.ram.append(current_value)
            expression = "".join(str(item) for item in self.ram)
            result = self.evaluate_expression(expression)
            self.text.set(result)

        self.update_ram_text()
        self.ram.append("/")
        self.operator = ""
        self.update_ram_text()


    def factorial(self):
        try:
            n = int(self.text.get())
            if n < 0:
                self.text.set("Invalid input")
            else:
                result = self.calculate_factorial(n)
                self.text.set(result)
        except:
            self.operator = '0'
            self.text.set("Overflow")


    def calculate_factorial(self, n):
        if n == 0 or n == 1:
            return 1

        result = Decimal(n) * Decimal(self.calculate_factorial(n - 1))

        return result


    def square(self):
        value = Decimal(self.text.get())
        result = value ** 2
        if abs(result) > 1e100 or (abs(result) < 1e-100 and result != 0):
            self.operator = '0'
            self.text.set("Overflow")
        else:
            self.text.set(result.normalize())
            

    def square_root(self):
        value = float(self.text.get())
        if value >= 0:
            result = sqrt(value)
            if abs(result) > 1e100:
                self.operator = '0'
                self.text.set("Overflow")
            else:
                if result.is_integer():
                    self.text.set(int(result))
                else:
                    self.text.set(result)
        else:
            self.text.set("Invalid input")


    def percent(self):
        try:
            value = float(self.text.get())
            if len(self.ram) <= 1:
                result = 0
            else:
                result = value / 100
            if abs(result) > 1e100:
                self.operator = '0'
                self.text.set("Overflow")
            else:
                self.text.set(result)
        except ValueError:
            self.text.set("Invalid input")


    def backspace(self):
        current_text = self.text.get()
        if len(current_text) > 1:
            new_text = current_text[:-1]
            self.text.set(new_text)
            self.operator = new_text
        else:
            self.text.set("0")
            self.operator = ""


    def add_decimal(self):
        current_text = self.text.get()

        if current_text == "0":
            self.operator = "0."
            current_text = self.text.set("0.")
        else:
            if '.' not in current_text:
                self.insert_operator(".")


    def calculate(self):
        self.ram.append(self.text.get())
        expression = "".join(str(item) for item in self.ram)
        result = self.evaluate_expression(expression)
        self.text.set(result)
        if self.ram[-1] != '=':
            self.ram.append("=")
        self.update_ram_text()
        self.ram = []


    def evaluate_expression(self, expression):
        try:
            expression = expression.replace('--', '+').replace('+-', '-')

            # It matches all integers and floating numbers even if they are negative all sign in [-+*/]
            # and all special cases where we have combinations of signs *- and /-
            tokens = re.findall(r'-|\d*\.\d+|\d+|\*\-|/-|[-+*/]', expression)

            # Add "0" to the beginning of tokens if the first token is "-" to handle case when we start with negative number
            if tokens and tokens[0] == '-':
                tokens = ['0'] + tokens

            # Convert to Reverse Polish Notation (RPN) using Shunting Yard algorithm
            # Parentheses could be added to the evaluate expression later.
            output_queue = []
            operator_stack = []
            precedence = {'+': 1, '-': 1, '*-': 2, '*': 2, '/-': 2, '/': 2}

            for token in tokens:
                if token.replace('-', '', 1).replace('.', '', 1).isnumeric():
                    output_queue.append(token)
                elif token in ['*-', '/-', '-', '+'] or token in '+-*/':
                    while operator_stack and operator_stack[-1] in '+-*/' and precedence[operator_stack[-1]] >= precedence[token]:
                        output_queue.append(operator_stack.pop())
                    operator_stack.append(token)

            while operator_stack:
                output_queue.append(operator_stack.pop())

            # Evaluate RPN
            operand_stack = []
            for token in output_queue:
                if token.isnumeric():
                    operand_stack.append(int(token))
                else:
                    try:
                        operand_stack.append(float(token))
                    except ValueError:
                        b = operand_stack.pop()
                        a = operand_stack.pop()
                        if token == '+':
                            operand_stack.append(a + b)
                        elif token == '-':
                            operand_stack.append(a - b)
                        elif token == '*':
                            operand_stack.append(a * b)
                        elif token == '*-':
                            operand_stack.append(a * -b)
                        elif token == '/-':
                            operand_stack.append(a / -b)
                        elif token == '/':
                            operand_stack.append(a / b)
                        elif token == '+-':
                            operand_stack.append(a + -b)
                        elif token == '--':
                            operand_stack.append(a - -b)


            result = operand_stack[0]
            decimal_result = (Decimal(result))

            formatted_result = '{:.15f}'.format(decimal_result.normalize()).rstrip('0').rstrip('.')

            return formatted_result

        except:
            return "Cannot divide by zero"


root = tk.Tk()

# Just test it on Windows and Linux and think it fixes the differences in hardcoded values in appearance.
platform_values = {
    "Windows": (330, 660),
    "Linux": (430, 680),
    "Other": (400, 700)
}

platform_name = platform.system()
x, y = platform_values.get(platform_name, platform_values["Other"])

WindowUtils.center_window(root, x, y)

calc = Calculator(root)
root.mainloop()
