from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression


class AsmHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        # ---------- Instructions ----------
        instruction_format = QTextCharFormat()
        instruction_format.setForeground(QColor("#569CD6"))

        instructions = [
            "mov", "add", "sub", "mul", "div",
            "push", "pop", "call", "ret",
            "jmp", "je", "jne", "jg", "jl",
            "cmp", "and", "or", "xor",
            "inc", "dec", "lea", "nop"
        ]

        for word in instructions:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.rules.append((pattern, instruction_format))

        # ---------- Registers ----------
        register_format = QTextCharFormat()
        register_format.setForeground(QColor("#4EC9B0"))

        registers = [
            "eax", "ebx", "ecx", "edx",
            "rax", "rbx", "rcx", "rdx",
            "rsi", "rdi", "rsp", "rbp",
            "al", "ah", "bl", "bh",
            "cl", "ch", "dl", "dh"
        ]

        for reg in registers:
            pattern = QRegularExpression(rf"\b{reg}\b")
            self.rules.append((pattern, register_format))

        # ---------- Directives ----------
        directive_format = QTextCharFormat()
        directive_format.setForeground(QColor("#C586C0"))

        self.rules.append((QRegularExpression(r"\.\w+"), directive_format))
        self.rules.append((QRegularExpression(r"\bsection\b"), directive_format))
        self.rules.append((QRegularExpression(r"\bglobal\b"), directive_format))

        # ---------- Numbers ----------
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))

        self.rules.append((QRegularExpression(r"\b0x[0-9A-Fa-f]+\b"), number_format))
        self.rules.append((QRegularExpression(r"\b\d+\b"), number_format))

        # ---------- Labels ----------
        label_format = QTextCharFormat()
        label_format.setForeground(QColor("#DCDCAA"))

        self.rules.append((QRegularExpression(r"^\s*\w+:"), label_format))

        # ---------- Comments ----------
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))

        self.rules.append((QRegularExpression(r";.*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    fmt
                )