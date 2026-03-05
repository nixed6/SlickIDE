from PySide6.QtWidgets import (
    QTabWidget,
    QPlainTextEdit,
    QFileDialog,
    QWidget,
    QTextEdit,
)
from PySide6.QtGui import QFont, QPainter, QColor, QTextFormat, QTextCursor
from PySide6.QtCore import QRect, QSize, Qt
from ui.syntax.manager import apply_syntax_highlighter

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 11))
        self.file_path = None

        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # Set a reasonable tab width (4 spaces)
        tab_stop = 4 * self.fontMetrics().horizontalAdvance(" ")
        self.setTabStopDistance(tab_stop)

    def keyPressEvent(self, event):
        # Auto-indent: when pressing Enter/Return, copy indentation from previous line
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            cursor.beginEditBlock()

            # Get text of current line up to cursor
            block_text = cursor.block().text()
            leading_ws = ""
            for ch in block_text:
                if ch in (" ", "\t"):
                    leading_ws += ch
                else:
                    break

            # Extra indent for block-open characters (Python ':' or '{')
            stripped = block_text.strip()
            extra_indent = ""
            if stripped.endswith(":") or stripped.endswith("{"):
                extra_indent = " " * 4

            # Let base class insert newline
            super().keyPressEvent(event)

            # Insert the same indentation on the new line
            cursor = self.textCursor()
            cursor.insertText(leading_ws + extra_indent)

            cursor.endEditBlock()
            return

        # Tab / Shift+Tab for indent / outdent
        if event.key() == Qt.Key_Tab and not event.modifiers():
            self._indent_or_unindent(indent=True)
            return
        if event.key() == Qt.Key_Backtab:
            self._indent_or_unindent(indent=False)
            return

        # Auto-close brackets and quotes
        pairs = {
            "(": ")",
            "[": "]",
            "{": "}",
            '"': '"',
            "'": "'",
        }
        text = event.text()
        if text in pairs:
            closing = pairs[text]
            cursor = self.textCursor()

            cursor.beginEditBlock()
            # Insert opening
            super().keyPressEvent(event)
            # Insert closing and move cursor back between them
            cursor = self.textCursor()
            cursor.insertText(closing)
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)
            cursor.endEditBlock()
            return

        super().keyPressEvent(event)

    def _indent_or_unindent(self, indent=True):
        """Indent or unindent the current line or selection by one tab stop."""
        cursor = self.textCursor()
        doc = self.document()

        cursor.beginEditBlock()

        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        cursor.setPosition(end)
        end_block = cursor.blockNumber()

        for block_num in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(block_num)
            block_cursor = QTextCursor(block)
            text = block.text()

            if indent:
                block_cursor.setPosition(block.position())
                block_cursor.insertText(" " * 4)
            else:
                # Remove up to 4 leading spaces or a single tab
                leading = len(text) - len(text.lstrip(" \t"))
                if leading > 0:
                    remove_count = 0
                    for ch in text[: min(4, leading)]:
                        if ch in (" ", "\t"):
                            remove_count += 1
                    if remove_count:
                        block_cursor.setPosition(block.position())
                        block_cursor.movePosition(
                            QTextCursor.Right,
                            QTextCursor.KeepAnchor,
                            remove_count,
                        )
                        block_cursor.removeSelectedText()

        cursor.endEditBlock()

    def toggle_comment(self):
        """Toggle line comment on the current line or selection, language-aware."""
        cursor = self.textCursor()
        cursor.beginEditBlock()

        # Determine comment prefix based on file type
        comment_prefix = "#"
        if self.file_path:
            ext = self.file_path.rsplit(".", 1)[-1].lower()
            if ext in ("asm", "s"):
                comment_prefix = ";"
            elif ext in ("c", "h", "hpp", "cpp", "cc", "java", "js", "ts"):
                comment_prefix = "//"

        # Work on all selected lines (or current line if no selection)
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        cursor.setPosition(end)
        end_block = cursor.blockNumber()

        # Check if all lines are already commented
        doc = self.document()
        all_commented = True
        for block_num in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(block_num)
            text = block.text().lstrip()
            if not text.startswith(comment_prefix):
                all_commented = False
                break

        # Apply toggle
        for block_num in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(block_num)
            block_cursor = QTextCursor(block)
            line_text = block.text()

            if all_commented:
                # Uncomment: remove prefix after leading whitespace
                leading_len = len(line_text) - len(line_text.lstrip())
                idx = leading_len
                if line_text[idx:].startswith(comment_prefix):
                    block_cursor.setPosition(block.position() + idx)
                    block_cursor.movePosition(
                        QTextCursor.Right,
                        QTextCursor.KeepAnchor,
                        len(comment_prefix),
                    )
                    block_cursor.removeSelectedText()
            else:
                # Comment: insert prefix after leading whitespace
                leading_len = len(line_text) - len(line_text.lstrip())
                block_cursor.setPosition(block.position() + leading_len)
                block_cursor.insertText(comment_prefix)

        cursor.endEditBlock()

    def line_number_area_width(self):
        digits = 1
        max_block = max(1, self.blockCount())
        while max_block >= 10:
            max_block //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(245, 245, 245))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(120, 120, 120))
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    int(Qt.AlignRight | Qt.AlignVCenter),
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            # Use a subtle current-line color close to the editor background
            line_color = QColor(40, 40, 40)

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)


class EditorTabs(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        self._open_files = {}

    def _on_tab_close_requested(self, index):
        widget = self.widget(index)
        # Clean up from open-files map
        if isinstance(widget, CodeEditor) and widget.file_path:
            self._open_files.pop(widget.file_path, None)
        self.removeTab(index)

    def new_tab(self, title="Untitled"):
        editor = CodeEditor()
        index = self.addTab(editor, title)
        self.setCurrentIndex(index)
        return editor

    def current_editor(self):
        return self.currentWidget()

    def open_file(self, file_path):
        # If file is already open, just activate that tab
        if file_path in self._open_files:
            index = self._open_files[file_path]
            if 0 <= index < self.count():
                self.setCurrentIndex(index)
                return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        editor = self.new_tab(file_path.split("/")[-1])
        editor.setPlainText(content)
        editor.file_path = file_path
        self._open_files[file_path] = self.indexOf(editor)

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

            # Update tab text
            self.setTabText(self.currentIndex(), file_path.split("/")[-1])

            # Apply appropriate syntax highlighting for the new extension
            apply_syntax_highlighter(editor, file_path)