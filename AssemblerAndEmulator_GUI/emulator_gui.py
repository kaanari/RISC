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
    def __init__(self,parent = None):
        super(CodeWindow, self).__init__(parent)
        self.labels = []
        self.code_hash = None
        self.setMinimumHeight(300)

        self.controller = None
        self.textChanged.connect(self.text_changed)

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

    # Move it to CodeBox Class
    def set_cursor_to_line(self, line, run = False):

        cursor = self.textCursor()

        instruction_block = self.document().findBlockByNumber(line)

        cursor.setPosition(instruction_block.position())
        self.setTextCursor(cursor)

        block_min_offset = 0
        if block_min_offset == line:
            self.controller.emulator_buttons.back_button.setDisabled(True)
            self.controller.emulator_buttons.back_button.hide()
            self.controller.emulator_buttons.back_button.show()

        else:
            if not run:
                self.controller.emulator_buttons.back_button.setDisabled(False)

        block_max_offset = self.document().lineCount() - 1
        if block_max_offset == line:
            self.controller.emulator_buttons.forward_button.setDisabled(True)
            self.controller.emulator_buttons.forward_button.hide()
            self.controller.emulator_buttons.forward_button.show()

        else:
            if not run:
                self.controller.emulator_buttons.forward_button.setDisabled(False)
                self.controller.emulator_buttons.stop_run_button.setDisabled(False)

    # Move it to CodeBox Class
    def text_changed(self):

        hash_object = hashlib.md5(self.toPlainText().encode())
        current_hash = str(hash_object.hexdigest())
        self.controller.control_buttons.save_button.setDisabled(current_hash == self.code_hash)

        self.controller.control_buttons.emulator_button.setDisabled(len(self.toPlainText()) == 0)
        self.controller.control_buttons.compile_button.setDisabled(len(self.toPlainText()) == 0)

        self.colorize()


class OpenFileButton(QPushButton):

    def __init__(self,controller):
        super().__init__("OPEN")
        self.setStyleSheet("background-color:#09424f;font-weight:bold;")
        self.clicked.connect(self.on_click)
        self.controller = controller

    def on_click(self):
        self.setStyleSheet("background-color:#353535;")

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "File Explorer", "",
                                                  "Assembly File (*.asm)", options=options)

        self.setStyleSheet("background-color:#09424f;font-weight:bold;")
        if file_name:
            self.controller.file_name = file_name
            file = open(file_name,"r+")
            code = file.read()
            self.controller.code_box.setPlainText(code)
            self.controller.control_buttons.save_button.setDisabled(True)
            self.controller.control_buttons.compile_button.setDisabled(False)
            self.controller.control_buttons.emulator_button.setDisabled(False)
            hash_object = hashlib.md5(code.encode())
            self.controller.code_box.code_hash = str(hash_object.hexdigest())
            file.close()


class SaveButton(QPushButton):

    def __init__(self,controller):
        super().__init__("SAVE")

        self.controller = controller

        self.setDisabled(True)
        self.setStyleSheet("font-weight:bold;")
        self.clicked.connect(self.on_click)

    def on_click(self):

        if self.controller.file_name == None:
            options = QFileDialog.Options()

            options |= QFileDialog.DontUseNativeDialog
            file_name = QFileDialog.getSaveFileName(self, "Save File", "",
                                                    "Assembly File (*.asm)", options=options)

            if file_name[0]:
                file_name = file_name[0].split('.')

                if len(file_name) == 1:
                    self.controller.file_name = file_name[0] + '.asm'
                elif len(file_name) == 2 and file_name[1].lower() == 'asm':
                    self.controller.file_name = file_name[0] + '.asm'
                else:
                    self.controller.command_line.append("Please use Assembly Extension(*.asm)")
                    return None

            else:
                self.command_line.append("Please enter a file name to save!")
                return None

        file = open(self.controller.file_name, "w")
        current_code = self.controller.code_box.toPlainText()
        file.seek(0)
        file.write(current_code)
        file.truncate()
        file.close()

        hash_object = hashlib.md5(current_code.encode())
        self.controller.code_hash = str(hash_object.hexdigest())
        self.hide()
        self.setDisabled(True)
        self.show()
        return 0


