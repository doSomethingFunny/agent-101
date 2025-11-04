"""安全计算器工具。

使用 AST 解析并仅允许安全的算术运算，避免 `eval` 带来的安全风险。

Functions:
    evaluate_expression: 计算表达式并返回浮点结果。

Raises:
    ValueError: 当表达式非法或含不支持的操作符时。
"""

from __future__ import annotations

import ast
import operator
from typing import Any


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Num):  # py<=3.7
        return float(node.n)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("仅支持数字常量")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _OPS:
            raise ValueError("不支持的二元运算符")
        return _OPS[op_type](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _OPS:
            raise ValueError("不支持的一元运算符")
        return _OPS[op_type](_eval(node.operand))
    if isinstance(node, ast.Expr):
        return _eval(node.value)
    raise ValueError("表达式包含不受支持的语法")


def evaluate_expression(expression: str) -> float:
    """计算数学表达式。

    Args:
        expression: 数学表达式字符串，例如 "(12 + 5) * 3"。

    Returns:
        float: 计算结果。

    Raises:
        ValueError: 当表达式非法或包含不支持的语法时。
    """

    try:
        tree = ast.parse(expression, mode="eval")
        return float(_eval(tree.body))
    except Exception as exc:
        raise ValueError(f"表达式非法: {exc}")