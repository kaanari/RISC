import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from memory import *
from buttons import *
from gui_elements import *
from emulator import *

# Additional ToDo's:
# ToDo: Add Comments to Assembler
# Enhancement: White Color mode can also be added.

class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set window size and name
        self.setWindowTitle("RISC-V Emulator & Compiler")
        self.resize(950, 480)
        self.setMinimumWidth(950)

        # Definition of Core Components
        self.command_line = CommandLine()
        self.code_box = CodeWindow()
        self.numbers = LineNumberBar(self.code_box)
        self.button_controller = ButtonController(self)

        """
        LAYOUT FOR MAIN WINDOW:
        
        +--------------------+-------------+
        |    CONTROL BTNS    |             |
        |--------------------|             |
        |   EMULATOR BTNS    |             |
        |--------------------|             |
        | L |                |   EMULATOR  |
        | I |                |    WINDOW   |          
        | N |      CODE      |             |
        | E |      BOX       |             |
        |   |                |             |
        | # |                |             |
        |--------------------+-------------|
        |               COMMAND            |
        |                LINE              |
        +----------------------------------+
        
        left_layout (Vertical) = CONTROL BTNS + EMULATOR BTNS + code_editor__layout
        code_editor_layout (Horizontal) = LINE # + CODE BOX
        top_layout (Horizontal) = left_layout + EMULATOR WINDOW
        wrapper (Vertical)     = top_layout + COMMANDLINE 
        """

        self.setLayout(self.wrapper())

    def paintEvent(self, event):
        """
        Works in every GUI painting process.
        Draws highlighted line in the code editor.
        """
        left_selected_bracket = QTextEdit.ExtraSelection()
        right_selected_bracket = QTextEdit.ExtraSelection()

        highlighted_line = QTextEdit.ExtraSelection()
        highlighted_line.format.setBackground(LineNumberBar.lineHighlightColor)
        highlighted_line.format.setProperty(QTextFormat.FullWidthSelection,QVariant(True))
        highlighted_line.cursor = self.code_box.textCursor()
        highlighted_line.cursor.clearSelection()
        self.code_box.setExtraSelections([highlighted_line,left_selected_bracket,right_selected_bracket])

    def wrapper(self):
        """
        :return: Wrapper Layout for MainWindow
        """
        outer_layout = QHBoxLayout()

        horizontal_line = QHLine()

        layout = QVBoxLayout()
        layout.addLayout(self.top_layout())
        layout.addWidget(horizontal_line)
        layout.addWidget(self.command_line)

        outer_layout.addLayout(layout)
        outer_layout.addLayout(self.button_controller.control_buttons.emulator_button.emulator.memory_view.full_layout())

        return outer_layout

    def top_layout(self):
        """
        :return: Top Layout for MainWindow (EMULATOR_WINDOW + left_layout)
        """
        layout = QHBoxLayout()
        layout.addLayout(self.left_layout())
        layout.addLayout(self.button_controller.control_buttons.emulator_button.emulator.emulator_window)

        return layout

    def left_layout(self):
        """
        :return: Left layout for MainWindow (CONTROL BTNS + EMULATOR BTNS + code_editor_layout)
        """
        layout = QVBoxLayout()
        layout.addLayout(self.button_controller.control_buttons)
        layout.addLayout(self.button_controller.emulator_buttons)
        layout.addLayout(self.code_editor_layout())

        return layout

    def code_editor_layout(self):
        """
        :return: Code Editor Layout for MainWindow (Line Numbers + Code Box)
        """
        layout = QHBoxLayout()
        layout.setSpacing(1)
        layout.addWidget(self.numbers)
        layout.addWidget(self.code_box)

        return layout


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

