import json
import pandas as pd
import numpy as np
from math import exp
import os
import sys
from exceptions import *

from sympy.core import symbol
import parse
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import simulation


class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

def choose_file(exp_entry, out, vars, sim_btn):
    filename = filedialog.askopenfilename(initialdir="", title="Choose a file", filetypes=(("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")))
    if filename.endswith('.json'):
        dict = parse.fileToDict(filename)
        set_vars(vars, dict, sim_btn)
        calc(input_list=None, out=out, vars=dict, filename=filename)
    elif filename.endswith('.txt'):
        try:
            with open(filename) as f:
                text = f.readline()
            exp_entry.delete(0,"end")
            exp_entry.insert(0, text)
        except FileNotFoundError:
            pass
    else:
        update_output(out, "Not a valid file!", color="red")

def set_vars(vars, dict, sim_btn):
    for key in dict:
        if key == "expression":
            vars[0].delete(0,"end")
            vars[0].insert(0, dict[key])
        if key == "method":
            vars[1].set(dict[key].title())
        if key == "error tolerance":
            vars[2].set(dict[key])
        if key == "max step":
            vars[3].set(dict[key])
        if key == "lower bound":
            vars[4].set(dict[key])
        if key == "upper bound":
            vars[5].set(dict[key])
        if key == "initial guess":
            vars[6].set(dict[key])
        if key == "first guess":
            vars[7].set(dict[key])
        if key == "second guess":
            vars[8].set(dict[key])
        if dict['method'].lower() == "bisection":
            sim_btn['state'] = tk.NORMAL
        else:
            sim_btn['state'] = tk.DISABLED

def destroyer(root):
    if messagebox.askquestion("Quit", "Are you sure you want to quit?") == "yes":
        root.quit()
        root.destroy()
        sys.exit()

def method_change(all_widgets, method_name, methods_list, sim_btn):
    # receive list of widgets and the method name chosen
    # remove visible widgets from grid
    # if name is bisection or regula falsi: show widgets for lowerbound and upperbound
    # if name is newton raphson or fixed point: show widgets for initial guess
    # if name is secant: show widgets for first guess and second guess
    # Extra: for fixed point and secant, specify that user enters g(x), f(x) otherwise

    if method_name == methods_list[0]:
        sim_btn['state'] = tk.NORMAL
    else:
        sim_btn['state'] = tk.DISABLED

    for widget in all_widgets[:len(all_widgets) - 1]:
        widget.grid_remove()
    
    if method_name == methods_list[0] or method_name == methods_list[1]:
        all_widgets[0].grid(column=0, row=6, sticky=tk.W)
        all_widgets[2].grid(column=1, row=6, sticky=tk.W)

        all_widgets[1].grid(column=0, row=7, sticky=tk.W, pady=(0, 5))
        all_widgets[3].grid(column=1, row=7, sticky=tk.W, pady=(0, 5))

    if method_name == methods_list[2] or method_name == methods_list[3]:
        all_widgets[4].grid(column=0, row=6, sticky=tk.W)

        all_widgets[5].grid(column=0, row=7, sticky=tk.W, pady=(0, 5))

    if method_name == methods_list[4]:
        all_widgets[6].grid(column=0, row=6, sticky=tk.W)
        all_widgets[8].grid(column=1, row=6, sticky=tk.W)

        all_widgets[7].grid(column=0, row=7, sticky=tk.W, pady=(0, 5))
        all_widgets[9].grid(column=1, row=7, sticky=tk.W, pady=(0, 5))

    if method_name == methods_list[2]:
        all_widgets[-1].config(text="Enter Expression g(x)")
    else: 
        all_widgets[-1].config(text="Enter Expression f(x)")

def button_click(exp_entry, symbol):
    current = exp_entry.get()
    exp_entry.insert(exp_entry.index(tk.INSERT), symbol)
    exp_entry.focus()
    if "()" in symbol:
        exp_entry.icursor(exp_entry.index(tk.INSERT) - 1)

def x(exp_entry):
    button_click(exp_entry, "x")

def plus(exp_entry):
    button_click(exp_entry, "+")

def minus(exp_entry):
    button_click(exp_entry, "-")

def mult(exp_entry):
    button_click(exp_entry, "*")

def div(exp_entry):
    button_click(exp_entry, "/")

def pwr(exp_entry):
    button_click(exp_entry, "^")

