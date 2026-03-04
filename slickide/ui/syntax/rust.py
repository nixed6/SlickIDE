from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression


class RustHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        # ---- Keywords ----
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#C586C0"))

        keywords = [
            "fn", "let", "mut", "impl", "struct",
            "enum", "match", "if", "else",
            "while", "for", "loop", "return",
            "pub", "use", "crate", "mod"
        ]

        for word in keywords:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.rules.append((pattern, keyword_format))

        # ---- Strings ----
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))

        self.rules.append((QRegularExpression(r'"[^"]*"'), string_format))

        # ---- Comments ----
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))

        self.rules.append((QRegularExpression(r"//.*"), comment_format))

        # ---- Numbers ----
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))

        self.rules.append((QRegularExpression(r"\b\d+\b"), number_format))

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