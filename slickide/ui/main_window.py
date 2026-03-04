from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QFileDialog
)
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QAction

from ui.editor import EditorTabs
from ui.file_explorer import FileExplorer
from ui.terminal import Terminal
from core.commands import CommandRegistry
from core.lsp.manager import LSPManager
from ui.syntax.manager import apply_syntax_highlighter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SlickIDE")
        self.resize(1200, 800)

        self.commands = CommandRegistry()
        self.current_project_path = None
        self.lsp_manager = LSPManager()

        self._setup_ui()
        self._create_menu()
        self._setup_process()
        self._register_commands()

    # ------------------------
    # UI SETUP
    # ------------------------

    def _setup_ui(self):
        # Central Editor
        self.editor_tabs = EditorTabs()
        self.setCentralWidget(self.editor_tabs)
        self.editor_tabs.new_tab()

        # File Explorer Dock
        self.file_explorer = FileExplorer()
        self.file_dock = QDockWidget("Files", self)
        self.file_dock.setWidget(self.file_explorer)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)

        # Open file with LSP auto-detect
        self.file_explorer.file_open_requested.connect(
            self._open_file_with_lsp
        )

        # Terminal Dock
        self.terminal = Terminal()
        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setWidget(self.terminal)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)

    # ------------------------
    # MENU BAR
    # ------------------------

    def _create_menu(self):
        menu = self.menuBar()

        # ----- File Menu -----
        file_menu = menu.addMenu("File")

        new_action = QAction("New File", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.editor_tabs.new_tab)
        file_menu.addAction(new_action)

        open_action = QAction("Open File", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file_dialog)
        file_menu.addAction(open_action)

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self._open_folder_dialog)
        file_menu.addAction(open_folder_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.editor_tabs.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.editor_tabs.save_file_as)
        file_menu.addAction(save_as_action)

        # ----- Run Menu -----
        run_menu = menu.addMenu("Run")

        run_action = QAction("Run File", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_current_file)
        run_menu.addAction(run_action)

    # ------------------------
    # PROCESS SETUP
    # ------------------------

    def _setup_process(self):
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._process_finished)

    # ------------------------
    # COMMAND REGISTRATION
    # ------------------------

    def _register_commands(self):
        self.commands.register("new_file", self.editor_tabs.new_tab)
        self.commands.register("save_file", self.editor_tabs.save_file)
        self.commands.register("run_file", self.run_current_file)

    # ------------------------
    # FILE / FOLDER DIALOGS
    # ------------------------

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            self._open_file_with_lsp(file_path)

    def _open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            self.current_project_path = folder_path
            self.file_explorer.set_root_path(folder_path)

            project_name = folder_path.split("/")[-1]
            self.setWindowTitle(f"SlickIDE - {project_name}")



    def _open_file_with_lsp(self, file_path):
        self.editor_tabs.open_file(file_path)

        editor = self.editor_tabs.current_editor()
        if editor:
            apply_syntax_highlighter(editor, file_path)

        self.lsp_manager.start_for_file(file_path)

    # ------------------------
    # RUN LOGIC
    # ------------------------

    def run_current_file(self):
        editor = self.editor_tabs.current_editor()
        if not editor:
            return

        if editor.file_path is None:
            self.editor_tabs.save_file()
            if editor.file_path is None:
                return

        self.terminal.clear_terminal()
        self.process.start("python", [editor.file_path])

    def _handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode()
        self.terminal.write(text)

    def _handle_stderr(self):
        data = self.process.readAllStandardError()
        text = bytes(data).decode()
        self.terminal.write(text)

    def _process_finished(self):
        self.terminal.write("\n[Process finished]\n")