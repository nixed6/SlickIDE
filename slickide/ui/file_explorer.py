from PySide6.QtWidgets import QFileSystemModel, QTreeView
from PySide6.QtCore import Signal


class FileExplorer(QTreeView):
    file_open_requested = Signal(str)

    def __init__(self, root_path="."):
        super().__init__()

        self.model = QFileSystemModel()
        self.model.setRootPath(root_path)

        self.setModel(self.model)
        self.setRootIndex(self.model.index(root_path))

        self.doubleClicked.connect(self._on_double_click)

    def set_root_path(self, path):
        self.model.setRootPath(path)
        self.setRootIndex(self.model.index(path))

    def _on_double_click(self, index):
        file_path = self.model.filePath(index)
        if not self.model.isDir(index):
            self.file_open_requested.emit(file_path)