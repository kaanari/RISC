from memory import *
import emulator
from assembler import Assembler
from gui_elements import QHLine, LineNumberBar


import hashlib

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


class OpenFileButton(QPushButton):

    def __init__(self,controller):
        super().__init__("OPEN")
        self.setStyleSheet("background-color:#09424f;font-weight:bold;")
        self.clicked.connect(self.on_click)
        self.controller = controller

    def on_click(self):

        emulator = self.controller.control_buttons.emulator_button.emulator

        if emulator != None:
            flag = emulator.isInitialized
        else:
            flag = False


        if flag:
            emulator.close()

        self.controller.command_line.setText("")

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
                    self.controller.command_line.insertPlainText("Please use Assembly Extension(*.asm)")
                    return None

            else:
                self.command_line.insertPlainText("Please enter a file name to save!")
                return None

        file = open(self.controller.file_name, "w")
        current_code = self.controller.code_box.toPlainText()
        file.seek(0)
        file.write(current_code)
        file.truncate()
        file.close()

        hash_object = hashlib.md5(current_code.encode())
        self.controller.code_box.code_hash = str(hash_object.hexdigest())
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
        self.controller.command_line.insertPlainText("Compiling is starting...")
        self.controller.command_line.hide()
        self.controller.command_line.show()

        try:
            bin = asm.assembly()
            bin_filename = "out.bin"
            with open(bin_filename, 'w') as bin_file:
                bin_file.write(bin)

            self.controller.command_line.insertPlainText("Compiling is done successfully.")
            self.controller.command_line.hide()
            self.controller.command_line.show()

            self.controller.command_line.insertPlainText("Machine Language codes are saved into {}.".format(bin_filename))
            self.controller.command_line.hide()
            self.controller.command_line.show()

        except Exception as err:
            self.controller.code_box.isErrorSet = True
            LineNumberBar.lineHighlightColor = LineNumberBar.error
            self.controller.code_box.set_cursor_to_line(err.line-1)
            self.controller.command_line.insertPlainText(str(err)+"\n")


class ButtonController:

    def __init__(self,app):

        self.code_box = app.code_box
        self.code_box.controller = self
        self.command_line = app.command_line
        self.file_name = None

        self.emulator_buttons = EmulatorButtons(self)
        self.control_buttons = ControlButtons(self)


class EmulateButton(QPushButton):

    def __init__(self, controller):
        super().__init__("EMULATE")

        self.controller = controller
        self.emulator   = emulator.Emulator(controller)


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

        self.controller.code_box.setReadOnly(True)
        if self.emulator.isInitialized:
            self.emulator.reset()

        if self.emulator.initialize() == None:
            self.controller.code_box.setReadOnly(False)
            return None

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
        _buttons = QHBoxLayout()

        self.controller = controller

        self.back_button = PicButton("./assets/left_arrow")
        self.stop_run_button = PicButton("./assets/run")
        self.forward_button = PicButton("./assets/right_arrow")
        self.reset_button = PicButton("./assets/reset")

        self.quit_debug_mode_button = PicButton("./assets/close")

        self.time_slider = emulator.StepSlider()

        _buttons.addWidget(self.back_button)
        _buttons.addWidget(self.stop_run_button)
        _buttons.addWidget(self.forward_button)
        _buttons.addWidget(self.reset_button)
        _buttons.addWidget(self.quit_debug_mode_button)
        _buttons.addWidget(self.time_slider.slider_text)
        _buttons.addWidget(self.time_slider)
        _buttons.addWidget(self.time_slider.slider_value)

        self.debug_line = QHLine()
        self.debug_line.setStyleSheet("background-color: #126e82;")
        self.debug_line.hide()

        self.addLayout(_buttons)
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
