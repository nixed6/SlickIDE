import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SlickIDE")
    app.setStyleSheet("""
QMainWindow {
    background-color: #1e1e1e;
}
QPlainTextEdit {
    background-color: #252526;
    color: #d4d4d4;
    border: none;
}
QTreeView {
    background-color: #1e1e1e;
    color: white;
}
""")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()