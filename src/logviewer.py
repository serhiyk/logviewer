#!/usr/bin/python
import sys
import re
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL


class MainWindow(QtGui.QWidget):
    error_words = ['err']
    warning_words = ['wrn', 'warning', 'warn']
    debug_words = ['dbg', 'debug']
    info_words = ['log', 'info']

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.parent = parent
        self.lastMatch = None
        self.content = []
        self.file_data = ''
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Log viewer')
        self.setStyleSheet("QGroupBox { padding-top: 10px; border:1px solid gray; }")
        self.main_layout = QtGui.QGridLayout(self)

        self.open_button = QtGui.QPushButton("Open", self)
        self.connect(self.open_button, SIGNAL('clicked()'), self.open_button_handler)
        self.pure_button = QtGui.QPushButton("Pure", self)
        self.connect(self.pure_button, SIGNAL('clicked()'), self.pure_button_handler)
        self.filter_button = QtGui.QPushButton("Filter", self)
        self.connect(self.filter_button, SIGNAL('clicked()'), self.filter_button_handler)
        self.viewer = QtGui.QTextEdit(self)

        self.find_group = QtGui.QGroupBox("Find", self)
        self.find_group_layout = QtGui.QVBoxLayout(self.find_group)
        self.find_field = QtGui.QLineEdit(self)
        self.find_group_layout.addWidget(self.find_field)
        self.whole_words = QtGui.QCheckBox("Whole words", self)
        self.find_group_layout.addWidget(self.whole_words)
        self.all_words = QtGui.QCheckBox("All words", self)
        self.find_group_layout.addWidget(self.all_words)
        self.case_sens = QtGui.QCheckBox("Case sens", self)
        self.find_group_layout.addWidget(self.case_sens)
        self.find_button = QtGui.QPushButton("Find", self)
        self.connect(self.find_button, SIGNAL('clicked()'), self.find_button_handler)
        self.find_group_layout.addWidget(self.find_button)

        self.black_filter_group = QtGui.QGroupBox("Black filter", self)
        self.black_filter_group_layout = QtGui.QVBoxLayout(self.black_filter_group)
        self.black_filter_field = QtGui.QTextEdit(self)
        self.black_filter_group_layout.addWidget(self.black_filter_field)

        self.white_filter_group = QtGui.QGroupBox("White filter", self)
        self.white_filter_group_layout = QtGui.QVBoxLayout(self.white_filter_group)
        self.white_filter_field = QtGui.QTextEdit(self)
        self.white_filter_group_layout.addWidget(self.white_filter_field)

        self.colour_group = QtGui.QGroupBox("Enable colour", self)
        self.colour_group_layout = QtGui.QVBoxLayout(self.colour_group)
        self.enable_error_colour = QtGui.QCheckBox("Error", self)
        self.colour_group_layout.addWidget(self.enable_error_colour)
        self.enable_warning_colour = QtGui.QCheckBox("Warning", self)
        self.colour_group_layout.addWidget(self.enable_warning_colour)

        self.log_filter_group = QtGui.QGroupBox("Log filter", self)
        self.log_filter_group_layout = QtGui.QVBoxLayout(self.log_filter_group)
        self.enable_error_filter = QtGui.QCheckBox("Error", self)
        self.enable_error_filter.setChecked(True)
        self.log_filter_group_layout.addWidget(self.enable_error_filter)
        self.enable_warning_filter = QtGui.QCheckBox("Warning", self)
        self.enable_warning_filter.setChecked(True)
        self.log_filter_group_layout.addWidget(self.enable_warning_filter)
        self.enable_debug_filter = QtGui.QCheckBox("Debug", self)
        self.enable_debug_filter.setChecked(True)
        self.log_filter_group_layout.addWidget(self.enable_debug_filter)
        self.enable_info_filter = QtGui.QCheckBox("Info", self)
        self.enable_info_filter.setChecked(True)
        self.log_filter_group_layout.addWidget(self.enable_info_filter)

        self.main_layout.setColumnMinimumWidth(0, 50)
        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 5)
        self.main_layout.addWidget(self.open_button, 0, 0, 1, 1)
        self.main_layout.addWidget(self.pure_button, 1, 0, 1, 1)
        self.main_layout.addWidget(self.filter_button, 2, 0, 1, 1)
        self.main_layout.addWidget(self.find_group, 3, 0, 1, 1)
        self.main_layout.addWidget(self.black_filter_group, 4, 0, 1, 1)
        self.main_layout.addWidget(self.white_filter_group, 5, 0, 1, 1)
        self.main_layout.addWidget(self.colour_group, 6, 0, 1, 1)
        self.main_layout.addWidget(self.log_filter_group, 7, 0, 1, 1)
        self.main_layout.addWidget(self.viewer, 0, 1, 9, 2)

        self.find_action = QtGui.QAction(QtGui.QIcon(), "Find", self)
        self.find_action.setShortcut("Ctrl+F")
        self.connect(self.find_action, SIGNAL("triggered()"), self.find_button_handler)
        self.addAction(self.find_action)

        self.show()

    def open_button_handler(self):
        dlg = QtGui.QFileDialog()
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            with open(filenames[0], 'r') as f:
                self.file_data = f.read()

    def find_button_handler(self):
        text = self.viewer.toPlainText()
        query = unicode(self.find_field.text())
        if self.whole_words.isChecked():
            query = r'\W' + query + r'\W'
        elif self.all_words.isChecked():
            query = r'.*'.join(query.split())
        flags = 0 if self.case_sens.isChecked() else re.IGNORECASE
        pattern = re.compile(query, flags)
        start = self.lastMatch.start() + 1 if self.lastMatch else 0
        self.lastMatch = pattern.search(text, start)
        if self.lastMatch:
            start = self.lastMatch.start()
            end = self.lastMatch.end()
            if self.whole_words.isChecked():
                start += 1
                end -= 1
            self.moveCursor(start, end)
        else:
            self.viewer.moveCursor(QtGui.QTextCursor.End)

    def pure_button_handler(self):
        self.viewer.setText(self.file_data)

    def filter_button_handler(self):
        filter_words = []
        if not self.enable_error_filter.isChecked():
            filter_words.extend(self.error_words)
        if not self.enable_warning_filter.isChecked():
            filter_words.extend(self.warning_words)
        if not self.enable_debug_filter.isChecked():
            filter_words.extend(self.debug_words)
        if not self.enable_info_filter.isChecked():
            filter_words.extend(self.info_words)
        for line in self.black_filter_field.toPlainText().split('\n'):
            if len(line) > 0:
                filter_words.append(r'.*'.join(str(line).split()))
        if len(filter_words) > 0:
            file_data = re.sub(r'.*(' + r'|'.join(filter_words) + r').*\n?', '', self.file_data, flags=re.MULTILINE | re.IGNORECASE)
        else:
            file_data = self.file_data
        filter_words = []
        for line in self.white_filter_field.toPlainText().split('\n'):
            if len(line) > 0:
                filter_words.append(r'.*'.join(str(line).split()))
        if len(filter_words) > 0:
            file_data = re.sub(r'^((?!' + r'|'.join(filter_words) + r').)*$\n?', r'', file_data, flags=re.MULTILINE | re.IGNORECASE)
        filter_words = []
        if self.enable_error_colour.isChecked():
            filter_words.extend(self.error_words)
        if self.enable_warning_colour.isChecked():
            filter_words.extend(self.warning_words)
        if len(filter_words) == 0:
            self.viewer.setText(file_data)
            return
        file_data = re.sub(r'(.*(' + r'|'.join(filter_words) + r').*)', r'<font color="Red">\1</font>', file_data, flags=re.MULTILINE | re.IGNORECASE)
        file_data = file_data.replace('\n', '<br>')
        self.viewer.setHtml(file_data)

    def moveCursor(self, start, end):
        cursor = self.viewer.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start)
        self.viewer.setTextCursor(cursor)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
