from PySide6.QtWidgets import QTextEdit


class Terminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def write(self, text):
        self.moveCursor(self.textCursor().End)
        self.insertPlainText(text)
        self.ensureCursorVisible()

    def clear_terminal(self):
        self.clear()