class CompileButton(QPushButton):

    def __init__(self,controller):
        super().__init__("COMPILE")

        self.controller = controller

        palette = QPalette()
        palette.setColor(QPalette.Button, QColor(156, 99, 0))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.Button, QColor(30, 30, 30))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(90, 90, 90))

        self.setPalette(palette)
        self.setStyleSheet("font-weight:bold;")
        self.setDisabled(True)

        self.clicked.connect(self.on_click)

    def on_click(self):

        if self.controller.control_buttons.save_button.on_click() == None:
            return None

        asm = Assembler(self.controller.file_name)
        self.controller.command_line.append("Compiling is starting...")
        self.controller.command_line.hide()
        self.controller.command_line.show()

        try:
            bin = asm.assembly()
            bin_filename = "out.bin"
            with open(bin_filename, 'w') as bin_file:
                bin_file.write(bin)

            self.controller.command_line.append("Compiling is done successfully.")
            self.controller.command_line.hide()
            self.controller.command_line.show()

            self.controller.command_line.append("Machine Language codes are saved into {}.".format(bin_filename))
            self.controller.command_line.hide()
            self.controller.command_line.show()

        except Exception as err:

            self.controller.command_line.append(str(err)+"\n")


class ButtonController:

    def __init__(self,app):

        self.code_box = app.code_box
        self.command_line = app.command_line
        self.file_name = None

        self.emulator_buttons = EmulatorButtons(self)
        self.control_buttons = ControlButtons(self)


class EmulateButton(QPushButton):

    def __init__(self, controller):
        super().__init__("EMULATE")

        self.controller = controller
        self.emulator   = Emulator(controller)


        palette = QPalette()
        palette.setColor(QPalette.Button, QColor(0, 84, 0))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.Button, QColor(30, 30, 30))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(90, 90, 90))
        self.setPalette(palette)
        self.setStyleSheet("font-weight:bold;")
        self.setDisabled(True)
        self.clicked.connect(self.on_click)


    def on_click(self):

        if self.emulator.isInitialized:
            self.emulator.reset()

        if self.emulator.initialize() == None:
            return None

        self.controller.code_box.setReadOnly(True)
        self.controller.emulator_buttons.show()
        self.controller.emulator_buttons.quit_debug_mode_button.setDisabled(False)


class ControlButtons(QVBoxLayout):

    def __init__(self,controller):
        super().__init__()

        self.open_button = OpenFileButton(controller)
        self.save_button = SaveButton(controller)
        self.compile_button = CompileButton(controller)
        self.emulator_button = EmulateButton(controller)

        buttons = QHBoxLayout()
        buttons.addWidget(self.open_button)
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.compile_button)
        buttons.addWidget(self.emulator_button)

        horizontal_line = QHLine()
        horizontal_line.setStyleSheet("background-color: #126e82;")

        self.addLayout(buttons)
        self.addWidget(horizontal_line)


class EmulatorButtons(QVBoxLayout):

    def __init__(self,controller):
        super().__init__()
        buttons = QHBoxLayout()

        self.controller = controller

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


class EmulatorWindow(QVBoxLayout):

    def __init__(self):
        super().__init__()
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

        self.addLayout(PC)

        self.register_list = []
        for i in range(8):
            horizontal_layout = QHBoxLayout()
            self.register_list.append(self.register_template(i, horizontal_layout))

            self.register_list.append(self.register_template(i, horizontal_layout, True))

            self.addLayout(horizontal_layout)

    def register_template(self, i, layout,second_column = False):
        register_label = QLabel()
        if not second_column:
            register_label.setText("R{:<{}}:".format(i * 2, 4 if i < 5 else 3))
        else:
            register_label.setText("  R{:<{}}: ".format(i * 2 + 1, 4 if i < 5 else 3))

        register_label.setStyleSheet("font-weight: bold;")
        register_label.setFixedWidth(40)
        register_label.setAlignment(Qt.AlignCenter)
        register_value = QLineEdit()
        register_value.setText("0x0000")
        register_value.setAlignment(Qt.AlignCenter)
        register_value.setReadOnly(True)
        register_value.setFixedWidth(80)

        layout.addWidget(register_label)
        layout.addWidget(register_value)

        return register_value
    # Move it to EmulatorWindow
    def update_registers(self, program_counter, register_values):

        self.pc_value.setText("{:#06x}".format(program_counter))

        for reg,reg_value in zip(self.register_list,register_values):
            new_value = "{:#06x}".format(reg_value)
            if new_value != reg.text():
                reg.setText(new_value)
                reg.setStyleSheet("color:#00de3b")
            else:
                reg.setStyleSheet("color:white")

    def clear_registers(self):
        self.pc_value.setText("0x0000")

        for reg in self.register_list:
            reg.setText("0x0000")
            reg.setStyleSheet("color:white")


