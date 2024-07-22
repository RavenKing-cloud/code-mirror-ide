import sys
import os
from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QToolBar, QAction, QComboBox, QFileDialog, QMessageBox, QShortcut, QFontDialog, QInputDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QKeySequence

# TODO: Add syntax highlighting for more languages to html

class CodeMirrorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mirror IDE')
        self.setGeometry(100, 100, 800, 600)

        self.current_file = None
        self.unsaved_changes = False

        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create a QWebEngineView
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

        # Get the absolute path of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the absolute path to the HTML file
        html_path = os.path.join(current_dir, 'codemirror.html')

        # Load the CodeMirror HTML file
        self.web_view.setUrl(QUrl.fromLocalFile(html_path))

        # Create the toolbar
        self.create_toolbar()

        # Track unsaved changes
        self.web_view.page().runJavaScript('editor.on("change", function() { window.unsavedChanges = true; });')

        # Add shortcuts
        self.add_shortcuts()

    def create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        # Create file menu actions
        file_menu = self.menuBar().addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        # Create theme selection combo box
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "default", "3024-day", "3024-night", "abcdef", "base16-dark",
            "base16-light", "bespin", "dracula", "eclipse", "monokai",
            "solarized", "twilight", "material-darker", "panda-syntax"
        ])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        toolbar.addWidget(self.theme_combo)

        # Create mode selection combo box
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "python", "javascript", "xml", "css", "c", "cpp", "csharp",
            "lua", "vb", "sql", "json", "java"
        ])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        toolbar.addWidget(self.mode_combo)

        # Create settings menu actions
        settings_menu = self.menuBar().addMenu("Settings")

        font_size_action = QAction("Font Size", self)
        font_size_action.triggered.connect(self.change_font_size)
        settings_menu.addAction(font_size_action)

        font_type_action = QAction("Font Type", self)
        font_type_action.triggered.connect(self.change_font_type)
        settings_menu.addAction(font_type_action)

    @pyqtSlot(str)
    def change_theme(self, theme):
        self.web_view.page().runJavaScript(f'changeTheme("{theme}");')
        self.adapt_window_color(theme)

    @pyqtSlot(str)
    def change_mode(self, mode):
        self.web_view.page().runJavaScript(f'changeMode("{mode}");')

    def adapt_window_color(self, theme):
        dark_themes = [
            "3024-night", "base16-dark", "dracula", "monokai", "solarized",
            "twilight", "material-darker", "panda-syntax"
        ]
        if theme in dark_themes:
            self.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
            self.web_view.setStyleSheet("background-color: #2e2e2e;")
        else:
            self.setStyleSheet("background-color: #ffffff; color: #000000;")
            self.web_view.setStyleSheet("background-color: #ffffff;")

    def new_file(self):
        if self.unsaved_changes:
            response = QMessageBox.question(self, "Unsaved Changes",
                                            "You have unsaved changes. Do you want to save them?",
                                            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if response == QMessageBox.Save:
                self.save_file()
            elif response == QMessageBox.Cancel:
                return
        self.web_view.page().runJavaScript('editor.setValue("");')
        self.current_file = None
        self.unsaved_changes = False
        self.setWindowTitle('CodeMirror in PyQt')

    def open_file(self):
        if self.unsaved_changes:
            response = QMessageBox.question(self, "Unsaved Changes",
                                            "You have unsaved changes. Do you want to save them?",
                                            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if response == QMessageBox.Save:
                self.save_file()
            elif response == QMessageBox.Cancel:
                return
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Python Files (*.py);;JavaScript Files (*.js);;XML Files (*.xml);;CSS Files (*.css);;C Files (*.c);;C++ Files (*.cpp);;C# Files (*.cs);;Lua Files (*.lua);;VB Files (*.vb);;CSV Files (*.csv);;JSON Files (*.json);;Java Files (*.java)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                content = file.read()
                self.web_view.page().runJavaScript(f'editor.setValue(`{content}`);')
                self.current_file = file_name
                self.unsaved_changes = False
                self.setWindowTitle(f'CodeMirror in PyQt - {file_name}')

    def save_file(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "All Files (*);;Python Files (*.py);;JavaScript Files (*.js);;XML Files (*.xml);;CSS Files (*.css);;C Files (*.c);;C++ Files (*.cpp);;C# Files (*.cs);;Lua Files (*.lua);;VB Files (*.vb);;CSV Files (*.csv);;JSON Files (*.json);;Java Files (*.java)", options=options)
        if file_name:
            self.save_to_file(file_name)
            self.current_file = file_name
            self.unsaved_changes = False
            self.setWindowTitle(f'CodeMirror in PyQt - {file_name}')

    def save_to_file(self, file_name):
        self.web_view.page().runJavaScript('editor.getValue();', self.get_code_from_editor(file_name))

    def get_code_from_editor(self, file_name):
        def callback(code):
            with open(file_name, 'w') as file:
                file.write(code)
            self.unsaved_changes = False
        return callback

    def add_shortcuts(self):
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.new_file)

        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self.open_file)

        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_file)

        save_as_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        save_as_shortcut.activated.connect(self.save_file_as)

    def change_font_size(self):
        # Placeholder for the font size adjustment code
        size, ok = QInputDialog.getInt(self, 'Font Size', 'Enter font size:', min=10, max=48)
        if ok:
            self.web_view.page().runJavaScript(f'document.querySelector(".CodeMirror").style.fontSize="{size}px";')

    def change_font_type(self):
        # Placeholder for the font type adjustment code
        font, ok = QFontDialog.getFont()
        if ok:
            font_family = font.family()
            self.web_view.page().runJavaScript(f'document.querySelector(".CodeMirror").style.fontFamily="{font_family}";')

    def closeEvent(self, event):
        if self.unsaved_changes:
            response = QMessageBox.question(self, "Unsaved Changes",
                                            "You have unsaved changes. Do you want to save them?",
                                            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if response == QMessageBox.Save:
                self.save_file()
            elif response == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = CodeMirrorWindow()
    main_win.show()
    sys.exit(app.exec_())