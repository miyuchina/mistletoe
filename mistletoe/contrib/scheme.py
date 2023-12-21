import re
from collections import ChainMap
from functools import reduce
from mistletoe.base_renderer import BaseRenderer
from mistletoe import span_token, block_token
from mistletoe.core_tokens import MatchObj


class Program(block_token.BlockToken):
    def __init__(self, lines):
        self.children = span_token.tokenize_inner(''.join([line.strip() for line in lines]))


class Expr(span_token.SpanToken):
    @classmethod
    def find(cls, string):
        matches = []
        start = []
        for i, c in enumerate(string):
            if c == '(':
                start.append(i)
            elif c == ')':
                pos = start.pop()
                end_pos = i + 1
                content = string[pos + 1:i]
                matches.append(MatchObj(pos, end_pos, (pos + 1, i, content)))
        return matches

    def __repr__(self):
        return '<Expr {}>'.format(self.children)


class Number(span_token.SpanToken):
    pattern = re.compile(r"(\d+)")
    parse_inner = False

    def __init__(self, match):
        self.number = eval(match.group(0))

    def __repr__(self):
        return '<Number {}>'.format(self.number)


class Variable(span_token.SpanToken):
    pattern = re.compile(r"([^\s()]+)")
    parse_inner = False

    def __init__(self, match):
        self.name = match.group(0)

    def __repr__(self):
        return '<Variable {!r}>'.format(self.name)


class Whitespace(span_token.SpanToken):
    parse_inner = False

    def __new__(self, _):
        return None


class Procedure:
    def __init__(self, expr_token, body, env):
        self.params = [child.name for child in expr_token.children]
        self.body = body
        self.env = env


class Scheme(BaseRenderer):
    def __init__(self):
        self.render_map = {
            "Program": self.render_program,
            "Expr": self.render_expr,
            "Number": self.render_number,
            "Variable": self.render_variable,
        }
        block_token._token_types = []
        span_token._token_types = [Expr, Number, Variable, Whitespace]

        self.env = ChainMap({
            "define": self.define,
            "lambda": lambda expr_token, *body: Procedure(expr_token, body, self.env),
            "+": lambda x, y: self.render(x) + self.render(y),
            "-": lambda x, y: self.render(x) - self.render(y),
            "*": lambda x, y: self.render(x) * self.render(y),
            "/": lambda x, y: self.render(x) / self.render(y),
            "<": lambda x, y: self.render(x) < self.render(y),
            ">": lambda x, y: self.render(x) > self.render(y),
            "<=": lambda x, y: self.render(x) <= self.render(y),
            ">=": lambda x, y: self.render(x) >= self.render(y),
            "=": lambda x, y: self.render(x) == self.render(y),
            "true": True,
            "false": False,
            "cons": lambda x, y: (self.render(x), self.render(y)),
            "car": lambda pair: self.render(pair)[0],
            "cdr": lambda pair: self.render(pair)[1],
            "and": lambda *args: all(map(self.render, args)),
            "or": lambda *args: any(map(self.render, args)),
            "not": lambda x: not self.render(x),
            "if": lambda cond, true, false: self.render(true) if self.render(cond) else self.render(false),
            "cond": self.cond,
            "null": None,
            "null?": lambda x: self.render(x) is None,
            "list": lambda *args: reduce(lambda x, y: (y, x), map(self.render, reversed(args)), None),
            "display": lambda *args: print(*map(self.render, args)),
        })

    def render_program(self, token):
        return self.render_inner(token)

    def render_inner(self, token):
        result = None
        for child in token.children:
            result = self.render(child)
        return result

    def render_expr(self, token):
        proc, *args = token.children
        proc = self.render(proc)
        return self.apply(proc, args) if isinstance(proc, Procedure) else proc(*args)

    def render_number(self, token):
        return token.number

    def render_variable(self, token):
        return self.env[token.name]

    def define(self, *args):
        if len(args) == 2:
            name_token, val_token = args
            self.env[name_token.name] = self.render(val_token)
        else:
            name_token, expr_token, *body = args
            self.env[name_token.name] = Procedure(expr_token, body, self.env)

    def cond(self, *exprs):
        for expr in exprs:
            test, value = expr.children
            if test == 'else' and 'else' not in self.env:
                return self.render(value)
            if self.render(test):
                return self.render(value)

    def apply(self, proc, args):
        old_env = self.env
        self.env = proc.env.new_child()
        try:
            for param, arg in zip(proc.params, args):
                self.env[param] = self.render(arg)
            result = None
            for expr in proc.body:
                result = self.render(expr)
        finally:
            self.env = old_env
        return result