class Emulator:

    def __init__(self,controller):

        self.controller = controller

        self.emulator_buttons = controller.emulator_buttons

        self.emulator_window = EmulatorWindow()

        self.program_counter = 0
        self.register_values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        self.run_period = 0  # 100ms

        self.instructions = []
        self.instruction_index = 0
        self.operation_stack = OperationStack()

        self.running = False
        self.isInitialized = False

        #self.timer = QtCore.QTimer()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_code)

        self.emulator_buttons.back_button.clicked.connect(self.step_back)
        self.emulator_buttons.stop_run_button.clicked.connect(self.stop_run_button_clicked)
        self.emulator_buttons.forward_button.clicked.connect(self.step_into)
        self.emulator_buttons.reset_button.clicked.connect(self.reset)
        self.emulator_buttons.quit_debug_mode_button.clicked.connect(self.close)

    def initialize(self):
        if self.controller.control_buttons.save_button.on_click() == None:
            return None
        asm = Assembler(self.controller.file_name)
        self.controller.command_line.append("Compiling is starting...")
        self.controller.command_line.hide()
        self.controller.command_line.show()

        try:
            bin = asm.assembly()

            self.controller.command_line.append("Compiling is done successfully.")
            self.controller.command_line.hide()
            self.controller.command_line.show()

            if asm.instructions == None:
                return None

            self.instructions = asm.instructions
            self.instruction_index = 0
            self.operation_stack.clear()

            self.controller.code_box.setPlainText(self.controller.code_box.toPlainText().rstrip() + "\n")
            self.controller.code_box.set_cursor_to_line(self.instructions[0].line - 1)

            self.emulator_buttons.back_button.setDisabled(True)
            self.emulator_buttons.stop_run_button.setDisabled(False)
            self.emulator_buttons.forward_button.setDisabled(False)
            self.emulator_buttons.reset_button.setDisabled(True)

            self.isInitialized = True

            return asm.instructions

        except Exception as err:

            self.controller.command_line.append(str(err)+"\n")
            return None

    # Move it to Emulator
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
        self.emulator_window.update_registers(self.program_counter, self.register_values)

        print(self.register_values,self.program_counter)

    # Move it to emulator
    def run_code(self):
        if not self.step_into(True):
            self.stop_run_button_clicked()
            self.emulator_buttons.forward_button.setDisabled(True)
            self.emulator_buttons.stop_run_button.setDisabled(True)
            self.emulator_buttons.back_button.setDisabled(False)
            #self.update()

    def step_into(self,run = False):
        cursor = self.controller.code_box.textCursor()
        current_block = cursor.block().blockNumber()

        if self.instruction_index < len(self.instructions)-1:

            OCB = OperationControlBlock(self.instructions[self.instruction_index],
                                        self.program_counter,self.register_values.copy(),
                                        self.instruction_index)

            self.operation_stack.push(OCB)
            self.execute()
            #print(self.operation_stack.print())

            self.controller.code_box.set_cursor_to_line(self.instructions[self.instruction_index].line-1, run)

        elif self.instruction_index == len(self.instructions)-1:
            self.controller.code_box.set_cursor_to_line(current_block + 1, run)
            OCB = OperationControlBlock(self.instructions[self.instruction_index],
                                        self.program_counter, self.register_values.copy(),
                                        self.instruction_index)

            self.operation_stack.push(OCB)
            self.execute()
            self.emulator_buttons.forward_button.setDisabled(True)
            self.emulator_buttons.stop_run_button.setDisabled(True)

            return False

        else:
            return False

        if not self.operation_stack.isEmpty():
            self.emulator_buttons.reset_button.setDisabled(False)

        return True

    def step_back(self):

        OCB = self.operation_stack.pop()
        operation = OCB.operation
        print("OCB",OCB.registers)

        self.controller.code_box.set_cursor_to_line(operation.line - 1)
        self.program_counter = OCB.PC
        self.register_values = OCB.registers
        self.instruction_index = OCB.operation_index

        if self.instruction_index == 0:
            self.emulator_buttons.back_button.setDisabled(True)

        self.emulator_window.update_registers(self.program_counter, self.register_values)

        if self.operation_stack.isEmpty():
            self.emulator_buttons.reset_button.setDisabled(True)

    def stop_run_button_clicked(self):
        if not self.running:
            self.running = True
            self.emulator_buttons.stop_run_button.change_image("./assets/pause")
            self.emulator_buttons.back_button.setDisabled(True)
            self.emulator_buttons.forward_button.setDisabled(True)
            self.timer.start(self.emulator_buttons.time_slider.value())

        else:
            self.running = False
            self.timer.stop()
            self.emulator_buttons.stop_run_button.change_image("./assets/run")

            self.step_into()

    def reset(self):

        if self.running:
            self.stop_run_button_clicked()
            self.emulator_buttons.stop_run_button.update()

        self.operation_stack.clear()
        self.register_values = [0]*16
        self.program_counter = 0
        self.emulator_window.pc_value.setText("0x0000")
        self.instruction_index = 0
        self.emulator_window.clear_registers()

        self.controller.code_box.set_cursor_to_line(self.instructions[0].line - 1)

        self.emulator_buttons.stop_run_button.setDisabled(False)
        self.emulator_buttons.back_button.setDisabled(True)

    def close(self):

        self.reset()
        self.controller.code_box.setReadOnly(False)
        self.emulator_buttons.hide()


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("QTextEdit")
        self.resize(720, 480)
        self.setMinimumWidth(720)

        self.command_line = QTextEdit()
        self.code_box = CodeWindow()
        self.numbers = NumberBar(self.code_box)


        self.button_controller = ButtonController(self)
        self.code_box.controller = self.button_controller

        leftLayout = QVBoxLayout()

        code_editor_layout = QHBoxLayout()
        code_editor_layout.setSpacing(1)
        code_editor_layout.addWidget(self.numbers)
        code_editor_layout.addWidget(self.code_box)


        leftLayout.addLayout(self.button_controller.control_buttons)
        leftLayout.addLayout(self.button_controller.emulator_buttons)
        leftLayout.addLayout(code_editor_layout)





        vertical_line = QVLine()
        vertical_line.setStyleSheet("background-color: #126e82;")
        upside = QHBoxLayout()
        upside.addLayout(leftLayout)
        upside.addWidget(vertical_line)
        upside.addLayout(self.button_controller.control_buttons.emulator_button.emulator.emulator_window)


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


        #self.button_controller.control_button.open_button.clicked.connect(self.open_button_clicked)
        #self.button_controller.control_button.save_button.clicked.connect(self.save_button_clicked)
        #self.button_controller.control_button.compile_button.clicked.connect(self.compile_button_clicked)
        #self.button_controller.control_button.debugger_button.clicked.connect(self.debugger_button_clicked)

        #self.button_controller.debug_buttons.back_button.clicked.connect(self.back_button_clicked)
        #self.button_controller.debug_buttons.stop_run_button.clicked.connect(self.stop_run_button_clicked)
        #self.button_controller.debug_buttons.forward_button.clicked.connect(self.forward_button_clicked)
        #self.button_controller.debug_buttons.reset_button.clicked.connect(self.reset_button_clicked)
        #self.button_controller.debug_buttons.quit_debug_mode_button.clicked.connect(self.quit_emulator)




    def paintEvent(self, event):

        left_selected_bracket = QTextEdit.ExtraSelection()
        right_selected_bracket = QTextEdit.ExtraSelection()

        highlighted_line = QTextEdit.ExtraSelection()
        highlighted_line.format.setBackground(lineHighlightColor)
        highlighted_line.format.setProperty(QTextFormat.FullWidthSelection,QVariant(True))
        highlighted_line.cursor = self.code_box.textCursor()
        highlighted_line.cursor.clearSelection()
        self.code_box.setExtraSelections([highlighted_line,left_selected_bracket,right_selected_bracket])






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

