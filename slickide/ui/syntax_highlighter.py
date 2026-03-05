from PySide6.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont
)
from PySide6.QtCore import QRegularExpression


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        # ---------- Keyword Format ----------
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            "and", "as", "assert", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "False",
            "finally", "for", "from", "global", "if", "import",
            "in", "is", "lambda", "None", "nonlocal", "not",
            "or", "pass", "raise", "return", "True", "try",
            "while", "with", "yield"
        ]

        for word in keywords:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.rules.append((pattern, keyword_format))

        # ---------- String Format ----------
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.rules.append((QRegularExpression(r'"[^"]*"'), string_format))
        self.rules.append((QRegularExpression(r"'[^']*'"), string_format))

        # ---------- Comment Format ----------
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r"#.*"), comment_format))

        # ---------- Number Format ----------
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.rules.append((QRegularExpression(r"\b[0-9]+\b"), number_format))

        # ---------- Function Name Format ----------
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        self.rules.append(
            (QRegularExpression(r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)"), function_format)
        )

        # ---------- Class Name Format ----------
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))
        class_format.setFontWeight(QFont.Bold)
        self.rules.append(
            (QRegularExpression(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)"), class_format)
        )

    def highlightBlock(self, text):
        for pattern, format_ in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    format_,
                )


class AsmHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        # ---------- Mnemonics ----------
        mnemonic_format = QTextCharFormat()
        mnemonic_format.setForeground(QColor("#569CD6"))
        mnemonic_format.setFontWeight(QFont.Bold)

        mnemonics = [
            # data movement
            "mov",
            "lea",
            "push",
            "pop",
            # arithmetic / logic
            "add",
            "sub",
            "mul",
            "imul",
            "div",
            "idiv",
            "inc",
            "dec",
            "and",
            "or",
            "xor",
            "not",
            "neg",
            # control flow
            "jmp",
            "je",
            "jne",
            "jg",
            "jge",
            "jl",
            "jle",
            "ja",
            "jae",
            "jb",
            "jbe",
            "call",
            "ret",
            # flags
            "cmp",
            "test",
        ]

        for m in mnemonics:
            pattern = QRegularExpression(rf"\b{m}\b")
            self.rules.append((pattern, mnemonic_format))

        # ---------- Registers ----------
        register_format = QTextCharFormat()
        register_format.setForeground(QColor("#4EC9B0"))

        registers = [
            "eax",
            "ebx",
            "ecx",
            "edx",
            "esi",
            "edi",
            "esp",
            "ebp",
            "rax",
            "rbx",
            "rcx",
            "rdx",
            "rsi",
            "rdi",
            "rsp",
            "rbp",
        ]

        register_pattern = QRegularExpression(
            r"\b(" + "|".join(registers) + r")\b"
        )
        self.rules.append((register_pattern, register_format))

        # ---------- Labels ----------
        label_format = QTextCharFormat()
        label_format.setForeground(QColor("#DCDCAA"))
        label_format.setFontWeight(QFont.Bold)
        self.rules.append(
            (QRegularExpression(r"^[A-Za-z_][A-Za-z0-9_]*:"), label_format)
        )

        # ---------- Directives ----------
        directive_format = QTextCharFormat()
        directive_format.setForeground(QColor("#C586C0"))
        self.rules.append(
            (QRegularExpression(r"\.(data|text|bss)\b"), directive_format)
        )
        self.rules.append(
            (
                QRegularExpression(
                    r"\b(db|dw|dd|dq|resb|resw|resd|resq)\b"
                ),
                directive_format,
            )
        )

        # ---------- Comments ----------
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r";.*"), comment_format))

        # ---------- Numbers ----------
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.rules.append(
            (QRegularExpression(r"\b0x[0-9A-Fa-f]+\b"), number_format)
        )
        self.rules.append(
            (QRegularExpression(r"\b[0-9]+\b"), number_format)
        )

    def highlightBlock(self, text):
        for pattern, format_ in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    format_,
                )