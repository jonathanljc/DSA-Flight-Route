import ast

class StringLiteralVisitor(ast.NodeVisitor):
    def visit_Str(self, node):
        print(f"String literal found at line {node.lineno}: {node.s}")

with open('main.py') as f:
    root = ast.parse(f.read())

visitor = StringLiteralVisitor()
visitor.visit(root)