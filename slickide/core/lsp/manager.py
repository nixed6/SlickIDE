import os
from PySide6.QtCore import QProcess
from .languages import LANGUAGE_SERVERS
from .client import LSPClient


class LSPManager:
    def __init__(self):
        self.process = None
        self.client = None
        self.current_language = None

    def start_for_file(self, file_path):
        extension = os.path.splitext(file_path)[1]

        if extension not in LANGUAGE_SERVERS:
            return None

        config = LANGUAGE_SERVERS[extension]

        if self.process:
            self.stop()

        self.process = QProcess()
        self.process.start(config["command"][0])

        self.client = LSPClient(self.process)
        self.current_language = config["language_id"]

        # Initialize LSP
        self.client.send_request(
            "initialize",
            {
                "processId": None,
                "rootUri": None,
                "capabilities": {}
            }
        )

        self.client.send_notification("initialized", {})

        print(f"LSP started for {self.current_language}")

        return self.client

    def stop(self):
        if self.process:
            self.process.kill()
            self.process = None
            self.client = None
            self.current_language = None


