from PyQt5.QtWidgets import *
from PyQt5 import QtCore,QtGui

import sys
import hashlib
from assembler import  Assembler

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time


# ToDo: Execute Jump Instruction and Memory instructions
# When there is an eerror, highlight error line!

lineBarColor = QColor("#39444a")
lineHighlightColor  = QColor("#39444a")


class DebugButtons(QVBoxLayout):

    def __init__(self):
        super().__init__()
        buttons = QHBoxLayout()

        self.back_button = PicButton("./assets/left_arrow")
        self.stop_run_button = PicButton("./assets/run")
        self.forward_button = PicButton("./assets/right_arrow")
        self.reset_button = PicButton("./assets/reset")

        self.quit_debug_mode_button = PicButton("./assets/close")

        self.time_slider = StepSlider()

        buttons.addWidget(self.back_button)
        buttons.addWidget(self.stop_run_button)
        buttons.addWidget(self.forward_button)
        buttons.addWidget(self.reset_button)
        buttons.addWidget(self.quit_debug_mode_button)
        buttons.addWidget(self.time_slider.slider_text)
        buttons.addWidget(self.time_slider)
        buttons.addWidget(self.time_slider.slider_value)

        self.debug_line = QHLine()
        self.debug_line.setStyleSheet("background-color: #126e82;")
        self.debug_line.hide()

        self.addLayout(buttons)
        self.addWidget(self.debug_line)
        self.hide()

    def show(self):

        self.back_button.show()
        self.stop_run_button.show()
        self.forward_button.show()
        self.reset_button.show()
        self.quit_debug_mode_button.show()
        self.debug_line.show()
        self.time_slider.show()

    def hide(self):

        self.back_button.hide()
        self.stop_run_button.hide()
        self.forward_button.hide()
        self.reset_button.hide()
        self.quit_debug_mode_button.hide()
        self.debug_line.hide()
        self.time_slider.hide()


