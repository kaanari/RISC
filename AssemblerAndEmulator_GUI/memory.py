from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import re

from memory import *
from buttons import *
from gui_elements import *
from emulator import *
import numpy as np

# Signaling PRoblems between GUI thread and Table Worker Thread.
# Worker thread changes GUI thread objects, it is not a good approach but it works now,
# At the beginning, there are some non-critical errors related with these issues.
# Can't be solved now. because I can't find any method to update table outsite the QT classes.
# Not a critical problem but it solves a crucial problem. Just gives an error at the beginning
class Memory:
    ADDRESS_LENGTH = 16
    MEM_SIZE = 2**(ADDRESS_LENGTH)

    def __init__(self):
        self.__memory = np.zeros(Memory.MEM_SIZE,dtype="int16")
        self.viewer = None

    def write(self, address, data):
        self.__memory[address] = data
        self.viewer.update_value(address)

    def read(self, address):
        #print(self.__memory[0:20])
        return self.__memory[address]

    def reset(self):
        self.__memory.fill(0)

    def block_write(self, starting_address, block):
        self.__memory[starting_address:len(block)] = block

    def copy(self):
        return self.__memory.copy()


class MemoryView(QTableWidget):

    def __init__(self, memory):
        super().__init__()

        self.memory = memory
        self.memory.viewer = self

        self.setRowCount(256)
        self.setColumnCount(2)
        header1 = QTableWidgetItem('Address')
        header1.setBackground(QColor(9, 66, 79))
        header1.setSizeHint(QSize(118, 25))
        self.setHorizontalHeaderItem(0, header1)

        header2 = QTableWidgetItem('Value')
        header2.setSizeHint(QSize(118, 25))
        header2.setBackground(QColor(9, 66, 79))
        self.setHorizontalHeaderItem(1, header2)

        self.verticalHeader().setVisible(False)
        self.setFixedWidth(256)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.current_page = 1
        self.page_size    = 256
        self.total_page   = int((2**16)/self.page_size)

        # BUTTONS AND NAVIGATION

        self.first_page_button = PicButton("./assets/first_page")
        self.back_button = PicButton("./assets/previous")
        self.forward_button = PicButton("./assets/next")
        self.last_page_button = PicButton("./assets/last_page")
        self.search_button = PicButton("./assets/search")
        self.search_button.setDisabled(False)

        self.name_label = QLabel("Memory Preview")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color:white;font-weight:bold;")

        self.search_box = QLineEdit()
        self.search_box.setFixedWidth(210)
        self.re_pattern = "((0x|0X)[0-9A-Fa-f]{4})|([0-9]{1,5})"
        pattern = QRegExp(self.re_pattern)
        self.search_box.setValidator(QRegExpValidator(pattern))
        self.search_box.returnPressed.connect(self.search)
        self.search_box.setAlignment(Qt.AlignCenter)
        self.search_box.setPlaceholderText("Hex(0xFFFF) or Integer(65535)")

        self.search_label = QLabel("Search Address: ")
        self.search_label.setFixedWidth(100)
        self.search_label.setAlignment(Qt.AlignCenter)

        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setText(str(self.current_page)+" / "+str(self.total_page))

        self.forward_button.setDisabled(False)
        self.last_page_button.setDisabled(False)

        self.forward_button.clicked.connect(self.next_page)
        self.back_button.clicked.connect(self.previous_page)
        self.first_page_button.clicked.connect(self.first_page)
        self.last_page_button.clicked.connect(self.last_page)
        self.search_button.clicked.connect(self.search_clicked)

        self.preview_format = 0
        # 0 -> HEX, 1 -> Unsigned Int, 2-> Signed Int

        self.horizontal_line = QHLine()
        self.horizontal_line2 = QHLine()
        self.horizontal_line3 = QHLine()
        self.horizontal_line4 = QHLine()
        self.vertical_line = QVLine()

        self.hide()

        self.worker = Worker(self)
        self.worker.start()

    def update_page_label(self):
        self.page_label.setText(str(self.current_page) + " / " + str(self.total_page))

    def last_page(self):
        self.current_page = self.total_page - 1
        self.next_page()

    def first_page(self):
        self.current_page = 2
        self.previous_page()

    def next_page(self):

        self.current_page += 1

        self.update_values()

        self.update_page_label()

        if self.current_page == self.total_page:
            self.forward_button.setDisabled(True)
            self.last_page_button.setDisabled(True)

        self.back_button.setDisabled(False)
        self.first_page_button.setDisabled(False)

    def previous_page(self):

        self.current_page -= 1

        self.update_values()
        self.update_page_label()

        if self.current_page == 1:
            self.back_button.setDisabled(True)
            self.first_page_button.setDisabled(True)

        self.forward_button.setDisabled(False)
        self.last_page_button.setDisabled(False)

    def full_layout(self):
        wrapper_layout = QHBoxLayout()
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        #search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)

        layout.addWidget(self.name_label)
        layout.addWidget(self.horizontal_line)
        #layout.addWidget(self.search_label) #
        layout.addLayout(search_layout)
        layout.addWidget(self.horizontal_line2)
        layout.addWidget(self)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.first_page_button)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.page_label)
        button_layout.addWidget(self.forward_button)
        button_layout.addWidget(self.last_page_button)
        layout.addWidget(self.horizontal_line3)
        layout.addLayout(button_layout)
        layout.addWidget(self.horizontal_line4)
        wrapper_layout.addWidget(self.vertical_line)
        wrapper_layout.addLayout(layout)
        return wrapper_layout

    def update_values(self):

        self.worker.signal.connect(self.finished)
        self.worker.start()

    def update_value(self, address):

        if self.calculate_page(address) == self.current_page:
            self.update_values()

    def finished(self):
        if not self.isHidden():
            self.hide()
            self.show()

    def search(self):
        number_str = self.search_box.text().upper()
        self.search_box.setText("")
        number = 0

        if number_str[:2] == "0X":
            number = int(number_str[2:], 16)

        else:
            number = int(number_str)

        if number >= 2**16:
            # Console a bilgi yazdırılabilir
            return None

        self.current_page = self.calculate_page(number)
        if self.current_page == 1:
            self.current_page += 1
            self.previous_page()

        else:
            self.current_page -= 1
            self.next_page()

    def hide(self):
        super().hide()
        self.search_box.hide()
        self.search_button.hide()
        self.horizontal_line.hide()
        self.horizontal_line2.hide()
        self.horizontal_line3.hide()
        self.horizontal_line4.hide()
        self.name_label.hide()

        self.first_page_button.hide()
        self.back_button.hide()
        self.page_label.hide()
        self.forward_button.hide()
        self.last_page_button.hide()
        self.vertical_line.hide()

    def show(self):
        super().show()
        self.search_box.show()
        self.search_button.show()
        self.horizontal_line.show()
        self.horizontal_line2.show()
        self.horizontal_line3.show()
        self.horizontal_line4.show()
        self.name_label.show()

        self.first_page_button.show()
        self.back_button.show()
        self.page_label.show()
        self.forward_button.show()
        self.last_page_button.show()
        self.vertical_line.show()

    def calculate_page(self, address):
        page_num = int(address / self.page_size) + 1
        return page_num

    def search_clicked(self):
        check_flag = re.fullmatch(self.re_pattern, self.search_box.text())

        if not check_flag == None:
            self.search()


