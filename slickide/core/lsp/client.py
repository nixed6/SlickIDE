import json
import threading
from PySide6.QtCore import QObject, Signal


class LSPClient(QObject):
    message_received = Signal(dict)

    def __init__(self, process):
        super().__init__()
        self.process = process
        self._buffer = b""

        # Connect process output
        self.process.readyReadStandardOutput.connect(self._read_stdout)

    # ------------------------
    # Sending JSON-RPC
    # ------------------------

    def send_request(self, method, params=None, request_id=1):
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        self._send_message(message)

    def send_notification(self, method, params=None):
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }

        self._send_message(message)

    def _send_message(self, message):
        content = json.dumps(message)
        content_bytes = content.encode("utf-8")

        header = f"Content-Length: {len(content_bytes)}\r\n\r\n"
        self.process.write(header.encode("utf-8") + content_bytes)

    # ------------------------
    # Receiving JSON-RPC
    # ------------------------

    def _read_stdout(self):
        self._buffer += self.process.readAllStandardOutput().data()

        while b"\r\n\r\n" in self._buffer:
            header, self._buffer = self._buffer.split(b"\r\n\r\n", 1)

            header_str = header.decode()
            content_length = 0

            for line in header_str.split("\r\n"):
                if line.startswith("Content-Length:"):
                    content_length = int(line.split(":")[1].strip())

            if len(self._buffer) < content_length:
                return  # wait for full message

            content = self._buffer[:content_length]
            self._buffer = self._buffer[content_length:]

            message = json.loads(content.decode())
            self.message_received.emit(message)