class PicButton(QAbstractButton):
    def __init__(self, pixmap, size = (20,40),parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = QPixmap(pixmap+".png")
        self.pixmap_active = QPixmap(pixmap+"_active.png")
        self.pixmap_hover = QPixmap(pixmap+"_hover.png")
        self.size = size

        self.pressed.connect(self.update)
        self.released.connect(self.update)
        self.setDisabled(True)

        self.setFixedWidth(size[1])
        self.setFixedHeight(size[0])

    def paintEvent(self, event):
        pix = self.pixmap

        if self.isEnabled():
            if self.underMouse():
                pix = self.pixmap_hover
            else:
                pix = self.pixmap_active

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def change_image(self,location):
        self.pixmap = QPixmap(location + ".png")
        self.pixmap_active = QPixmap(location + "_active.png")
        self.pixmap_hover = QPixmap(location + "_hover.png")

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(self.size[0],self.size[1])


class StepSlider(QSlider):

    def __init__(self):
        super().__init__()
        self.setOrientation(Qt.Horizontal)
        self.setMaximumWidth(300)
        self.setMaximum(1000)
        self.setMinimum(0)

        self.valueChanged.connect(self.update_step_time)

        self.setStyleSheet(
            "QSlider::groove:horizontal {\
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop: 0 #126e82, stop: 1 #8cebff);\
            height: 4px;\
            border-radius: 2px;\
            }QSlider::handle:horizontal {\
            background-color: #bababa;\
            height: 8px;\
            width: 8px;\
            margin: -8px 2; \
            }")

        self.slider_text = QLabel()
        self.slider_text.setText("Step Delay:")
        self.slider_text.setStyleSheet("color:#999999")
        self.slider_text.setFixedWidth(70)
        self.slider_text.setAlignment(Qt.AlignCenter)

        self.slider_value = QLabel()
        self.slider_value.setText("0 ms")
        self.slider_value.setFixedWidth(60)
        self.slider_value.setAlignment(Qt.AlignVCenter)

        self.hide()

    def mousePressEvent(self, QMouseEvent):
        super(StepSlider,self).mousePressEvent(QMouseEvent)
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            val = self.pixel_pos_to_range(QMouseEvent.pos())
            self.setValue(val)

    def pixel_pos_to_range(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == QtCore.Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1;
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == QtCore.Qt.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                               sliderMax - sliderMin, opt.upsideDown)

    def update_step_time(self,value):
        self.slider_value.setText(str(value)+" ms")

    def hide(self):
        super().hide()
        self.slider_text.hide()
        self.slider_value.hide()

    def show(self):
        super().show()
        self.slider_text.show()
        self.slider_value.show()


class OperationControlBlock:

    def __init__(self, operation, PC, registers, operation_index):
        self.operation = operation
        self.operation_index = operation_index
        self.PC = PC
        self.registers = registers

    def line(self):
        return self.operation.line


class OperationStack:

    def __init__(self):

        self.__stack = []

    def push(self,operation_control_block):
        self.__stack.append(operation_control_block)
        return True

    def pop(self):
        if len(self.__stack) != 0:
            return self.__stack.pop()
        else:
            return False

    def clear(self):
        self.__stack = []
        return True

    def print(self):
        for op in self.__stack:
            print(op.operation, op.PC, op.registers)

    def isEmpty(self):
        return len(self.__stack) == 0


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class NumberBar(QWidget):
    def __init__(self, parent = None):
        super(NumberBar, self).__init__(parent)
        self.editor = parent
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.editor.blockCountChanged.connect(self.update_width)
        self.editor.updateRequest.connect(self.update_on_scroll)
        self.update_width('1')

    def update_on_scroll(self, rect, scroll):
        if self.isVisible():
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update()

    def update_width(self, string):
        width = self.fontMetrics().width(str(string)) + 10
        if self.width() != width:
            self.setFixedWidth(width)

    def paintEvent(self, event):
        if self.isVisible():
            block = self.editor.firstVisibleBlock()
            height = self.fontMetrics().height()
            number = block.blockNumber()
            painter = QPainter(self)
            painter.fillRect(event.rect(), lineBarColor)
            #painter.drawRect(0, 0, event.rect().width() - 1, event.rect().height() - 1)
            font = painter.font()
            current_block = self.editor.textCursor().block().blockNumber() + 1

            condition = True
            while block.isValid() and condition:
                block_geometry = self.editor.blockBoundingGeometry(block)
                offset = self.editor.contentOffset()
                block_top = block_geometry.translated(offset).top()
                number += 1

                rect = QRect(0, block_top, self.width() - 5, height)

                if number == current_block:
                    font.setBold(True)
                    painter.setPen(QColor(50, 130, 184))
                else:
                    painter.setPen(Qt.white)
                    font.setBold(False)

                painter.setFont(font)

                painter.drawText(rect, Qt.AlignRight, '%i'%number)

                if block_top > event.rect().bottom():
                    condition = False

                block = block.next()

            painter.end()


class CodeWindow(QPlainTextEdit):
    def __init__(self, parent = None):
        super(CodeWindow, self).__init__(parent)
        self.labels = []
        #self.setStyleSheet("background-color: #CFD8DC;")


        # Setup the regex engine
        #self.cursorPositionChanged.connect(self.line_highlight)

    def colorize(self):
        format = QtGui.QTextCharFormat()
        # format.setBackground(QtGui.QBrush(QtGui.QColor("red")))
        format.setForeground(QtGui.QColor(255, 255, 255))
        self.blockSignals(True)
        cursor = self.textCursor()
        cursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)

        cursor.setPosition(len(self.toPlainText()), QtGui.QTextCursor.KeepAnchor)

        cursor.setCharFormat(format)
        self.blockSignals(False)
        self.label_search()
        self.instruction_search()
        self.register_search()

    def label_search(self):
        format = QtGui.QTextCharFormat()
        #format.setBackground(QtGui.QBrush(QtGui.QColor("red")))
        format.setForeground(QtGui.QColor(93, 166, 90))
        format.setFontWeight(QtGui.QFont.Bold)
        cursor = self.textCursor()
        pattern = "[a-zA-Z]+\w*( |\s)*:"


        regex = QtCore.QRegExp(pattern)

        # Process the displayed document
        self.labels = []
        pos = 0
        index = regex.indexIn(self.toPlainText(), pos)

        self.blockSignals(True)

        while (index != -1):
            # Select the matched text and apply the desired format
            den = regex.matchedLength()
            label_name = regex.capturedTexts()[0][:-1].strip()
            if label_name not in self.labels:
                #print("APPEND ",label_name)
                self.labels.append(label_name)
            cursor.setPosition(index, QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(index + den, QtGui.QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            # Move to the next match
            pos = index + den
            index = regex.indexIn(self.toPlainText(), pos)

        #print(self.labels)
        if self.labels:
            # Process the displayed documen
            str_label_list = '|'.join(self.labels)
            #print(str_label_list)
            pattern = "({})( |\s)+".format(str_label_list)
            pattern = "(( |\s)+|,)"+pattern
            regex = QtCore.QRegExp(pattern)

            # Process the displayed document
            pos = 0
            index = regex.indexIn(self.toPlainText(), pos)

            while (index != -1):
                # Select the matched text and apply the desired format
                den = regex.matchedLength()
                cursor.setPosition(index, QtGui.QTextCursor.MoveAnchor)
                cursor.setPosition(index + den, QtGui.QTextCursor.KeepAnchor)
                cursor.setCharFormat(format)
                # Move to the next match
                pos = index + den
                index = regex.indexIn(self.toPlainText(), pos)

            pattern = ","
            regex = QtCore.QRegExp(pattern)

            # Process the displayed document
            pos = 0
            index = regex.indexIn(self.toPlainText(), pos)

            while (index != -1):
                # Select the matched text and apply the desired format
                den = regex.matchedLength()
                cursor.setPosition(index, QtGui.QTextCursor.MoveAnchor)
                cursor.setPosition(index + den, QtGui.QTextCursor.KeepAnchor)
                cursor.setCharFormat(QtGui.QTextCharFormat())
                # Move to the next match
                pos = index + den
                index = regex.indexIn(self.toPlainText(), pos)

        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QBrush(QtGui.QColor("transparent")))

        self.setCurrentCharFormat(format)




        self.blockSignals(False)

    def instruction_search(self):
        format = QtGui.QTextCharFormat()
        #format.setBackground(QtGui.QBrush(QtGui.QColor("red")))
        format.setFontWeight(QtGui.QFont.Bold)

        cursor = self.textCursor()
        pattern = "(^|\n) *\s*(ADD|SUB|AND|OR|NOT|XOR|CMP|SHL|SHR|LOAD|STORE|JUMP|JZ|JNZ|LOADI) +"
        regex = QtCore.QRegExp(pattern)

        # Process the displayed document
        pos = 0
        index = regex.indexIn(self.toPlainText().upper(), pos)

        self.blockSignals(True)

        while (index != -1):
            # Select the matched text and apply the desired format
            den = regex.matchedLength()
            x = regex.capturedTexts()
            #print(index, den,x)
            if x[2] in ['ADD','SUB']:
                format.setForeground(QtGui.QColor(198, 40, 40))

            elif x[2] in ['AND','OR','NOT','XOR','SHR','SHL']:
                format.setForeground(QtGui.QColor(30, 136, 229))

            elif x[2] == 'CMP':
                format.setForeground(QtGui.QColor(178, 181, 5))

            elif x[2] in ['LOAD','STORE','LOADI']:
                format.setForeground(QtGui.QColor(143, 214, 225))
            elif x[2] in ['JZ','JNZ','JUMP']:
                format.setForeground(QtGui.QColor(230, 122, 59))




            cursor.setPosition(index, QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(index + den, QtGui.QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            # Move to the next match
            pos = index + den
            index = regex.indexIn(self.toPlainText().upper(), pos)

        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QBrush(QtGui.QColor("transparent")))

        self.nop_instruction()

        self.setCurrentCharFormat(format)
        self.blockSignals(False)

    def register_search(self):
        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QColor(156, 156, 156))
        format.setFontWeight(QtGui.QFont.Bold)

        cursor = self.textCursor()

        pattern = "R"+"|R".join(list(map(str,range(16))))
        regex = QtCore.QRegExp(pattern)

        # Process the displayed document
        pos = 0
        index = regex.indexIn(self.toPlainText().upper(), pos)

        self.blockSignals(True)

        while (index != -1):
            # Select the matched text and apply the desired format
            den = regex.matchedLength()
            x = regex.capturedTexts()
            #print(index, den,x)
            cursor.setPosition(index, QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(index + den, QtGui.QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            # Move to the next match
            pos = index + den
            index = regex.indexIn(self.toPlainText().upper(), pos)

        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QBrush(QtGui.QColor("transparent")))

        self.setCurrentCharFormat(format)
        self.blockSignals(False)

    def nop_instruction(self):
        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QColor(191, 0, 188))
        format.setFontWeight(QtGui.QFont.Bold)

        cursor = self.textCursor()
        pattern= "(^|\n) *\s*NOP( +|\s+)"

        regex = QtCore.QRegExp(pattern)

        # Process the displayed document
        pos = 0
        index = regex.indexIn(self.toPlainText().upper(), pos)

        self.blockSignals(True)

        while (index != -1):
            # Select the matched text and apply the desired format
            den = regex.matchedLength()
            x = regex.capturedTexts()
            #print(index, den,x)
            cursor.setPosition(index, QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(index + den, QtGui.QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            # Move to the next match
            pos = index + den
            index = regex.indexIn(self.toPlainText().upper(), pos)

        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QBrush(QtGui.QColor("transparent")))

        self.setCurrentCharFormat(format)
        self.blockSignals(False)


class OpenFileButton(QPushButton):

    def __init__(self):
        super().__init__("OPEN")
        self.setStyleSheet("background-color:#09424f;font-weight:bold;")


class SaveButton(QPushButton):

    def __init__(self):
        super().__init__("SAVE")


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.file = None
        self.file_name = None
        self.code_hash = None
        self.code = None

        self.run_period = 1 #100ms

        self.program_counter = 0
        self.register_values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        self.setWindowTitle("QTextEdit")
        self.resize(720, 480)
        self.setMinimumWidth(720)

        self.code_box = CodeWindow()
        self.open_button = OpenFileButton()

        self.save_button = QPushButton("SAVE")

        self.save_button.setDisabled(True)
        self.compile_button = QPushButton("COMPILE")
        self.save_button.setStyleSheet("font-weight:bold;")
        palette = QPalette()
        palette.setColor(QPalette.Button, QColor(156, 99, 0))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.Button, QColor(30, 30, 30))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(90, 90, 90))
        self.compile_button.setPalette(palette)
        self.compile_button.setStyleSheet("font-weight:bold;")
        #self.compile_button.setStyleSheet("background-color:#c76400;")
        self.compile_button.setDisabled(True)
        self.debugger_button = QPushButton("DEBUG")

        palette = QPalette()
        palette.setColor(QPalette.Button, QColor(0, 84, 0))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.Button, QColor(30, 30, 30))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(90, 90, 90))
        self.debugger_button.setPalette(palette)
        self.debugger_button.setStyleSheet("font-weight:bold;")
        self.debugger_button.setDisabled(True)

        leftLayout = QVBoxLayout()
        control_button = QHBoxLayout()
        control_button.addWidget(self.open_button)
        control_button.addWidget(self.save_button)
        control_button.addWidget(self.compile_button)
        control_button.addWidget(self.debugger_button)

        self.debug_buttons = DebugButtons()


        self.numbers = NumberBar(self.code_box)

        self.code_box.setMinimumHeight(300)

        layoutH = QHBoxLayout()
        layoutH.setSpacing(1)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.code_box)

        horizontal_line = QHLine()
        horizontal_line.setStyleSheet("background-color: #126e82;")


        leftLayout.addLayout(control_button)
        leftLayout.addWidget(horizontal_line)
        leftLayout.addLayout(self.debug_buttons)
        leftLayout.addLayout(layoutH)


        self.pc_text = QLabel()
        self.pc_text.setText("PC   : ")
        self.pc_text.setStyleSheet("font-weight: bold;")
        self.pc_text.setFixedWidth(40)
        self.pc_text.setAlignment(Qt.AlignCenter)
        self.pc_value = QLineEdit()
        self.pc_value.setText("0x0000")
        self.pc_value.setAlignment(QtCore.Qt.AlignCenter)
        self.pc_value.setReadOnly(True)
        self.pc_value.setFixedWidth(213)
        PC = QHBoxLayout()

        PC.addWidget(self.pc_text)
        PC.addWidget(self.pc_value)


        registers = QVBoxLayout()
        registers.addLayout(PC)


        self.register_list = []
        for i in range(8):
            register_label0 = QLabel()
            register_label0.setText("R{:<{}}:".format(i*2,4 if i<5 else 3))
            register_label0.setStyleSheet("font-weight: bold;")
            register_label0.setFixedWidth(40)
            register_label0.setAlignment(Qt.AlignCenter)
            register_value0 = QLineEdit()
            register_value0.setText("0x0000")
            register_value0.setAlignment(Qt.AlignCenter)
            register_value0.setReadOnly(True)
            register_value0.setFixedWidth(80)
            self.register_list.append(register_value0)

            register_label1 = QLabel()
            register_label1.setText("  R{:<{}}: ".format(i * 2 + 1,4 if i<5 else 3))
            register_label1.setStyleSheet("font-weight: bold;")
            register_label1.setFixedWidth(40)
            register_label1.setAlignment(Qt.AlignCenter)
            register_value1 = QLineEdit()
            register_value1.setText("0x0000")
            register_value1.setAlignment(QtCore.Qt.AlignCenter)
            register_value1.setFixedWidth(80)
            register_value1.setReadOnly(True)
            self.register_list.append(register_value1)


            L1 = QHBoxLayout()
            L1.addWidget(register_label0)
            L1.addWidget(register_value0)
            L1.addWidget(register_label1)
            L1.addWidget(register_value1)
            registers.addLayout(L1)

        vertical_line = QVLine()
        vertical_line.setStyleSheet("background-color: #126e82;")
        upside = QHBoxLayout()
        upside.addLayout(leftLayout)
        upside.addWidget(vertical_line)
        upside.addLayout(registers)

        self.command_line = QTextEdit()
        self.command_line.setStyleSheet("font-weight: bold;")
        self.command_line.setReadOnly(True)
        self.command_line.setText("")
        self.command_line.setMinimumHeight(100)
        self.command_line.setMaximumHeight(150)

        outer = QVBoxLayout()
        horizontal_line = QHLine()
        horizontal_line.setStyleSheet("background-color: #126e82;")
        outer.addLayout(upside)
        outer.addWidget(horizontal_line)
        outer.addWidget(self.command_line)
        self.setLayout(outer)

        self.code_box.textChanged.connect(self.text_changed)
        self.open_button.clicked.connect(self.open_button_clicked)
        self.save_button.clicked.connect(self.save_button_clicked)
        self.compile_button.clicked.connect(self.compile_button_clicked)
        self.debugger_button.clicked.connect(self.debugger_button_clicked)

        self.debug_buttons.back_button.clicked.connect(self.back_button_clicked)
        self.debug_buttons.stop_run_button.clicked.connect(self.stop_run_button_clicked)
        self.debug_buttons.forward_button.clicked.connect(self.forward_button_clicked)
        self.debug_buttons.reset_button.clicked.connect(self.reset_button_clicked)
        self.debug_buttons.quit_debug_mode_button.clicked.connect(self.quit_emulator)
        # Brackets ExtraSelection ...
        self.left_selected_bracket = QTextEdit.ExtraSelection()
        self.right_selected_bracket = QTextEdit.ExtraSelection()

        self.instructions = []
        self.instruction_index = 0
        self.operation_stack = OperationStack()

        self.running = False

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.run_code)

    def open_button_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "File Explorer", "",
                                                  "Assembly File (*.asm)", options=options)

        if file_name:
            self.file_name = file_name
            self.file = open(self.file_name,"r+")
            self.code = self.file.read()
            self.code_box.setPlainText(self.code)
            self.save_button.setDisabled(True)
            self.compile_button.setDisabled(False)
            self.debugger_button.setDisabled(False)
            hash_object = hashlib.md5(self.code.encode())
            self.code_hash = str(hash_object.hexdigest())
            self.file.close()

    def save_button_clicked(self):
        if self.file_name == None:
            options = QFileDialog.Options()


            options |= QFileDialog.DontUseNativeDialog
            file_name = QFileDialog.getSaveFileName(self, "Save File", "",
                                                       "Assembly File (*.asm)", options=options)

            if file_name[0]:
                file_name = file_name[0].split('.')

                if len(file_name) == 1:
                    self.file_name = file_name[0]+'.asm'
                elif len(file_name) == 2 and file_name[1].lower() == 'asm':
                    self.file_name = file_name[0] + '.asm'
                else:
                    self.command_line.append("Please use Assembly Extension(*.asm)")
                    return None

            else:
                self.command_line.append("Please enter a file name to save!")
                return None


        self.file = open(self.file_name, "w")
        current_code = self.code_box.toPlainText()
        self.file.seek(0)
        self.file.write(current_code)
        self.file.truncate()
        self.file.close()
        self.file = open(self.file_name,"r+")

        hash_object = hashlib.md5(current_code.encode())
        self.code_hash = str(hash_object.hexdigest())
        self.save_button.hide()
        self.save_button.setDisabled(True)
        self.save_button.show()
        self.file.close()
        return 0

    def compile_button_clicked(self):
        if self.save_button_clicked() == None:
            return None
        asm = Assembler(self.file_name)
        self.command_line.append("Compiling is starting...")
        self.command_line.hide()
        self.command_line.show()
        try:
            bin = asm.assembly()
            bin_filename = "out.bin"
            with open(bin_filename, 'w') as bin_file:
                bin_file.write(bin)

            self.command_line.append("Compiling is done successfully.")
            self.command_line.hide()
            self.command_line.show()

            self.command_line.append("Machine Language codes are saved into {}.".format(bin_filename))
            self.command_line.hide()
            self.command_line.show()

        except Exception as err:

            self.command_line.append(str(err)+"\n")

    def start_debug(self):
        if self.save_button_clicked() == None:
            return None
        asm = Assembler(self.file_name)
        self.command_line.append("Compiling is starting...")
        self.command_line.hide()
        self.command_line.show()
        try:
            bin = asm.assembly()

            self.command_line.append("Compiling is done successfully.")
            self.command_line.hide()
            self.command_line.show()
            return asm.instructions

        except Exception as err:

            self.command_line.append(str(err)+"\n")

    def set_cursor_to_line(self, line, run = False):

        cursor = self.code_box.textCursor()

        instruction_block = self.code_box.document().findBlockByNumber(line)

        cursor.setPosition(instruction_block.position())
        self.code_box.setTextCursor(cursor)

        block_min_offset = 0
        if block_min_offset == line:
            self.debug_buttons.back_button.setDisabled(True)
            self.debug_buttons.back_button.hide()
            self.debug_buttons.back_button.show()

        else:
            if not run:
                self.debug_buttons.back_button.setDisabled(False)

        block_max_offset = self.code_box.document().lineCount() - 1
        if block_max_offset == line:
            self.debug_buttons.forward_button.setDisabled(True)
            self.debug_buttons.forward_button.hide()
            self.debug_buttons.forward_button.show()

        else:
            if not run:
                self.debug_buttons.forward_button.setDisabled(False)
                self.debug_buttons.stop_run_button.setDisabled(False)

    def debugger_button_clicked(self):

        self.instructions = self.start_debug()
        if self.instructions == None:
            return None
        self.instruction_index = 0
        self.operation_stack.clear()

        for ins in self.instructions:
            print(ins.line, end=' | ')


        self.code_box.setReadOnly(True)
        self.debug_buttons.show()
        self.debug_buttons.quit_debug_mode_button.setDisabled(False)

        if self.instructions:

            self.code_box.setPlainText(self.code_box.toPlainText().rstrip() +"\n")
            self.set_cursor_to_line(self.instructions[0].line-1)


            self.debug_buttons.back_button.setDisabled(True)
            self.debug_buttons.stop_run_button.setDisabled(False)
            self.debug_buttons.forward_button.setDisabled(False)
            self.debug_buttons.reset_button.setDisabled(True)

    def back_button_clicked(self):

        OCB = self.operation_stack.pop()
        operation = OCB.operation
        print("OCB",OCB.registers)

        self.set_cursor_to_line(operation.line - 1)
        self.program_counter = OCB.PC
        self.register_values = OCB.registers
        self.instruction_index = OCB.operation_index

        if self.instruction_index == 0:
            self.debug_buttons.back_button.setDisabled(True)

        self.update_registers()

        if self.operation_stack.isEmpty():
            self.debug_buttons.reset_button.setDisabled(True)

    def run_code(self):
        if not self.forward_button_clicked(True):
            self.stop_run_button_clicked()
            self.debug_buttons.forward_button.setDisabled(True)
            self.debug_buttons.stop_run_button.setDisabled(True)
            self.debug_buttons.back_button.setDisabled(False)
            self.update()

    def stop_run_button_clicked(self):
        if not self.running:
            self.running = True
            self.debug_buttons.stop_run_button.change_image("./assets/pause")
            self.debug_buttons.back_button.setDisabled(True)
            self.debug_buttons.forward_button.setDisabled(True)
            self.timer.start(self.debug_buttons.time_slider.value())

        else:
            self.running = False
            self.timer.stop()
            self.debug_buttons.stop_run_button.change_image("./assets/run")

            self.forward_button_clicked()

    def forward_button_clicked(self,run = False):
        cursor = self.code_box.textCursor()
        current_block = cursor.block().blockNumber()

        if self.instruction_index < len(self.instructions)-1:

            OCB = OperationControlBlock(self.instructions[self.instruction_index],
                                        self.program_counter,self.register_values.copy(),
                                        self.instruction_index)

            self.operation_stack.push(OCB)
            self.execute()
            #print(self.operation_stack.print())

            self.set_cursor_to_line(self.instructions[self.instruction_index].line-1, run)

        elif self.instruction_index == len(self.instructions)-1:
            self.set_cursor_to_line(current_block + 1, run)
            OCB = OperationControlBlock(self.instructions[self.instruction_index],
                                        self.program_counter, self.register_values.copy(),
                                        self.instruction_index)

            self.operation_stack.push(OCB)
            self.execute()
            self.debug_buttons.forward_button.setDisabled(True)
            self.debug_buttons.stop_run_button.setDisabled(True)

            return False

        else:
            return False

        if not self.operation_stack.isEmpty():
            self.debug_buttons.reset_button.setDisabled(False)

        return True

    def execute(self):
        instruction = self.instructions[self.instruction_index]
        op_code = instruction.opcode

        if op_code == "ADD":
            Rd = int(instruction.operand1[1:])
            Rs1 = int(instruction.operand2[1:])
            Rs2 = int(instruction.operand3[1:])

            self.register_values[Rd] = self.register_values[Rs1] + self.register_values[Rs2]
            if self.register_values[Rd] > int("ffff",16):
                self.register_values[Rd] -= int("ffff",16) + 1

        elif op_code == "SUB":
            Rd = int(instruction.operand1[1:])
            Rs1 = int(instruction.operand2[1:])
            Rs2 = int(instruction.operand3[1:])

            self.register_values[Rd] = abs(self.register_values[Rs1] - self.register_values[Rs2])


        elif op_code == "AND":
            Rd = int(instruction.operand1[1:])
            Rs1 = int(instruction.operand2[1:])
            Rs2 = int(instruction.operand3[1:])

            self.register_values[Rd] = self.register_values[Rs1] & self.register_values[Rs2]

        elif op_code == "OR":
            Rd = int(instruction.operand1[1:])
            Rs1 = int(instruction.operand2[1:])
            Rs2 = int(instruction.operand3[1:])

            self.register_values[Rd] = self.register_values[Rs1] | self.register_values[Rs2]

        elif op_code == "NOT":
            Rd = int(instruction.operand1[1:])
            Rs2 = int(instruction.operand2[1:])

            self.register_values[Rd] = ~self.register_values[Rs2]

        elif op_code == "XOR":
            Rd = int(instruction.operand1[1:])
            Rs1 = int(instruction.operand2[1:])
            Rs2 = int(instruction.operand3[1:])

            self.register_values[Rd] = self.register_values[Rs1] ^ self.register_values[Rs2]

        elif op_code == "CMP":
            Rd = int(instruction.operand1[1:])
            Rs1 = int(instruction.operand2[1:])
            Rs2 = int(instruction.operand3[1:])

            EQUAL = '0'
            AZ = '0'
            BZ = '0'
            AGB = '0'
            ALB = '0'

            if self.register_values[Rs1] == self.register_values[Rs2]:
                EQUAL = '1'

            if self.register_values[Rs1] == 0:
                AZ = '1'

            if self.register_values[Rs2] == 0:
                BZ = '1'

            if self.register_values[Rs1] > self.register_values[Rs2]:
                AGB = '1'

            if self.register_values[Rs1] < self.register_values[Rs2]:
                ALB = '1'

            status_word = "0"*11 + ALB + AGB + BZ + AZ + EQUAL
            self.register_values[Rd] = int(status_word,2)

        elif op_code == "SHL":
            Rd = int(instruction.operand1[1:])
            Rs2 = int(instruction.operand2[1:])

            self.register_values[Rd] = int(("{:016b}".format(self.register_values[Rs2]))[1:]+"0",2)

        elif op_code == "SHR":
            Rd = int(instruction.operand1[1:])
            Rs2 = int(instruction.operand2[1:])

            self.register_values[Rd] = int("0"+("{:016b}".format(self.register_values[Rs2]))[:-1], 2)

        elif op_code == "LOAD":
            Rd = int(instruction.operand1[1:])
            Rs2 = int(instruction.operand2[1:])

            #self.register_values[Rd] =

        elif op_code == "STORE":
            pass
        elif op_code == "JUMP":
            jump_offset = instruction.machineCode[-8:]
            print(jump_offset)

            self.program_counter+=1

            if jump_offset[0] == '1':
                complement = int(str(11111111 - int(jump_offset)),2)+1
                offset_temp = -complement

            else:
                offset_temp = int(jump_offset,2)


            print("OFFSET",offset_temp)
            self.program_counter += offset_temp
            print("NEW PX",self.program_counter)
            self.instruction_index = self.program_counter

            if self.instruction_index != len(self.instructions)-1:
                pass

            self.program_counter-=1
            self.instruction_index -= 1
            #print()
            # Jump to instruction where after add PC+1 to jumpoffset

        elif op_code == "NOP":
            pass
        elif op_code == "JZ":
            pass
        elif op_code == "JNZ":
            pass
        elif op_code == "LOADI":
            Rd = int(instruction.operand1[1:])
            Rs1 = int(instruction.operand2)

            self.register_values[Rd] = Rs1

        self.program_counter += 1
        self.instruction_index += 1
        self.update_registers()

        print(self.register_values,self.program_counter)

    def update_registers(self):

        self.pc_value.setText("{:#06x}".format(self.program_counter))

        for reg,reg_value in zip(self.register_list,self.register_values):
            new_value = "{:#06x}".format(reg_value)
            if new_value != reg.text():
                reg.setText(new_value)
                reg.setStyleSheet("color:#00de3b")
            else:
                reg.setStyleSheet("color:white")

    def reset_button_clicked(self):

        self.operation_stack.clear()
        self.register_values = [0]*16
        self.program_counter = 0
        self.pc_value.setText("0x0000")
        self.instruction_index = 0

        if self.running:
            self.stop_run_button_clicked()
            self.stop_run_button.update()

        self.set_cursor_to_line(self.instructions[0].line - 1)

        for reg_value in self.register_list:
            reg_value.setText("0x0000")
            reg_value.setStyleSheet("color:white")

        self.debug_buttons.stop_run_button.setDisabled(False)
        self.debug_buttons.back_button.setDisabled(True)

    def text_changed(self):

        hash_object = hashlib.md5(self.code_box.toPlainText().encode())
        current_hash = str(hash_object.hexdigest())
        self.save_button.setDisabled(current_hash == self.code_hash)

        self.debugger_button.setDisabled(len(self.code_box.toPlainText()) == 0)
        self.compile_button.setDisabled(len(self.code_box.toPlainText()) == 0)

        self.code_box.colorize()

    def paintEvent(self, event):
        highlighted_line = QTextEdit.ExtraSelection()
        highlighted_line.format.setBackground(lineHighlightColor)
        highlighted_line.format.setProperty(QTextFormat
                                            .FullWidthSelection,
                                            QVariant(True))
        highlighted_line.cursor = self.code_box.textCursor()
        highlighted_line.cursor.clearSelection()
        self.code_box.setExtraSelections([highlighted_line,
                                        self.left_selected_bracket,
                                        self.right_selected_bracket])

    def quit_emulator(self):
        self.code_box.setReadOnly(False)
        self.debug_buttons.hide()

        if self.running:
            self.stop_run_button_clicked()
            self.stop_run_button.update()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor(30, 30, 30))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(90, 90, 90))
    app.setPalette(palette)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
