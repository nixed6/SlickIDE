import os
from PySide6.QtCore import QProcess
from .languages import LANGUAGE_SERVERS
from .client import LSPClient


class LSPManager:
    def __init__(self):
        self.process = None
        self.client = None
        self.current_language = None
        self.current_file_path = None
        self.current_version = 0
        self.current_editor = None

    def start_for_file(self, file_path):
        extension = os.path.splitext(file_path)[1]

        if extension not in LANGUAGE_SERVERS:
            return None

        config = LANGUAGE_SERVERS[extension]

        if self.process:
            self.stop()

        self.process = QProcess()

        command = config["command"]
        program = command[0]
        args = command[1:] if len(command) > 1 else []
        self.process.start(program, args)

        self.client = LSPClient(self.process)
        self.current_language = config["language_id"]
        self.current_file_path = file_path
        self.current_version = 0

        # Initialize LSP with a basic workspace rooted at the file's directory
        root_uri = f"file://{os.path.dirname(file_path).replace(os.sep, '/')}"

        self.client.send_request(
            "initialize",
            {
                "processId": None,
                "rootUri": root_uri,
                "capabilities": {},
            },
        )

        self.client.send_notification("initialized", {})

        print(f"LSP started for {self.current_language}")

        return self.client

    def attach_editor(self, editor):
        """Attach an editor to the current LSP session and send didOpen / didChange."""
        if not self.client or not self.current_file_path:
            return

        # Disconnect from previous editor if any
        if self.current_editor is not None and self.current_editor is not editor:
            try:
                self.current_editor.textChanged.disconnect(
                    self._on_editor_text_changed
                )
            except TypeError:
                pass

        self.current_editor = editor

        # Send didOpen with the full current text
        uri = f"file://{self.current_file_path.replace(os.sep, '/')}"
        text = editor.toPlainText()
        self.current_version = 1

        self.client.send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": self.current_language,
                    "version": self.current_version,
                    "text": text,
                }
            },
        )

        # Now track changes
        editor.textChanged.connect(self._on_editor_text_changed)

    def _on_editor_text_changed(self):
        if not self.client or not self.current_editor or not self.current_file_path:
            return

        self.current_version += 1
        uri = f"file://{self.current_file_path.replace(os.sep, '/')}"
        text = self.current_editor.toPlainText()

        self.client.send_notification(
            "textDocument/didChange",
            {
                "textDocument": {
                    "uri": uri,
                    "version": self.current_version,
                },
                "contentChanges": [
                    {
                        "text": text,
                    }
                ],
            },
        )

    def stop(self):
        if self.current_editor is not None:
            try:
                self.current_editor.textChanged.disconnect(
                    self._on_editor_text_changed
                )
            except TypeError:
                pass

        if self.process:
            self.process.kill()

        self.process = None
        self.client = None
        self.current_language = None
        self.current_file_path = None
        self.current_version = 0
        self.current_editor = None
