from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression


class JavaHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        # ---------- Keywords ----------
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))

        keywords = [
            "class", "public", "private", "protected",
            "static", "void", "int", "float", "double",
            "boolean", "char", "new", "return",
            "if", "else", "switch", "case",
            "for", "while", "do", "break", "continue",
            "try", "catch", "finally", "throw", "throws",
            "extends", "implements", "import", "package",
            "this", "super", "null", "true", "false"
        ]

        for word in keywords:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.rules.append((pattern, keyword_format))

        # ---------- Strings ----------
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))

        self.rules.append((QRegularExpression(r'"[^"]*"'), string_format))

        # ---------- Single-line Comments ----------
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))

        self.rules.append((QRegularExpression(r"//.*"), comment_format))

        # ---------- Numbers ----------
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))

        self.rules.append((QRegularExpression(r"\b\d+\b"), number_format))

        # ---------- Annotations ----------
        annotation_format = QTextCharFormat()
        annotation_format.setForeground(QColor("#C586C0"))

        self.rules.append((QRegularExpression(r"@\w+"), annotation_format))

        # ---------- Multi-line Comments ----------
        self.comment_start = QRegularExpression(r"/\*")
        self.comment_end = QRegularExpression(r"\*/")
        self.multi_comment_format = comment_format

    def highlightBlock(self, text):
        # Apply single-line rules
        for pattern, fmt in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    fmt
                )

        # Multi-line comment handling
        self.setCurrentBlockState(0)

        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start.match(text)
            start_index = match.capturedStart() if match.hasMatch() else -1

        while start_index >= 0:
            match = self.comment_end.match(text, start_index)
            if match.hasMatch():
                end_index = match.capturedEnd()
                length = end_index - start_index
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(1)
                length = len(text) - start_index

            self.setFormat(start_index, length, self.multi_comment_format)

            match = self.comment_start.match(text, start_index + length)
            start_index = match.capturedStart() if match.hasMatch() else -1