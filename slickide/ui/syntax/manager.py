import os

from ui.syntax.python import PythonHighlighter
from ui.syntax.cpp import CppHighlighter
from ui.syntax.rust import RustHighlighter
from ui.syntax.java import JavaHighlighter
from ui.syntax.asm import AsmHighlighter


def apply_syntax_highlighter(editor, file_path):
    extension = os.path.splitext(file_path)[1]

    document = editor.document()

    if extension == ".py":
        PythonHighlighter(document)

    elif extension in [".cpp", ".c", ".hpp", ".h"]:
        CppHighlighter(document)

    elif extension == ".rs":
        RustHighlighter(document)

    elif extension == ".java":
        JavaHighlighter(document)

    elif extension in [".asm", ".s"]:
        AsmHighlighter(document)

    else:
        # No highlighting
        pass