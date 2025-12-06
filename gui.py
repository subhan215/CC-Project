#!/usr/bin/env python3
"""
Mini-C Compiler GUI
CS4031 - Compiler Construction | Fall 2025

A simple graphical user interface for the Mini-C compiler
that allows instructors to test code snippets interactively.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import tempfile
import os
from pathlib import Path

# Import compiler modules
try:
    from src.frontend import lex, parse_program
    from src.backend import (
        variable_resolution_pass,
        emit_tacky,
        Converter,
        replace_pseudoregisters,
        fix_up_instructions,
        CodeEmitter
    )
    from src.backend.optimizer import optimize_program, OptimizationStats
    COMPILER_AVAILABLE = True
except ImportError:
    COMPILER_AVAILABLE = False


import re

def strip_comments(code):
    """Remove C-style comments from code."""
    # Remove multi-line comments /* ... */
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Remove single-line comments // ...
    code = re.sub(r'//.*', '', code)
    return code


def pretty_print_ast(node, indent=0):
    """Pretty print an AST node as a tree structure."""
    prefix = "│   " * indent
    branch = "├── " if indent > 0 else ""
    result = []

    node_type = type(node).__name__

    if node_type == "Program":
        result.append("Program")
        for i, decl in enumerate(node.function_definition):
            is_last = (i == len(node.function_definition) - 1)
            child_prefix = "└── " if is_last else "├── "
            child_indent = "    " if is_last else "│   "
            child_result = pretty_print_ast(decl, 0)
            lines = child_result.split('\n')
            result.append(child_prefix + lines[0])
            for line in lines[1:]:
                if line.strip():
                    result.append(child_indent + line)

    elif node_type == "FunDecl":
        name = node.name.name if hasattr(node.name, 'name') else str(node.name)
        ret_type = get_type_name(node.fun_type.base_type) if hasattr(node.fun_type, 'base_type') else "?"
        params_str = format_params(node.params)
        result.append(f"Function: {ret_type} {name}({params_str})")
        if hasattr(node, 'body') and node.body:
            body_result = pretty_print_body(node.body, "    ")
            result.append(body_result)

    elif node_type == "VarDecl":
        name = node.name.name if hasattr(node.name, 'name') else str(node.name)
        var_type = get_type_name(node.var_type) if hasattr(node, 'var_type') else "?"
        init_str = ""
        if hasattr(node, 'init') and node.init and type(node.init).__name__ != "Null":
            init_str = " = " + pretty_print_expr(node.init)
        result.append(f"VarDecl: {var_type} {name}{init_str}")

    else:
        result.append(str(node))

    return '\n'.join(result)


def pretty_print_body(body, prefix="    "):
    """Pretty print a function body."""
    result = []

    items = []
    if hasattr(body, 'block'):
        block = body.block
        if hasattr(block, '__iter__') and not isinstance(block, str):
            items = list(block)
        else:
            items = [block]
    elif hasattr(body, '__iter__') and not isinstance(body, str):
        items = list(body)
    else:
        items = [body]

    if not items:
        return prefix + "(empty block)"

    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        branch = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "

        stmt_str = pretty_print_statement(item, prefix + child_prefix)
        lines = stmt_str.split('\n')
        result.append(prefix + branch + lines[0])
        for line in lines[1:]:
            if line.strip():
                result.append(line)

    return '\n'.join(result)


def pretty_print_statement(stmt, prefix=""):
    """Pretty print a statement."""
    stmt_type = type(stmt).__name__

    if stmt_type == "S":
        return pretty_print_statement(stmt.statement, prefix)
    elif stmt_type == "D":
        return pretty_print_ast(stmt.declaration, 0)
    elif stmt_type == "Return":
        expr_str = pretty_print_expr(stmt.exp) if hasattr(stmt, 'exp') else ""
        return f"Return: {expr_str}"
    elif stmt_type == "If":
        cond_str = pretty_print_expr(stmt.exp)
        result = f"If ({cond_str})"
        has_else = hasattr(stmt, '_else') and stmt._else and type(stmt._else).__name__ != "Null"
        then_branch = "├── " if has_else else "└── "
        then_prefix = "│   " if has_else else "    "
        result += f"\n{prefix}{then_branch}Then: " + pretty_print_statement(stmt.then, prefix + then_prefix)
        if has_else:
            result += f"\n{prefix}└── Else: " + pretty_print_statement(stmt._else, prefix + "    ")
        return result
    elif stmt_type == "While":
        cond_str = pretty_print_expr(stmt.exp)
        return f"While ({cond_str})\n{prefix}└── Body: " + pretty_print_statement(stmt.body, prefix + "    ")
    elif stmt_type == "For":
        init_str = pretty_print_expr(stmt.init) if hasattr(stmt, 'init') else ""
        cond_str = pretty_print_expr(stmt.condition) if hasattr(stmt, 'condition') else ""
        post_str = pretty_print_expr(stmt.post) if hasattr(stmt, 'post') else ""
        return f"For ({init_str}; {cond_str}; {post_str})\n{prefix}└── Body: " + pretty_print_statement(stmt.body, prefix + "    ")
    elif stmt_type == "Block" or stmt_type == "Compound":
        block = stmt.block if hasattr(stmt, 'block') else []
        if hasattr(block, '__iter__') and not isinstance(block, str):
            items = list(block)
        else:
            items = [block] if block else []
        if not items:
            return "Block: {}"
        result = "Block:"
        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            branch = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "
            result += f"\n{prefix}{branch}" + pretty_print_statement(item, prefix + child_prefix)
        return result
    elif stmt_type == "Expression":
        return f"Expr: {pretty_print_expr(stmt.exp)}"
    elif stmt_type == "Break":
        return "Break"
    elif stmt_type == "Continue":
        return "Continue"
    else:
        return str(stmt)


def format_any_value(val):
    """Format any value - handles constants, identifiers, etc."""
    if val is None:
        return ""

    val_type = type(val).__name__

    # Handle constant types
    if val_type == "ConstInt" or val_type.startswith("ConstInt"):
        return str(val.int) if hasattr(val, 'int') else str(val)
    if val_type == "ConstLong" or val_type.startswith("ConstLong"):
        return str(val.long) if hasattr(val, 'long') else str(val)
    if val_type == "ConstUInt" or val_type.startswith("ConstUInt"):
        return str(val.uint) if hasattr(val, 'uint') else str(val)
    if val_type == "ConstULong" or val_type.startswith("ConstULong"):
        return str(val.ulong) if hasattr(val, 'ulong') else str(val)
    if val_type == "ConstDouble" or val_type.startswith("ConstDouble"):
        return str(val.double) if hasattr(val, 'double') else str(val)
    if val_type == "ConstChar" or val_type.startswith("ConstChar"):
        return repr(val.char) if hasattr(val, 'char') else str(val)

    # Check for int/long/etc attributes directly (in case type name doesn't match)
    if hasattr(val, 'int') and not hasattr(val, 'identifier') and not hasattr(val, 'name'):
        return str(val.int)
    if hasattr(val, 'long') and not hasattr(val, 'identifier'):
        return str(val.long)

    # Handle Identifier
    if val_type == "Identifier" or val_type.startswith("Identifier"):
        return val.name if hasattr(val, 'name') else str(val)

    # Handle Constant wrapper
    if val_type == "Constant":
        return format_any_value(val.value)

    return None  # Not a simple value


def clean_raw_repr(s):
    """Clean up raw object representations in a string."""
    import re
    # Replace ConstInt(int=X,type=Int()) with just X
    s = re.sub(r'ConstInt\(int=(\d+),type=Int\(\)\)', r'\1', s)
    s = re.sub(r'ConstLong\(long=(\d+),type=Long\(\)\)', r'\1L', s)
    s = re.sub(r'ConstUInt\(uint=(\d+),type=UInt\(\)\)', r'\1u', s)
    s = re.sub(r'ConstULong\(ulong=(\d+),type=ULong\(\)\)', r'\1uL', s)
    s = re.sub(r'ConstDouble\(double=([0-9.]+),type=Double\(\)\)', r'\1', s)
    # Replace Identifier(name=X) with just X
    s = re.sub(r'Identifier\(name=(\w+)\)', r'\1', s)
    return s


def pretty_print_expr(expr):
    """Pretty print an expression as a string."""
    if expr is None:
        return ""

    expr_type = type(expr).__name__

    if expr_type == "Null":
        return ""

    # Try to format as a simple value first
    simple = format_any_value(expr)
    if simple is not None:
        return simple

    if expr_type == "Var":
        ident = expr.identifier
        if hasattr(ident, 'name'):
            return ident.name
        return format_any_value(ident) or str(ident)
    elif expr_type == "Binary":
        left = pretty_print_expr(expr.left)
        right = pretty_print_expr(expr.right)
        op = format_operator(expr.operator)
        return f"({left} {op} {right})"
    elif expr_type == "Unary":
        operand = pretty_print_expr(expr.expr)
        op = format_operator(expr.operator)
        return f"({op}{operand})"
    elif expr_type == "FunctionCall":
        name = expr.identifier.name if hasattr(expr.identifier, 'name') else str(expr.identifier)
        args = ", ".join(pretty_print_expr(arg) for arg in expr.args)
        return f"{name}({args})"
    elif expr_type == "Assignment":
        left = pretty_print_expr(expr.left) if hasattr(expr, 'left') else ""
        right = pretty_print_expr(expr.right) if hasattr(expr, 'right') else ""
        return f"{left} = {right}"
    elif expr_type == "SingleInit":
        return pretty_print_expr(expr.exp)
    elif expr_type == "InitExp":
        return pretty_print_expr(expr.exp) if hasattr(expr, 'exp') else ""
    elif expr_type == "InitDecl":
        return pretty_print_ast(expr.declaration, 0)
    elif expr_type == "Subscript":
        arr = pretty_print_expr(expr.exp1) if hasattr(expr, 'exp1') else pretty_print_expr(expr.array) if hasattr(expr, 'array') else ""
        idx = pretty_print_expr(expr.exp2) if hasattr(expr, 'exp2') else pretty_print_expr(expr.index) if hasattr(expr, 'index') else ""
        return f"{arr}[{idx}]"
    elif expr_type == "Conditional":
        cond = pretty_print_expr(expr.condition)
        then = pretty_print_expr(expr.exp2)
        els = pretty_print_expr(expr.exp3)
        return f"({cond} ? {then} : {els})"
    else:
        return str(expr)


def format_operator(op):
    """Format an operator enum to string."""
    op_str = str(op)
    if "." in op_str:
        op_str = op_str.split(".")[-1]

    op_map = {
        "ADD": "+", "SUBTRACT": "-", "MULTIPLY": "*", "DIVIDE": "/", "REMAINDER": "%",
        "EQUAL": "==", "NOT_EQUAL": "!=", "LESS_THAN": "<", "GREATER_THAN": ">",
        "LESS_OR_EQUAL": "<=", "GREATER_OR_EQUAL": ">=", "LessOrEqual": "<=", "GreaterOrEqual": ">=",
        "LessThan": "<", "GreaterThan": ">", "Equal": "==", "NotEqual": "!=",
        "Add": "+", "Subtract": "-", "Multiply": "*", "Divide": "/", "Remainder": "%",
        "AND": "&&", "OR": "||", "NOT": "!", "NEGATE": "-", "COMPLEMENT": "~",
        "And": "&&", "Or": "||", "Not": "!", "Negate": "-", "Complement": "~",
    }
    return op_map.get(op_str, op_str)


def format_params(params):
    """Format parameter list."""
    if not params:
        return "void"
    result = []
    for p in params:
        if hasattr(p, '_type'):
            ptype = get_type_name(p._type)
        elif hasattr(p, 'type'):
            ptype = get_type_name(p.type)
        else:
            ptype = "?"

        if hasattr(p, 'name'):
            pname_obj = p.name
            pname = format_any_value(pname_obj)
            if pname is None:
                if isinstance(pname_obj, str):
                    pname = pname_obj
                else:
                    pname = str(pname_obj)
        elif hasattr(p, 'identifier'):
            pname = format_any_value(p.identifier) or str(p.identifier)
        else:
            pname = "?"
        result.append(f"{ptype} {pname}")
    return ", ".join(result)


def get_type_name(t):
    """Get a readable type name."""
    if t is None:
        return "?"
    tname = type(t).__name__
    if tname in ["Int", "Long", "UInt", "ULong", "Char", "Double", "Void", "SChar", "UChar"]:
        return tname.lower()
    elif tname == "Pointer":
        # Check for 'ref' first (actual attribute name), then 'referenced'
        if hasattr(t, 'ref'):
            inner = get_type_name(t.ref)
        elif hasattr(t, 'referenced'):
            inner = get_type_name(t.referenced)
        else:
            inner = "?"
        return f"{inner}*"
    elif tname == "Array":
        # Array class uses _type for element type and _int for size
        if hasattr(t, '_type'):
            inner = get_type_name(t._type)
        elif hasattr(t, 'element'):
            inner = get_type_name(t.element)
        elif hasattr(t, 'type'):
            inner = get_type_name(t.type)
        else:
            inner = "?"

        # Handle size - Array uses _int attribute
        size = "?"
        if hasattr(t, '_int'):
            size_val = t._int
            if isinstance(size_val, int):
                size = str(size_val)
            elif hasattr(size_val, '_int'):
                size = str(size_val._int)
            elif hasattr(size_val, 'value'):
                size = format_any_value(size_val.value) or str(size_val)
            else:
                size = format_any_value(size_val) or str(size_val)
        elif hasattr(t, 'size'):
            size_val = t.size
            if isinstance(size_val, int):
                size = str(size_val)
            elif hasattr(size_val, 'value'):
                size = format_any_value(size_val.value) or str(size_val)
            else:
                size = format_any_value(size_val) or str(size_val)
        return f"{inner}[{size}]"
    elif tname == "Structure":
        tag = t.tag if hasattr(t, 'tag') else "?"
        return f"struct {tag}"
    elif tname == "FunType":
        if hasattr(t, 'base_type'):
            ret = get_type_name(t.base_type)
            return f"{ret}(...)"
        return "function"
    return tname


def pretty_print_symbols(symbols):
    """Pretty print symbol table."""
    result = []
    result.append("┌" + "─" * 60 + "┐")
    result.append("│ {:^58} │".format("SYMBOL TABLE"))
    result.append("├" + "─" * 20 + "┬" + "─" * 20 + "┬" + "─" * 18 + "┤")
    result.append("│ {:^18} │ {:^18} │ {:^16} │".format("Name", "Type", "Attributes"))
    result.append("├" + "─" * 20 + "┼" + "─" * 20 + "┼" + "─" * 18 + "┤")

    for name, info in symbols.items():
        if name.startswith("tmp."):
            continue  # Skip temporaries for cleaner output

        # Get type
        if 'fun_type' in info:
            ft = info['fun_type']
            if hasattr(ft, 'base_type') and hasattr(ft, 'params'):
                ret = get_type_name(ft.base_type)
                params = ", ".join(get_type_name(p) if not hasattr(p, '_type') else get_type_name(p._type) for p in ft.params) if ft.params else "void"
                type_str = f"{ret}({params})"
            else:
                type_str = "function"
        elif 'type' in info:
            type_str = get_type_name(info['type'])
        elif 'val_type' in info:
            type_str = get_type_name(info['val_type'])
        else:
            type_str = "?"

        # Get attributes
        if 'attrs' in info and info['attrs']:
            attr = info['attrs']
            attr_type = type(attr).__name__
            if attr_type == "FunAttr":
                attr_str = "global" if getattr(attr, 'global_scope', False) else "local"
            elif attr_type == "LocalAttr":
                attr_str = "local"
            elif attr_type == "StaticAttr":
                attr_str = "static"
            else:
                attr_str = attr_type
        else:
            attr_str = "-"

        # Truncate if too long
        name_str = name[:18] if len(name) > 18 else name
        type_str = type_str[:18] if len(type_str) > 18 else type_str
        attr_str = attr_str[:16] if len(attr_str) > 16 else attr_str

        result.append("│ {:^18} │ {:^18} │ {:^16} │".format(name_str, type_str, attr_str))

    result.append("└" + "─" * 20 + "┴" + "─" * 20 + "┴" + "─" * 18 + "┘")
    return '\n'.join(result)


def pretty_print_ir(tacky_ir):
    """Pretty print TACKY IR."""
    result = []

    # Get the function definitions from TackyProgram
    if hasattr(tacky_ir, 'function_definition'):
        functions = tacky_ir.function_definition
    elif hasattr(tacky_ir, 'top_level'):
        functions = tacky_ir.top_level
    else:
        functions = tacky_ir

    # Handle if it's not iterable
    if not hasattr(functions, '__iter__') or isinstance(functions, str):
        functions = [functions]

    for func in functions:
        func_type = type(func).__name__

        if func_type == "TackyFunction":
            # Get function name
            func_name = func.name if hasattr(func, 'name') else (func.identifier if hasattr(func, 'identifier') else '?')

            result.append("=" * 50)
            result.append(f"Function: {func_name}")
            result.append("=" * 50)

            # Parameters
            if hasattr(func, 'params') and func.params:
                params_list = []
                for p in func.params:
                    ptype = get_type_name(p._type) if hasattr(p, '_type') else '?'
                    pname = p.name.name if hasattr(p, 'name') and hasattr(p.name, 'name') else (p.name if hasattr(p, 'name') else str(p))
                    params_list.append(f"{ptype} {pname}")
                params_str = ", ".join(params_list)
                result.append(f"Parameters: ({params_str})")
            else:
                result.append("Parameters: (void)")
            result.append("-" * 50)

            # Instructions
            if hasattr(func, 'body') and func.body:
                for i, instr in enumerate(func.body):
                    result.append(f"  {i:3d}: {format_ir_instruction(instr)}")
            else:
                result.append("  (no instructions)")

            result.append("")

        elif func_type == "TackyStaticVariable":
            # Handle static variables
            var_name = func.name if hasattr(func, 'name') else '?'
            result.append(f"Static Variable: {var_name}")
            result.append("")

    if not result:
        result.append("(No IR generated)")

    return '\n'.join(result)


def format_ir_instruction(instr):
    """Format a single IR instruction."""
    instr_type = type(instr).__name__

    if instr_type == "TackyReturn":
        val = format_ir_value(instr.val) if hasattr(instr, 'val') else ""
        return f"return {val}"

    elif instr_type == "TackyBinary":
        dst = format_ir_value(instr.dst)
        left = format_ir_value(instr.src1)
        right = format_ir_value(instr.src2)
        op = format_operator(instr.operator)
        return f"{dst} = {left} {op} {right}"

    elif instr_type == "TackyUnary":
        dst = format_ir_value(instr.dst)
        src = format_ir_value(instr.src)
        op = format_operator(instr.operator)
        return f"{dst} = {op}{src}"

    elif instr_type == "TackyCopy":
        dst = format_ir_value(instr.dst)
        src = format_ir_value(instr.src)
        return f"{dst} = {src}"

    elif instr_type == "TackyJump":
        target = instr.identifier if hasattr(instr, 'identifier') else instr.target
        return f"jump {target}"

    elif instr_type == "TackyJumpIfZero":
        cond = format_ir_value(instr.condition)
        target = instr.target if hasattr(instr, 'target') else instr.identifier
        return f"if {cond} == 0 goto {target}"

    elif instr_type == "TackyJumpIfNotZero":
        cond = format_ir_value(instr.condition)
        target = instr.target if hasattr(instr, 'target') else instr.identifier
        return f"if {cond} != 0 goto {target}"

    elif instr_type == "TackyLabel":
        label = instr.identifer if hasattr(instr, 'identifer') else (instr.identifier if hasattr(instr, 'identifier') else '?')
        return f"{label}:"

    elif instr_type == "TackyFunCall":
        dst = format_ir_value(instr.dst) if hasattr(instr, 'dst') and instr.dst else ""
        args = ", ".join(format_ir_value(a) for a in instr.args) if hasattr(instr, 'args') and instr.args else ""
        name = instr.fun_name if hasattr(instr, 'fun_name') else (instr.name if hasattr(instr, 'name') else '?')
        if dst:
            return f"{dst} = call {name}({args})"
        return f"call {name}({args})"

    elif instr_type == "TackySignExtend":
        dst = format_ir_value(instr.dst)
        src = format_ir_value(instr.src)
        return f"{dst} = sign_extend({src})"

    elif instr_type == "TackyZeroExtend":
        dst = format_ir_value(instr.dst)
        src = format_ir_value(instr.src)
        return f"{dst} = zero_extend({src})"

    elif instr_type == "TackyTruncate":
        dst = format_ir_value(instr.dst)
        src = format_ir_value(instr.src)
        return f"{dst} = truncate({src})"

    elif instr_type == "TackyGetAddress":
        dst = format_ir_value(instr.dst)
        src = format_ir_value(instr.src)
        return f"{dst} = &{src}"

    elif instr_type == "TackyLoad":
        dst = format_ir_value(instr.dst)
        src = format_ir_value(instr.src_ptr) if hasattr(instr, 'src_ptr') else format_ir_value(instr.src)
        return f"{dst} = *{src}"

    elif instr_type == "TackyStore":
        dst = format_ir_value(instr.dst_ptr) if hasattr(instr, 'dst_ptr') else format_ir_value(instr.dst)
        src = format_ir_value(instr.src)
        return f"*{dst} = {src}"

    elif instr_type == "TackyAddPtr":
        dst = format_ir_value(instr.dst)
        ptr = format_ir_value(instr.ptr)
        idx = format_ir_value(instr.index)
        scale = instr.scale if hasattr(instr, 'scale') else 1
        return f"{dst} = {ptr} + {idx} * {scale}"

    elif instr_type == "TackyCopyToOffSet":
        dst = format_ir_value(instr.dst) if hasattr(instr, 'dst') else '?'
        src = format_ir_value(instr.src) if hasattr(instr, 'src') else '?'
        offset = instr.offset if hasattr(instr, 'offset') else 0
        return f"{dst}[{offset}] = {src}"

    elif instr_type == "TackyCopyFromOffSet":
        dst = format_ir_value(instr.dst) if hasattr(instr, 'dst') else '?'
        src = format_ir_value(instr.src) if hasattr(instr, 'src') else '?'
        offset = instr.offset if hasattr(instr, 'offset') else 0
        return f"{dst} = {src}[{offset}]"

    else:
        return str(instr)


def format_ir_value(val):
    """Format an IR value."""
    if val is None:
        return "?"

    val_type = type(val).__name__

    # Try format_any_value first for constants and identifiers
    simple = format_any_value(val)
    if simple is not None and simple != "":
        return simple

    if val_type == "TackyVar":
        return val.identifier if hasattr(val, 'identifier') else str(val)
    elif val_type == "TackyConstant":
        v = val.value
        result = format_any_value(v)
        return result if result else str(v)
    elif val_type == "TackyIdentifier":
        return val.name if hasattr(val, 'name') else str(val)
    else:
        return str(val)


class MiniCCompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini-C Compiler - CS4031 Compiler Construction")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)

        # Configure style
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        self.style.configure('Phase.TButton', font=('Helvetica', 10))
        self.style.configure('Stats.TLabel', font=('Consolas', 9))

        # Compiler statistics
        self.stats = {
            'tokens': 0,
            'symbols': 0,
            'ir_instructions': 0,
            'asm_lines': 0
        }

        # Syntax highlighting colors (VS Code dark theme)
        self.syntax_colors = {
            'keyword': '#569cd6',      # Blue
            'type': '#4ec9b0',         # Teal
            'number': '#b5cea8',       # Light green
            'string': '#ce9178',       # Orange
            'comment': '#6a9955',      # Green
            'operator': '#d4d4d4',     # White
            'function': '#dcdcaa',     # Yellow
            'preprocessor': '#c586c0', # Purple
        }

        self.create_widgets()
        self.load_sample_code()
        self.setup_syntax_highlighting()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(
            title_frame,
            text="Mini-C Compiler",
            style='Title.TLabel'
        ).pack(side=tk.LEFT)

        ttk.Label(
            title_frame,
            text="CS4031 - Compiler Construction | Fall 2025",
            foreground='gray'
        ).pack(side=tk.RIGHT)

        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Source Code (Mini-C)", padding="5")
        input_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        # Code input with line numbers
        self.code_input = scrolledtext.ScrolledText(
            input_frame,
            width=80,
            height=12,
            font=('Consolas', 11),
            wrap=tk.NONE,
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white'
        )
        self.code_input.grid(row=0, column=0, sticky="nsew")

        # Input buttons
        input_btn_frame = ttk.Frame(input_frame)
        input_btn_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        ttk.Button(input_btn_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_btn_frame, text="Save File", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_btn_frame, text="Clear", command=self.clear_input).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_btn_frame, text="Load Sample", command=self.load_sample_code).pack(side=tk.LEFT, padx=2)

        # Sample selector
        ttk.Label(input_btn_frame, text="Samples:").pack(side=tk.LEFT, padx=(20, 5))
        self.sample_var = tk.StringVar(value="factorial")
        sample_combo = ttk.Combobox(
            input_btn_frame,
            textvariable=self.sample_var,
            values=["factorial", "fibonacci", "array_sum", "gcd", "power", "prime", "loops", "simple"],
            width=12,
            state="readonly"
        )
        sample_combo.pack(side=tk.LEFT, padx=2)
        sample_combo.bind("<<ComboboxSelected>>", lambda e: self.load_sample_code())

        # Export button
        ttk.Button(input_btn_frame, text="Export...", command=self.show_export_menu).pack(side=tk.RIGHT, padx=2)

        # Phase Buttons Section
        phase_frame = ttk.LabelFrame(main_frame, text="Compilation Phases", padding="5")
        phase_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        phases = [
            ("1. Lex", self.run_lexer, "Tokenize source code"),
            ("2. Parse", self.run_parser, "Build Abstract Syntax Tree"),
            ("3. Validate", self.run_semantic, "Type check & symbol table"),
            ("4. IR", self.run_ir, "Generate TACKY IR"),
            ("5. Optimize", self.run_optimize, "Constant folding, dead store elimination"),
            ("6. Assembly", self.run_assembly, "Generate x86-64 assembly"),
            ("Run", self.run_full, "Full compilation"),
        ]

        for i, (text, command, tooltip) in enumerate(phases):
            btn = ttk.Button(phase_frame, text=text, command=command, width=14)
            btn.grid(row=0, column=i, padx=3, pady=3)
            self.create_tooltip(btn, tooltip)

        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=3, column=0, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            width=80,
            height=15,
            font=('Consolas', 10),
            wrap=tk.WORD,
            bg='#0c0c0c',
            fg='#00ff00',
            state=tk.DISABLED
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

        # Output buttons
        output_btn_frame = ttk.Frame(output_frame)
        output_btn_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        ttk.Button(output_btn_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_btn_frame, text="Copy Output", command=self.copy_output).pack(side=tk.LEFT, padx=2)

        # Statistics display
        stats_frame = ttk.LabelFrame(main_frame, text="Compiler Statistics", padding="5")
        stats_frame.grid(row=4, column=0, sticky="ew", pady=(5, 0))

        self.stats_var = tk.StringVar(value="Tokens: 0 | Symbols: 0 | IR Instructions: 0 | ASM Lines: 0")
        stats_label = ttk.Label(stats_frame, textvariable=self.stats_var, style='Stats.TLabel')
        stats_label.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, sticky="ew", pady=(10, 0))

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="yellow", padding=2)
            label.pack()
            widget.tooltip = tooltip
            widget.after(1500, lambda: tooltip.destroy() if hasattr(widget, 'tooltip') else None)

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def set_output(self, text, tag=None):
        """Set the output text."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)

    def append_output(self, text):
        """Append to output text."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)

    def clear_output(self):
        """Clear the output area."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def clear_input(self):
        """Clear the input area."""
        self.code_input.delete(1.0, tk.END)

    def copy_output(self):
        """Copy output to clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        self.status_var.set("Output copied to clipboard")

    def get_code(self):
        """Get the source code from input."""
        return self.code_input.get(1.0, tk.END).strip()

    def open_file(self):
        """Open a file dialog to load source code."""
        filepath = filedialog.askopenfilename(
            filetypes=[("C files", "*.c"), ("All files", "*.*")]
        )
        if filepath:
            with open(filepath, 'r') as f:
                self.code_input.delete(1.0, tk.END)
                self.code_input.insert(1.0, f.read())
            self.status_var.set(f"Loaded: {filepath}")

    def save_file(self):
        """Save current code to file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".c",
            filetypes=[("C files", "*.c"), ("All files", "*.*")]
        )
        if filepath:
            with open(filepath, 'w') as f:
                f.write(self.get_code())
            self.status_var.set(f"Saved: {filepath}")

    def load_sample_code(self):
        """Load sample code based on selection."""
        samples = {
            "factorial": '''/* Test Case: Factorial */
int factorial(int n) {
    if (n <= 1)
        return 1;
    return n * factorial(n - 1);
}

int main(void) {
    return factorial(5);  // Returns 120
}''',
            "fibonacci": '''/* Test Case: Fibonacci */
int fibonacci(int n) {
    if (n <= 1)
        return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main(void) {
    return fibonacci(10);  // Returns 55
}''',
            "array_sum": '''/* Test Case: Array Sum */
int main(void) {
    int arr[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int i = 0; i < 5; i = i + 1) {
        sum = sum + arr[i];
    }
    return sum;  // Returns 15
}''',
            "gcd": '''/* Test Case: GCD (Greatest Common Divisor) */
int gcd(int a, int b) {
    if (b == 0)
        return a;
    return gcd(b, a % b);
}

int main(void) {
    return gcd(54, 24);  // Returns 6
}''',
            "power": '''/* Test Case: Power Function */
int power(int base, int exp) {
    if (exp == 0)
        return 1;
    return base * power(base, exp - 1);
}

int main(void) {
    return power(2, 5);  // Returns 32
}''',
            "prime": '''/* Test Case: Prime Check */
int is_prime(int n) {
    if (n <= 1)
        return 0;
    if (n <= 3)
        return 1;
    if (n % 2 == 0)
        return 0;
    for (int i = 3; i * i <= n; i = i + 2) {
        if (n % i == 0)
            return 0;
    }
    return 1;
}

int main(void) {
    return is_prime(17);  // Returns 1 (true)
}''',
            "loops": '''/* Test Case: Loop Demonstrations */
int main(void) {
    int sum = 0;

    // For loop
    for (int i = 1; i <= 5; i = i + 1) {
        sum = sum + i;
    }

    // While loop
    int j = 5;
    while (j > 0) {
        sum = sum + j;
        j = j - 1;
    }

    return sum;  // Returns 30
}''',
            "simple": '''/* Simple Test */
int main(void) {
    int x = 10;
    int y = 20;
    return x + y;  // Returns 30
}'''
        }

        sample = self.sample_var.get()
        if sample in samples:
            self.code_input.delete(1.0, tk.END)
            self.code_input.insert(1.0, samples[sample])
            self.highlight_syntax()
            self.status_var.set(f"Loaded sample: {sample}")

    def run_lexer(self):
        """Run lexical analysis."""
        self.status_var.set("Running lexical analysis...")
        self.clear_output()

        try:
            code = self.get_code()
            if not code:
                self.set_output("Error: No source code provided")
                return

            # Strip comments before lexing
            code = strip_comments(code)
            tokens = lex(code)

            output = "=" * 50 + "\n"
            output += "  LEXICAL ANALYSIS - Token Stream\n"
            output += "=" * 50 + "\n\n"
            output += f"Total tokens: {len(tokens)}\n\n"
            output += "-" * 50 + "\n"
            output += f"{'Token Type':<25} {'Value':<25}\n"
            output += "-" * 50 + "\n"

            for token_type, token_value in tokens:
                output += f"{token_type:<25} {repr(token_value):<25}\n"

            self.set_output(output)
            self.update_stats(tokens=len(tokens))
            self.status_var.set(f"Lexical analysis complete: {len(tokens)} tokens")

        except Exception as e:
            self.set_output(f"Lexer Error:\n{str(e)}")
            self.status_var.set("Lexical analysis failed")

    def run_parser(self):
        """Run syntax analysis."""
        self.status_var.set("Running syntax analysis...")
        self.clear_output()

        try:
            code = self.get_code()
            # Strip comments before parsing
            code = strip_comments(code)
            tokens = lex(code)
            ast = parse_program([token for _, token in tokens])

            output = "=" * 50 + "\n"
            output += "  SYNTAX ANALYSIS - Abstract Syntax Tree\n"
            output += "=" * 50 + "\n\n"
            output += pretty_print_ast(ast)

            self.set_output(clean_raw_repr(output))
            self.status_var.set("Syntax analysis complete")

        except Exception as e:
            self.set_output(f"Parser Error:\n{str(e)}")
            self.status_var.set("Syntax analysis failed")

    def run_semantic(self):
        """Run semantic analysis."""
        self.status_var.set("Running semantic analysis...")
        self.clear_output()

        try:
            code = self.get_code()
            # Strip comments before semantic analysis
            code = strip_comments(code)
            tokens = lex(code)
            ast = parse_program([token for _, token in tokens])
            ast, symbols, type_table = variable_resolution_pass(ast)

            output = "=" * 50 + "\n"
            output += "  SEMANTIC ANALYSIS\n"
            output += "=" * 50 + "\n\n"
            output += pretty_print_symbols(symbols) + "\n\n"
            output += "--- Type Table ---\n"
            output += str(type_table) + "\n\n"
            output += "--- Validated AST ---\n"
            output += pretty_print_ast(ast)

            self.set_output(clean_raw_repr(output))
            self.update_stats(tokens=len(tokens), symbols=len(symbols))
            self.status_var.set("Semantic analysis complete")

        except Exception as e:
            self.set_output(f"Semantic Error:\n{str(e)}")
            self.status_var.set("Semantic analysis failed")

    def run_ir(self):
        """Run IR generation."""
        self.status_var.set("Generating intermediate representation...")
        self.clear_output()

        try:
            code = self.get_code()
            # Strip comments before IR generation
            code = strip_comments(code)
            tokens = lex(code)
            ast = parse_program([token for _, token in tokens])
            ast, symbols, type_table = variable_resolution_pass(ast)
            tacky_ir, symbols1, type_table = emit_tacky(ast, symbols, type_table)

            output = "=" * 50 + "\n"
            output += "  INTERMEDIATE REPRESENTATION (TACKY IR)\n"
            output += "=" * 50 + "\n\n"
            output += pretty_print_ir(tacky_ir)

            # Count IR instructions
            ir_count = 0
            if hasattr(tacky_ir, 'function_definition'):
                for func in tacky_ir.function_definition:
                    if hasattr(func, 'body'):
                        ir_count += len(func.body)

            self.set_output(clean_raw_repr(output))
            self.update_stats(tokens=len(tokens), symbols=len(symbols), ir_instructions=ir_count)
            self.status_var.set("IR generation complete")

        except Exception as e:
            self.set_output(f"IR Generation Error:\n{str(e)}")
            self.status_var.set("IR generation failed")

    def run_optimize(self):
        """Run optimization phase."""
        self.status_var.set("Running optimization...")
        self.clear_output()

        try:
            code = self.get_code()
            code = strip_comments(code)
            tokens = lex(code)
            ast = parse_program([token for _, token in tokens])
            ast, symbols, type_table = variable_resolution_pass(ast)
            tacky_ir, symbols1, type_table = emit_tacky(ast, symbols, type_table)

            # Count instructions before optimization
            ir_before = 0
            if hasattr(tacky_ir, 'function_definition'):
                for func in tacky_ir.function_definition:
                    if hasattr(func, 'body'):
                        ir_before += len(func.body)

            # Run optimization
            optimized_ir, opt_stats = optimize_program(tacky_ir, enabled=True)

            # Count instructions after optimization
            ir_after = 0
            if hasattr(optimized_ir, 'function_definition'):
                for func in optimized_ir.function_definition:
                    if hasattr(func, 'body'):
                        ir_after += len(func.body)

            output = "=" * 60 + "\n"
            output += "  OPTIMIZATION PHASE\n"
            output += "=" * 60 + "\n\n"

            output += "--- BEFORE OPTIMIZATION ---\n"
            output += f"Total Instructions: {ir_before}\n\n"
            output += pretty_print_ir(tacky_ir) + "\n\n"

            output += "=" * 60 + "\n"
            output += "--- AFTER OPTIMIZATION ---\n"
            output += f"Total Instructions: {ir_after}\n\n"
            output += pretty_print_ir(optimized_ir) + "\n\n"

            output += "=" * 60 + "\n"
            output += "--- OPTIMIZATION STATISTICS ---\n"
            output += "=" * 60 + "\n"
            output += f"  Constants Folded:        {opt_stats.constants_folded}\n"
            output += f"  Dead Stores Eliminated:  {opt_stats.dead_stores_eliminated}\n"
            output += f"  Algebraic Simplifications: {opt_stats.algebraic_simplifications}\n"
            output += f"  Strength Reductions:     {opt_stats.strength_reductions}\n"
            output += f"\n"
            output += f"  Instructions Before:     {ir_before}\n"
            output += f"  Instructions After:      {ir_after}\n"
            if ir_before > 0:
                reduction = ((ir_before - ir_after) / ir_before) * 100
                output += f"  Reduction:               {reduction:.1f}%\n"

            self.set_output(clean_raw_repr(output))
            self.update_stats(tokens=len(tokens), symbols=len(symbols), ir_instructions=ir_after)
            self.status_var.set(f"Optimization complete: {ir_before} -> {ir_after} instructions")

        except Exception as e:
            self.set_output(f"Optimization Error:\n{str(e)}")
            self.status_var.set("Optimization failed")

    def run_assembly(self):
        """Generate assembly code."""
        self.status_var.set("Generating assembly...")
        self.clear_output()

        try:
            # Create temp file and compile to assembly
            code = self.get_code()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(code)
                temp_c = f.name

            temp_path = Path(temp_c)
            temp_i = temp_path.with_suffix('.i')
            temp_s = temp_path.with_suffix('.s')

            try:
                # Preprocess
                subprocess.run(
                    ['gcc', '-E', '-P', str(temp_path), '-o', str(temp_i)],
                    check=True,
                    capture_output=True
                )

                with open(temp_i, 'r') as f:
                    preprocessed = f.read()

                # Compile
                tokens = lex(preprocessed)
                ast = parse_program([token for _, token in tokens])
                ast, symbols, type_table = variable_resolution_pass(ast)
                tacky_ir, symbols1, type_table = emit_tacky(ast, symbols, type_table)

                # Optimization pass
                tacky_ir, _ = optimize_program(tacky_ir, enabled=True)

                conv = Converter(symbols1, type_table)
                a_ast, backend_symbol_table = conv.convert_to_assembly_ast(tacky_ir)

                [a_ast, stack_allocation, backend_symbol_table] = replace_pseudoregisters(
                    a_ast, symbols, backend_symbol_table
                )
                fix_up_instructions(a_ast, stack_allocation, backend_symbol_table)

                emitter = CodeEmitter(str(temp_s), symbols, backend_symbol_table)
                emitter.emit_program(a_ast)
                emitter.save()

                # Read assembly
                with open(temp_s, 'r') as f:
                    assembly = f.read()

                asm_lines = len([l for l in assembly.split('\n') if l.strip()])

                output = "=" * 50 + "\n"
                output += "  x86-64 ASSEMBLY (AT&T Syntax)\n"
                output += "=" * 50 + "\n\n"
                output += assembly

                self.set_output(output)
                self.update_stats(tokens=len(tokens), symbols=len(symbols), asm_lines=asm_lines)
                self.status_var.set("Assembly generation complete")

            finally:
                for f in [temp_c, temp_i, temp_s]:
                    if os.path.exists(f):
                        os.unlink(f)

        except subprocess.CalledProcessError as e:
            self.set_output(f"Preprocessor Error:\n{e.stderr.decode() if e.stderr else str(e)}")
            self.status_var.set("Assembly generation failed")
        except Exception as e:
            self.set_output(f"Assembly Generation Error:\n{str(e)}")
            self.status_var.set("Assembly generation failed")

    def run_full(self):
        """Full compilation and execution."""
        self.status_var.set("Compiling and running...")
        self.clear_output()

        try:
            code = self.get_code()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(code)
                temp_c = f.name

            temp_path = Path(temp_c)
            temp_i = temp_path.with_suffix('.i')
            temp_s = temp_path.with_suffix('.s')
            temp_exe = temp_path.with_suffix('.exe') if os.name == 'nt' else temp_path.with_suffix('')

            try:
                output = "=" * 50 + "\n"
                output += "  FULL COMPILATION & EXECUTION\n"
                output += "=" * 50 + "\n\n"

                # Phase 1: Preprocess
                output += "[1/7] Preprocessing... "
                subprocess.run(
                    ['gcc', '-E', '-P', str(temp_path), '-o', str(temp_i)],
                    check=True,
                    capture_output=True
                )
                output += "OK\n"

                with open(temp_i, 'r') as f:
                    preprocessed = f.read()

                # Phase 2: Lex
                output += "[2/7] Lexical Analysis... "
                tokens = lex(preprocessed)
                output += f"OK ({len(tokens)} tokens)\n"

                # Phase 3: Parse
                output += "[3/7] Syntax Analysis... "
                ast = parse_program([token for _, token in tokens])
                output += "OK\n"

                # Phase 4: Semantic
                output += "[4/7] Semantic Analysis... "
                ast, symbols, type_table = variable_resolution_pass(ast)
                output += f"OK ({len(symbols)} symbols)\n"

                # Phase 5: IR
                output += "[5/7] IR Generation... "
                tacky_ir, symbols1, type_table = emit_tacky(ast, symbols, type_table)
                output += "OK\n"

                # Phase 6: Optimization
                output += "[6/7] Optimization... "
                tacky_ir, opt_stats = optimize_program(tacky_ir, enabled=True)
                opt_info = f"({opt_stats.constants_folded} folded, {opt_stats.dead_stores_eliminated} eliminated)"
                output += f"OK {opt_info}\n"

                # Phase 7: Codegen
                output += "[7/7] Code Generation... "
                conv = Converter(symbols1, type_table)
                a_ast, backend_symbol_table = conv.convert_to_assembly_ast(tacky_ir)
                [a_ast, stack_allocation, backend_symbol_table] = replace_pseudoregisters(
                    a_ast, symbols, backend_symbol_table
                )
                fix_up_instructions(a_ast, stack_allocation, backend_symbol_table)

                emitter = CodeEmitter(str(temp_s), symbols, backend_symbol_table)
                emitter.emit_program(a_ast)
                emitter.save()
                output += "OK\n"

                # Assemble and Link
                output += "\n[*] Assembling and Linking... "
                subprocess.run(
                    ['gcc', str(temp_s), '-o', str(temp_exe)],
                    check=True,
                    capture_output=True
                )
                output += "OK\n"

                # Execute
                output += "\n" + "-" * 50 + "\n"
                output += "EXECUTION RESULT:\n"
                output += "-" * 50 + "\n"

                result = subprocess.run(
                    [str(temp_exe)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.stdout:
                    output += f"stdout: {result.stdout}\n"
                output += f"Return value: {result.returncode}\n"
                output += "-" * 50 + "\n"
                output += "\nCompilation successful!"

                self.set_output(output)
                self.status_var.set(f"Execution complete. Return value: {result.returncode}")

            finally:
                for f in [temp_c, temp_i, temp_s, temp_exe]:
                    if os.path.exists(str(f)):
                        os.unlink(str(f))

        except subprocess.TimeoutExpired:
            self.append_output("\n\nError: Execution timed out (5 second limit)")
            self.status_var.set("Execution timed out")
        except subprocess.CalledProcessError as e:
            self.append_output(f"\n\nCompilation/Linking Error:\n{e.stderr.decode() if e.stderr else str(e)}")
            self.status_var.set("Compilation failed")
        except Exception as e:
            self.set_output(f"Error:\n{str(e)}")
            self.status_var.set("Compilation failed")

    def setup_syntax_highlighting(self):
        """Setup syntax highlighting tags and bindings."""
        # Configure tags for different token types
        self.code_input.tag_configure('keyword', foreground=self.syntax_colors['keyword'])
        self.code_input.tag_configure('type', foreground=self.syntax_colors['type'])
        self.code_input.tag_configure('number', foreground=self.syntax_colors['number'])
        self.code_input.tag_configure('string', foreground=self.syntax_colors['string'])
        self.code_input.tag_configure('comment', foreground=self.syntax_colors['comment'])
        self.code_input.tag_configure('function', foreground=self.syntax_colors['function'])
        self.code_input.tag_configure('preprocessor', foreground=self.syntax_colors['preprocessor'])

        # Bind key events for syntax highlighting
        self.code_input.bind('<KeyRelease>', self.on_key_release)
        self.code_input.bind('<<Paste>>', lambda e: self.root.after(10, self.highlight_syntax))

    def on_key_release(self, event=None):
        """Handle key release for syntax highlighting."""
        self.highlight_syntax()

    def highlight_syntax(self):
        """Apply syntax highlighting to the code editor."""
        # Remove all existing tags
        for tag in ['keyword', 'type', 'number', 'string', 'comment', 'function', 'preprocessor']:
            self.code_input.tag_remove(tag, '1.0', tk.END)

        code = self.code_input.get('1.0', tk.END)

        # Keywords
        keywords = r'\b(if|else|while|for|do|return|break|continue|switch|case|default|goto|sizeof)\b'
        # Types
        types = r'\b(int|long|short|char|double|float|void|unsigned|signed|struct|union|enum|const|static|extern)\b'
        # Numbers
        numbers = r'\b\d+\.?\d*[fFlLuU]?\b'
        # Strings
        strings = r'"[^"\\]*(\\.[^"\\]*)*"'
        # Characters
        chars = r"'[^'\\]*(\\.[^'\\]*)*'"
        # Single-line comments
        single_comments = r'//.*$'
        # Multi-line comments
        multi_comments = r'/\*[\s\S]*?\*/'
        # Function calls (identifier followed by parenthesis)
        functions = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()'
        # Preprocessor directives
        preprocessor = r'^\s*#.*$'

        # Apply highlighting
        self._highlight_pattern(keywords, 'keyword')
        self._highlight_pattern(types, 'type')
        self._highlight_pattern(numbers, 'number')
        self._highlight_pattern(strings, 'string')
        self._highlight_pattern(chars, 'string')
        self._highlight_pattern(functions, 'function')
        self._highlight_pattern(preprocessor, 'preprocessor', multiline=True)
        self._highlight_pattern(single_comments, 'comment', multiline=True)
        self._highlight_pattern(multi_comments, 'comment', multiline=True)

    def _highlight_pattern(self, pattern, tag, multiline=False):
        """Apply a tag to all matches of a pattern."""
        code = self.code_input.get('1.0', tk.END)
        flags = re.MULTILINE if multiline else 0

        for match in re.finditer(pattern, code, flags):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.code_input.tag_add(tag, start_idx, end_idx)

    def update_stats(self, tokens=0, symbols=0, ir_instructions=0, asm_lines=0):
        """Update the compiler statistics display."""
        self.stats['tokens'] = tokens
        self.stats['symbols'] = symbols
        self.stats['ir_instructions'] = ir_instructions
        self.stats['asm_lines'] = asm_lines

        stats_text = f"Tokens: {tokens} | Symbols: {symbols} | IR Instructions: {ir_instructions} | ASM Lines: {asm_lines}"
        self.stats_var.set(stats_text)

    def show_export_menu(self):
        """Show export options menu."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Export Tokens (.txt)", command=lambda: self.export_output('tokens'))
        menu.add_command(label="Export AST (.txt)", command=lambda: self.export_output('ast'))
        menu.add_command(label="Export Symbol Table (.txt)", command=lambda: self.export_output('symbols'))
        menu.add_command(label="Export IR (.txt)", command=lambda: self.export_output('ir'))
        menu.add_command(label="Export Assembly (.s)", command=lambda: self.export_output('assembly'))
        menu.add_separator()
        menu.add_command(label="Export All (.zip)", command=self.export_all)

        # Get button position
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def export_output(self, export_type):
        """Export compiler output to file."""
        extensions = {
            'tokens': '.txt',
            'ast': '.txt',
            'symbols': '.txt',
            'ir': '.txt',
            'assembly': '.s'
        }

        filepath = filedialog.asksaveasfilename(
            defaultextension=extensions.get(export_type, '.txt'),
            filetypes=[("Text files", "*.txt"), ("Assembly files", "*.s"), ("All files", "*.*")],
            title=f"Export {export_type.capitalize()}"
        )

        if not filepath:
            return

        try:
            code = self.get_code()
            code = strip_comments(code)
            content = ""

            if export_type == 'tokens':
                tokens = lex(code)
                content = "TOKENS\n" + "=" * 50 + "\n"
                for token_type, token_value in tokens:
                    content += f"{token_type:<25} {repr(token_value)}\n"

            elif export_type == 'ast':
                tokens = lex(code)
                ast = parse_program([token for _, token in tokens])
                content = "ABSTRACT SYNTAX TREE\n" + "=" * 50 + "\n"
                content += clean_raw_repr(pretty_print_ast(ast))

            elif export_type == 'symbols':
                tokens = lex(code)
                ast = parse_program([token for _, token in tokens])
                ast, symbols, _ = variable_resolution_pass(ast)
                content = "SYMBOL TABLE\n" + "=" * 50 + "\n"
                content += clean_raw_repr(pretty_print_symbols(symbols))

            elif export_type == 'ir':
                tokens = lex(code)
                ast = parse_program([token for _, token in tokens])
                ast, symbols, type_table = variable_resolution_pass(ast)
                tacky_ir, _, _ = emit_tacky(ast, symbols, type_table)
                content = "TACKY INTERMEDIATE REPRESENTATION\n" + "=" * 50 + "\n"
                content += clean_raw_repr(pretty_print_ir(tacky_ir))

            elif export_type == 'assembly':
                # Need to use temp file for assembly generation
                with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                    f.write(self.get_code())
                    temp_c = f.name

                temp_path = Path(temp_c)
                temp_i = temp_path.with_suffix('.i')
                temp_s = temp_path.with_suffix('.s')

                try:
                    subprocess.run(['gcc', '-E', '-P', str(temp_path), '-o', str(temp_i)], check=True, capture_output=True)
                    with open(temp_i, 'r') as f:
                        preprocessed = f.read()

                    tokens = lex(preprocessed)
                    ast = parse_program([token for _, token in tokens])
                    ast, symbols, type_table = variable_resolution_pass(ast)
                    tacky_ir, symbols1, type_table = emit_tacky(ast, symbols, type_table)

                    conv = Converter(symbols1, type_table)
                    a_ast, backend_symbol_table = conv.convert_to_assembly_ast(tacky_ir)
                    [a_ast, stack_allocation, backend_symbol_table] = replace_pseudoregisters(a_ast, symbols, backend_symbol_table)
                    fix_up_instructions(a_ast, stack_allocation, backend_symbol_table)

                    emitter = CodeEmitter(str(temp_s), symbols, backend_symbol_table)
                    emitter.emit_program(a_ast)
                    emitter.save()

                    with open(temp_s, 'r') as f:
                        content = f.read()
                finally:
                    for f in [temp_c, temp_i, temp_s]:
                        if os.path.exists(f):
                            os.unlink(f)

            with open(filepath, 'w') as f:
                f.write(content)

            self.status_var.set(f"Exported {export_type} to {filepath}")
            messagebox.showinfo("Export Successful", f"Exported {export_type} to:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def export_all(self):
        """Export all compilation outputs to a zip file."""
        import zipfile

        filepath = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")],
            title="Export All Outputs"
        )

        if not filepath:
            return

        try:
            code = self.get_code()
            code_stripped = strip_comments(code)

            with zipfile.ZipFile(filepath, 'w') as zf:
                # Source code
                zf.writestr("source.c", self.get_code())

                # Tokens
                tokens = lex(code_stripped)
                tokens_content = "TOKENS\n" + "=" * 50 + "\n"
                for token_type, token_value in tokens:
                    tokens_content += f"{token_type:<25} {repr(token_value)}\n"
                zf.writestr("tokens.txt", tokens_content)

                # AST
                ast = parse_program([token for _, token in tokens])
                ast_content = "ABSTRACT SYNTAX TREE\n" + "=" * 50 + "\n"
                ast_content += clean_raw_repr(pretty_print_ast(ast))
                zf.writestr("ast.txt", ast_content)

                # Symbol table
                ast, symbols, type_table = variable_resolution_pass(ast)
                sym_content = "SYMBOL TABLE\n" + "=" * 50 + "\n"
                sym_content += clean_raw_repr(pretty_print_symbols(symbols))
                zf.writestr("symbols.txt", sym_content)

                # IR
                tacky_ir, symbols1, type_table = emit_tacky(ast, symbols, type_table)
                ir_content = "TACKY INTERMEDIATE REPRESENTATION\n" + "=" * 50 + "\n"
                ir_content += clean_raw_repr(pretty_print_ir(tacky_ir))
                zf.writestr("ir.txt", ir_content)

                # Try to add assembly
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                        f.write(self.get_code())
                        temp_c = f.name

                    temp_path = Path(temp_c)
                    temp_i = temp_path.with_suffix('.i')
                    temp_s = temp_path.with_suffix('.s')

                    subprocess.run(['gcc', '-E', '-P', str(temp_path), '-o', str(temp_i)], check=True, capture_output=True)
                    with open(temp_i, 'r') as f:
                        preprocessed = f.read()

                    tokens = lex(preprocessed)
                    ast = parse_program([token for _, token in tokens])
                    ast, symbols, type_table = variable_resolution_pass(ast)
                    tacky_ir, symbols1, type_table = emit_tacky(ast, symbols, type_table)

                    conv = Converter(symbols1, type_table)
                    a_ast, backend_symbol_table = conv.convert_to_assembly_ast(tacky_ir)
                    [a_ast, stack_allocation, backend_symbol_table] = replace_pseudoregisters(a_ast, symbols, backend_symbol_table)
                    fix_up_instructions(a_ast, stack_allocation, backend_symbol_table)

                    emitter = CodeEmitter(str(temp_s), symbols, backend_symbol_table)
                    emitter.emit_program(a_ast)
                    emitter.save()

                    with open(temp_s, 'r') as f:
                        zf.writestr("output.s", f.read())

                    for f in [temp_c, temp_i, temp_s]:
                        if os.path.exists(f):
                            os.unlink(f)
                except:
                    pass  # Assembly generation optional

            self.status_var.set(f"Exported all outputs to {filepath}")
            messagebox.showinfo("Export Successful", f"Exported all outputs to:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")


def main():
    root = tk.Tk()
    app = MiniCCompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
