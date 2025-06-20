import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget, QFileSystemModel,
    QTableView, QSplitter, QHeaderView, QAbstractItemView, QMenu, QAction, QMessageBox,
    QInputDialog, QLineEdit, QFileDialog, QTextEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QDir, QItemSelectionModel, QModelIndex, QPropertyAnimation
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl


class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Провідник")
        self.setGeometry(100, 100, 1200, 800)

        self.tree_view = QTreeView()
        self.table_view = QTableView()

        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath("")
        self.tree_view.setModel(self.dir_model)
        self.tree_view.setRootIndex(self.dir_model.index(""))
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.setHeaderHidden(True)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.table_view.setModel(self.file_model)
        self.table_view.setRootIndex(self.file_model.index(""))
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.open_context_menu)

        self.tree_view.clicked.connect(self.on_tree_view_clicked)
        self.table_view.doubleClicked.connect(self.on_file_double_click)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.table_view)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

    def on_tree_view_clicked(self, index):
        path = self.dir_model.filePath(index)
        self.table_view.setRootIndex(self.file_model.index(path))

    def open_context_menu(self, position):
        menu = QMenu()

        open_action = QAction("Відкрити", self)
        open_action.triggered.connect(self.open_selected_file)
        menu.addAction(open_action)

        indexes = self.table_view.selectionModel().selectedIndexes()
        if indexes:
            file_path = self.file_model.filePath(indexes[0])
            if os.path.isfile(file_path) and file_path.endswith(('.txt', '.md', '.py', '.log')):
                edit_action = QAction("Редагувати документ", self)
                edit_action.triggered.connect(self.edit_selected_file)
                menu.addAction(edit_action)

        rename_action = QAction("Змінити назву", self)
        rename_action.triggered.connect(self.rename_selected_file)
        menu.addAction(rename_action)

        new_file_action = QAction("Створити новий файл", self)
        new_file_action.triggered.connect(self.create_new_file)
        menu.addAction(new_file_action)

        menu.exec_(self.table_view.viewport().mapToGlobal(position))

    def on_file_double_click(self, index):
        file_path = self.file_model.filePath(index)
        reply = QMessageBox.question(
            self, "Запуск файлу", f"Ви впевнені, що хочете відкрити {file_path}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def open_selected_file(self):
        indexes = self.table_view.selectionModel().selectedIndexes()
        if indexes:
            self.on_file_double_click(indexes[0])

    def edit_selected_file(self):
        indexes = self.table_view.selectionModel().selectedIndexes()
        if indexes:
            file_path = self.file_model.filePath(indexes[0])
            if os.path.isfile(file_path) and file_path.endswith(('.txt', '.md', '.py', '.log')):
                self.open_text_editor(file_path)

    def rename_selected_file(self):
        indexes = self.table_view.selectionModel().selectedIndexes()
        if indexes:
            file_path = self.file_model.filePath(indexes[0])
            dir_path = os.path.dirname(file_path)
            old_name = os.path.basename(file_path)

            new_name, ok = QInputDialog.getText(
                self, "Змінити назву", "Введіть нову назву:", QLineEdit.Normal, old_name)
            if ok and new_name:
                new_path = os.path.join(dir_path, new_name)
                try:
                    os.rename(file_path, new_path)
                    self.file_model.setData(
                        self.file_model.index(dir_path), "", Qt.EditRole)
                except Exception as e:
                    QMessageBox.critical(
                        self, "Помилка", f"Не вдалося перейменувати файл: {e}")

    def create_new_file(self):
        dir_path = self.file_model.filePath(self.table_view.rootIndex())
        if os.path.isdir(dir_path):
            file_name, ok = QInputDialog.getText(
                self, "Створити новий файл", "Введіть назву файлу:"
            )
            if ok and file_name:
                file_path = os.path.join(dir_path, file_name)
                with open(file_path, 'w') as file:
                    file.write("")

                self.file_model.setRootPath("")
                self.file_model.setRootPath(dir_path)
                self.table_view.setRootIndex(self.file_model.index(dir_path))

    def open_text_editor(self, file_path):
        self.editor_window = QMainWindow(self)
        self.editor_window.setWindowTitle(f"Редагування - {file_path}")
        self.editor_window.setGeometry(150, 150, 800, 600)

        text_edit = QTextEdit(self.editor_window)
        with open(file_path, 'r') as file:
            text_edit.setText(file.read())

        save_button = QPushButton("Зберегти")
        save_button.clicked.connect(lambda: self.save_file(file_path, text_edit))

        close_button = QPushButton("Закрити")
        close_button.clicked.connect(self.editor_window.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)

        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.editor_window.setCentralWidget(container)
        self.editor_window.show()

    def save_file(self, file_path, text_edit):
        with open(file_path, 'w') as file:
            file.write(text_edit.toPlainText())
        QMessageBox.information(self, "Збережено", f"Файл {file_path} збережено.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    explorer = FileExplorer()
    explorer.show()
    sys.exit(app.exec_())