def sqrt(exp_entry):
    button_click(exp_entry, "sqrt()")

def leftbracket(exp_entry):
    button_click(exp_entry, "()")

def rightbracket(exp_entry):
    button_click(exp_entry, ")")

def cos(exp_entry):
    button_click(exp_entry, "cos()")

def sin(exp_entry):
    button_click(exp_entry, "sin()")

def e(exp_entry):
    button_click(exp_entry, "E")

def clear(exp_entry):
    exp_entry.delete(0, tk.END)
    exp_entry.focus()

def update_output(output, text, color="black"):
    output.configure(state='normal', foreground=color)
    output.delete("1.0", tk.END)
    output.insert('1.0', text)
    output.configure(state='disabled')

def calc(input_list, out, vars=None, filename="input.json"):
    update_output(out, "Calculating...")
    if vars is None:
        vars = {
            'expression': input_list[0].get(),
            'method': input_list[1].get().lower(),
            'error tolerance': input_list[2].get(),
            'max step': input_list[3].get(),
            #'lower bound': input_list[4].get(),
            #'upper bound': input_list[5].get(),
            #'initial guess': float(input_list[6].get()),
            #'first guess': float(input_list[7].get()),
            #'second guess': input_list[8].get(),
            'file path': 'out.json'
        }
        if vars['method'] == 'bisection' or vars['method'] == 'regula falsi':
            vars['lower bound'] = float(input_list[4].get())
            vars['upper bound'] = float(input_list[5].get())

        if vars['method'] == 'fixed point' or vars['method'] == 'newton raphson':
            vars['initial guess'] = float(input_list[6].get())

        if vars['method'] == 'secant':
            vars['first guess'] = float(input_list[7].get())
            vars['second guess'] = float(input_list[8].get())

        with open("input.json", "w") as outfile:
            json.dump(vars, outfile)

    if "file path" not in vars.keys():
        vars["file path"] = "out.json"
    if os.path.isfile(vars["file path"]):
        os.remove(vars["file path"])

    try: 
        parse.call_from_file(filename)
    except (notConvergent, noRootInInterval, badExpression, cannotDiffererntiate, badDictionary, ZeroDivisionError, badFile) as e:
        update_output(out, e, color="red")
        return 
    except Exception as e:
        update_output(out, e, color="red")
        #print(e)

    
    out.after(1000, lambda *args: check(out, vars["file path"]))
    


def check(out, filename="out.json"):
    if os.path.isfile(filename):
        try:
            output = parse.fileToDict(filename)
            if output["status"] == "bad":
                if out["exception"] == "noRootInterval":
                    raise noRootInInterval("No root exists in interval")
                elif out["exception"] == "notConvergent":
                    raise notConvergent("Method did not converge!")
            update_output(out, format_dict(output))
        except FileNotFoundError as e:
            update_output(out, "")
            print(e)
        except (noRootInInterval, notConvergent) as e:
            update_output(out, e, color="red")
    else:
        update_output(out, "Calculating...")
        out.after(1000, lambda *args: check(out, filename))


def format_dict(dict):
    output = ""
    output += output_table(dict).to_string()
    output += "\n\nRoot: " + str(dict['root'])
    output += "\nTime: " + str(dict['time']) + " milliseconds"
    output += "\nIterations: " + str(dict['iterations'])
    output += "\nPrecision: " + str(dict['precision percentage']) + "%"
    return output

def output_table(dict):
    dont_include = ["method", "iterations", "precision percentage", "root", "time", "exception", "status"]
    dict_df = without_keys(dict, dont_include)
    df = pd.DataFrame(dict_df)
    df.index = np.arange(1, len(df) + 1)
    return df


def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}


def simulate(exp_entry, vars, output_txt):
    calc(vars, output_txt)
    x , expression_parsed = parse.get_expression(exp_entry.get())
    func = lambda y:float(expression_parsed.subs(x,y))
    try:
        dict = parse.fileToDict("out.json")
        df = output_table(dict)
        xrange = (-5, 5)
        step = 0.1
        simulation.simulate(df, func, xrange, step)
    except FileNotFoundError:
        pass

def string_entered(exp_entry):
    try:
        if exp_entry.get()[-1] == "(":
            exp_entry.insert(exp_entry.index(tk.INSERT), ")")
            exp_entry.icursor(exp_entry.index(tk.INSERT) - 1)
    except IndexError:
        pass

