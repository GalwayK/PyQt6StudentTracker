import PyQt6
import sys
import sqlite3
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QLineEdit, \
    QPushButton, QGridLayout, QWidget, QToolBar, QStatusBar, QLabel, QHBoxLayout, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.width = 800
        self.setFixedWidth(self.width)

        self.setWindowTitle("Student Management System")
        self.file_menu_item = self.menuBar().addMenu("&File")
        self.help_menu_item = self.menuBar().addMenu("&Help")
        self.edit_menu_item = self.menuBar().addMenu("&Edit")

        self.add_student_action = QAction(QIcon("files/icons/add.png"), "Add Student", self)
        self.search_student_action = QAction(QIcon("files/icons/search.png"), "Search", self)

        self.file_menu_item.addAction(self.add_student_action)
        self.edit_menu_item.addAction(self.search_student_action)

        self.add_student_action.triggered.connect(self.insert_student)
        self.search_student_action.triggered.connect(self.find_student)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about)

        self.help_menu_item.addAction(self.about_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Student ID", "Student Name", "Course", "Phone Number"))
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, int(self.width * .10))
        for i in range(1, 4):
            self.table.setColumnWidth(i, int(self.width * .3))

        self.toolbar = QToolBar()
        self.toolbar.setMovable(True)

        self.toolbar.addAction(self.add_student_action)
        self.toolbar.addAction(self.search_student_action)

        self.addToolBar(self.toolbar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.table.cellClicked.connect(self.show_cell_status)

        self.grid_layout.addWidget(self.table, 0, 0)

        self.setLayout(self.grid_layout)

        self.central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(self.central_widget)
        self.load_data()

    def load_data(self):
        connection = sqlite3.connect("files/database.db")
        result = connection.execute("SELECT * FROM students").fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert_student(self):
        dialog = self.InsertDialog()
        dialog.exec()
        self.load_data()

    def find_student(self):
        dlg = self.SearchDialog()
        dlg.exec()

    def highlight_student(self, name):
        print(f"Here: {name}")
        items = self.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            self.table.item(item.row(), 1).setSelected(True)

    def show_cell_status(self):
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.update_student)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete_student)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def update_student(self):
        dialog = self.UpdateDialog()
        dialog.exec()
        self.load_data()

    def delete_student(self):
        dialog = self.DeleteDialog()
        dialog.exec()
        self.load_data()

    def show_about(self):
        dialog = self.AboutDialog()
        dialog.exec()

    class AboutDialog(QMessageBox):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("About")
            about_text = """This app was created as part of Ardit Sulce's
Python Mega Course, On Udemy
It was created by Kyle Galway"""
            self.setText(about_text)

    class DeleteDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Delete Student Dialog")
            layout = QVBoxLayout()

            table_row = window.table.currentRow()
            self.student_id = window.table.item(table_row, 0).text()

            self.student_name = QLabel(f"Name: {window.table.item(table_row, 1).text()}")

            self.student_course = QLineEdit(f"Course: {window.table.item(table_row, 2).text()}")

            self.student_phone = QLineEdit(f"Mobile: {window.table.item(table_row, 3).text()}")

            buttons = QHBoxLayout()

            self.confirm_button = QPushButton("Confirm Delete")
            self.confirm_button.clicked.connect(self.delete_student)

            self.cancel_button = QPushButton("Cancel Delete")
            self.cancel_button.clicked.connect(self.cancel_delete)

            buttons.addWidget(self.confirm_button)
            buttons.addWidget(self.cancel_button)
            button_widget = QWidget()
            button_widget.setLayout(buttons)

            layout.addWidget(self.student_name)
            layout.addWidget(self.student_course)
            layout.addWidget(self.student_phone)
            layout.addWidget(button_widget)

            self.setLayout(layout)

        def delete_student(self):
            connection = sqlite3.connect("files/database.db")
            connection.execute("DELETE FROM STUDENTS WHERE ID = ?", (self.student_id,))
            connection.commit()
            confirmation_dialog = QMessageBox()
            confirmation_dialog.setWindowTitle("Successful Deletion")
            confirmation_dialog.setText(f"Successfully deleted student #{self.student_id}")
            confirmation_dialog.exec()
            self.close()

        def cancel_delete(self):
            self.close()

    class UpdateDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Update Student Dialog")
            layout = QVBoxLayout()

            table_row = window.table.currentRow()
            self.student_id = window.table.item(table_row, 0).text()

            self.student_name = QLineEdit(window.table.item(table_row, 1).text())

            self.student_course = QLineEdit(window.table.item(table_row, 2).text())

            self.student_phone = QLineEdit(window.table.item(table_row, 3).text())

            self.submit_button = QPushButton("Update Student")
            self.submit_button.clicked.connect(self.update_student)

            layout.addWidget(self.student_name)
            layout.addWidget(self.student_course)
            layout.addWidget(self.student_phone)
            layout.addWidget(self.submit_button)

            self.setLayout(layout)

        def update_student(self):
            student_name = self.student_name.text().strip(" ")
            student_course = self.student_course.text().strip(" ")
            student_phone = self.student_phone.text().strip(" ")
            student_tuple = (student_name, student_course, student_phone, self.student_id)
            if "" in student_tuple:
                return None
            else:
                connection = sqlite3.connect("files/database.db")
                connection.execute("UPDATE STUDENTS SET name = ?, course = ?, mobile = ? "
                                   "WHERE id = ?", student_tuple)
                connection.commit()
                self.close()
                return None

    class InsertDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Insert Student Dialog")
            layout = QVBoxLayout()

            self.student_name = QLineEdit()
            self.student_name.setPlaceholderText("Student Name")

            self.student_course = QLineEdit()
            self.student_course.setPlaceholderText("Student Course")

            self.student_phone = QLineEdit()
            self.student_phone.setPlaceholderText("Phone Number")

            self.submit_button = QPushButton("Submit Student")
            self.submit_button.clicked.connect(self.add_student)

            layout.addWidget(self.student_name)
            layout.addWidget(self.student_course)
            layout.addWidget(self.student_phone)
            layout.addWidget(self.submit_button)

            self.setLayout(layout)

        def add_student(self):
            student_name = self.student_name.text().strip(" ")
            student_course = self.student_course.text().strip(" ")
            student_phone = self.student_phone.text().strip(" ")

            if "" in [student_name, student_phone, student_course]:
                print("Something went wrong. You may be missing a field in your entry.")
                return None
            else:
                self.insert_student(student_name, student_course, student_phone)

        @staticmethod
        def insert_student(name, course, phone):
            try:
                connection = sqlite3.connect("files/database.db")
                connection.execute("INSERT INTO students (name, course, mobile) values (?, ?, ?)",
                                   (name, course, phone))
                connection.commit()
                connection.close()
            except Exception as error:
                print(error)

    class SearchDialog(QDialog):
        def __init__(self):
            super().__init__()
            vertical_layout = QVBoxLayout()

            self.setWindowTitle("Search Student Dialog")

            self.student_name = QLineEdit()
            self.student_name.setPlaceholderText("Student Name")

            self.submit_button = QPushButton("Submit Search")
            self.submit_button.clicked.connect(self.search_student)

            self.student = None

            vertical_layout.addWidget(self.student_name)
            vertical_layout.addWidget(self.submit_button)

            self.setLayout(vertical_layout)

        def search_student(self):
            if self.student_name.text() == " ":
                print("Feh")
                return None
            else:
                self.student = self.student_name.text()
                window.highlight_student(self.student)


application = QApplication(sys.argv)
window = MainWindow()
window.show()
application.exec()