class Worker(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self,mem_view):
        super().__init__()

        self.mem_view = mem_view

        self.value_item = QTableWidgetItem()
        self.value_item.setTextAlignment(Qt.AlignCenter)
        self.value_item.setSizeHint(QSize(118, 15))
        self.address_item = QTableWidgetItem()
        self.address_item.setTextAlignment(Qt.AlignCenter)
        self.address_item.setBackground(QColor(67, 68, 69))
        self.address_item.setFlags(Qt.ItemIsEnabled)
        self.value_item.setSizeHint(QSize(118, 15))


    def run(self):

        if self.mem_view.preview_format == 0:
            self.preview_format = "0x{:04X}"

        else:
            self.preview_format = "{:5d}"

        self.lower_bound = (self.mem_view.current_page - 1) * self.mem_view.page_size
        self.upper_bound = self.mem_view.current_page * self.mem_view.page_size

        """Long-running task."""
        for idx, address in enumerate(range(self.lower_bound, self.upper_bound)):
            self.address_item.setText(self.preview_format.format(address))
            self.mem_view.setItem(idx, 0, QTableWidgetItem(self.address_item))

            value = self.mem_view.memory.read(address)

            if self.mem_view.preview_format == 0 or self.mem_view.preview_format == 1:
                if value < 0:
                    # 2's Complement
                    value = 65535 - abs(value) + 1

            self.value_item.setText(self.preview_format.format(value))
            self.mem_view.setItem(idx, 1, QTableWidgetItem(self.value_item))

        self.signal.emit("")
