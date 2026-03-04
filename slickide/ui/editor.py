from PySide6.QtWidgets import QTabWidget, QPlainTextEdit, QFileDialog
from PySide6.QtGui import QFont
from PySide6.QtCore import QFile, QTextStream
from ui.syntax_highlighter import PythonHighlighter

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 11))
        self.file_path = None

        self.highlighter = PythonHighlighter(self.document())


class EditorTabs(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.removeTab)

    def new_tab(self, title="Untitled"):
        editor = CodeEditor()
        index = self.addTab(editor, title)
        self.setCurrentIndex(index)
        return editor

    def current_editor(self):
        return self.currentWidget()

    def open_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        editor = self.new_tab(file_path.split("/")[-1])
        editor.setPlainText(content)
        editor.file_path = file_path

    def save_file(self):
        editor = self.current_editor()
        if not editor:
            return

        if editor.file_path is None:
            self.save_file_as()
        else:
            with open(editor.file_path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())

    def save_file_as(self):
        editor = self.current_editor()
        if not editor:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As"
        )

        if file_path:
            editor.file_path = file_path
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())

            self.setTabText(self.currentIndex(), file_path.split("/")[-1])