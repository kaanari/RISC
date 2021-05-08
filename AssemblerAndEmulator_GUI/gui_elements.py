from buttons import *

import hashlib

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: #126e82;")


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: #126e82;")


class LineNumberBar(QWidget):
    lineBarColor = QColor("#39444a")
    lineHighlightColor = QColor("#39444a")
    normal = QColor("#39444a")
    error = QColor("#8a0000")

    def __init__(self, code_box,parent = None):
        super().__init__(parent)
        self.editor = code_box

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
            painter.fillRect(event.rect(), LineNumberBar.lineBarColor)
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
        self.isErrorSet = False

    def colorize(self):
        format = QTextCharFormat()

        format.setForeground(QColor(255, 255, 255))
        self.blockSignals(True)
        cursor = self.textCursor()
        cursor.setPosition(0, QTextCursor.MoveAnchor)

        cursor.setPosition(len(self.toPlainText()), QTextCursor.KeepAnchor)

        cursor.setCharFormat(format)
        self.blockSignals(False)
        self.label_search()
        self.instruction_search()
        self.register_search()

    def label_search(self):
        format = QTextCharFormat()

        format.setForeground(QColor(93, 166, 90))
        format.setFontWeight(QFont.Bold)
        cursor = self.textCursor()
        pattern = "[a-zA-Z]+\w*( |\s)*:"


        regex = QRegExp(pattern)

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
                self.labels.append(label_name)

            cursor.setPosition(index, QTextCursor.MoveAnchor)
            cursor.setPosition(index + den, QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            # Move to the next match
            pos = index + den
            index = regex.indexIn(self.toPlainText(), pos)

        if self.labels:
            # Process the displayed documen
            str_label_list = '|'.join(self.labels)

            pattern = "({})( |\s)+".format(str_label_list)
            pattern = "(( |\s)+|,)"+pattern
            regex = QRegExp(pattern)

            # Process the displayed document
            pos = 0
            index = regex.indexIn(self.toPlainText(), pos)

            while (index != -1):
                # Select the matched text and apply the desired format
                den = regex.matchedLength()
                cursor.setPosition(index, QTextCursor.MoveAnchor)
                cursor.setPosition(index + den, QTextCursor.KeepAnchor)
                cursor.setCharFormat(format)
                # Move to the next match
                pos = index + den
                index = regex.indexIn(self.toPlainText(), pos)

            pattern = ","
            regex = QRegExp(pattern)

            # Process the displayed document
            pos = 0
            index = regex.indexIn(self.toPlainText(), pos)

            while (index != -1):
                # Select the matched text and apply the desired format
                den = regex.matchedLength()
                cursor.setPosition(index, QTextCursor.MoveAnchor)
                cursor.setPosition(index + den, QTextCursor.KeepAnchor)
                cursor.setCharFormat(QTextCharFormat())
                # Move to the next match
                pos = index + den
                index = regex.indexIn(self.toPlainText(), pos)

        format = QTextCharFormat()
        format.setBackground(QBrush(QColor("transparent")))

        self.setCurrentCharFormat(format)




        self.blockSignals(False)

    def instruction_search(self):
        format = QTextCharFormat()

        format.setFontWeight(QFont.Bold)

        cursor = self.textCursor()
        pattern = "(^|\n) *\s*(ADD|SUB|AND|OR|NOT|XOR|CMP|SHL|SHR|LOAD|STORE|JUMP|JZ|JNZ|LOADI) +"
        regex = QRegExp(pattern)

        # Process the displayed document
        pos = 0
        index = regex.indexIn(self.toPlainText().upper(), pos)

        self.blockSignals(True)

        while (index != -1):
            # Select the matched text and apply the desired format
            den = regex.matchedLength()
            x = regex.capturedTexts()

            if x[2] in ['ADD','SUB']:
                format.setForeground(QColor(198, 40, 40))

            elif x[2] in ['AND','OR','NOT','XOR','SHR','SHL']:
                format.setForeground(QColor(30, 136, 229))

            elif x[2] == 'CMP':
                format.setForeground(QColor(178, 181, 5))

            elif x[2] in ['LOAD','STORE','LOADI']:
                format.setForeground(QColor(143, 214, 225))
            elif x[2] in ['JZ','JNZ','JUMP']:
                format.setForeground(QColor(230, 122, 59))




            cursor.setPosition(index, QTextCursor.MoveAnchor)
            cursor.setPosition(index + den, QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            # Move to the next match
            pos = index + den
            index = regex.indexIn(self.toPlainText().upper(), pos)

        format = QTextCharFormat()
        format.setBackground(QBrush(QColor("transparent")))

        self.nop_instruction()

        self.setCurrentCharFormat(format)
        self.blockSignals(False)

    def register_search(self):
        format = QTextCharFormat()
        format.setForeground(QColor(156, 156, 156))
        format.setFontWeight(QFont.Bold)

        cursor = self.textCursor()

        pattern = "R"+"|R".join(list(map(str,range(16))))
        regex = QRegExp(pattern)

        # Process the displayed document
        pos = 0
        index = regex.indexIn(self.toPlainText().upper(), pos)

        self.blockSignals(True)

        while (index != -1):
            # Select the matched text and apply the desired format
            den = regex.matchedLength()
            x = regex.capturedTexts()

            cursor.setPosition(index, QTextCursor.MoveAnchor)
            cursor.setPosition(index + den, QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            # Move to the next match
            pos = index + den
            index = regex.indexIn(self.toPlainText().upper(), pos)

        format = QTextCharFormat()
        format.setBackground(QBrush(QColor("transparent")))

        self.setCurrentCharFormat(format)
        self.blockSignals(False)

    def nop_instruction(self):
        format = QTextCharFormat()
        format.setForeground(QColor(191, 0, 188))
        format.setFontWeight(QFont.Bold)

        cursor = self.textCursor()
        pattern= "(^|\n) *\s*NOP( +|\s+)"

        regex = QRegExp(pattern)

        # Process the displayed document
        pos = 0
        index = regex.indexIn(self.toPlainText().upper(), pos)

        self.blockSignals(True)

        while (index != -1):
            # Select the matched text and apply the desired format
            den = regex.matchedLength()
            x = regex.capturedTexts()

            cursor.setPosition(index, QTextCursor.MoveAnchor)
            cursor.setPosition(index + den, QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)
            # Move to the next match
            pos = index + den
            index = regex.indexIn(self.toPlainText().upper(), pos)

        format = QTextCharFormat()
        format.setBackground(QBrush(QColor("transparent")))

        self.setCurrentCharFormat(format)
        self.blockSignals(False)

    def mousePressEvent(self, QMouseEvent):
        if self.isErrorSet:
            LineNumberBar.lineHighlightColor = LineNumberBar.normal
            self.isErrorSet = False

        if not self.isReadOnly():
            super().mousePressEvent(QMouseEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        if self.isErrorSet:
            LineNumberBar.lineHighlightColor = LineNumberBar.normal
            self.isErrorSet = False

        if not self.isReadOnly():
            super().mousePressEvent(QMouseEvent)

    def keyPressEvent(self, QKeyEvent):
        if self.isErrorSet:
            LineNumberBar.lineHighlightColor = LineNumberBar.normal
            self.isErrorSet = False

        if not self.isReadOnly():
            super().keyPressEvent(QKeyEvent)
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

    def set_cursor_last_line(self):

        cursor = self.textCursor()
        line = self.document().lineCount() - 1
        instruction_block = self.document().findBlockByNumber(line)

        cursor.setPosition(instruction_block.position())
        self.setTextCursor(cursor)

        self.controller.emulator_buttons.forward_button.setDisabled(True)
        self.controller.emulator_buttons.forward_button.hide()
        self.controller.emulator_buttons.forward_button.show()

    # Move it to CodeBox Class
    def text_changed(self):

        hash_object = hashlib.md5(self.toPlainText().encode())
        current_hash = str(hash_object.hexdigest())
        self.controller.control_buttons.save_button.setDisabled(current_hash == self.code_hash)

        self.controller.control_buttons.emulator_button.setDisabled(len(self.toPlainText()) == 0)
        self.controller.control_buttons.compile_button.setDisabled(len(self.toPlainText()) == 0)

        self.colorize()


class CommandLine(QTextEdit):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("font-weight: bold;")
        self.setReadOnly(True)
        self.setMinimumHeight(100)
        self.setMaximumHeight(150)
        self.lineCount = 1

    def insertPlainText(self, p_str):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

        empty_space = 2
        if self.lineCount>= 10:
            empty_space -= 1

        if self.lineCount >= 100:
            empty_space -= 1

        space = "&nbsp"*empty_space

        line_number = "<pre style='color:#29a0ba'>{:3d} >> </pre]>".format(self.lineCount)
        message     = "<span style='color:white'>{}</span><br>".format(p_str)
        self.insertHtml(line_number+message)
        self.lineCount += 1

        #super().__init__()

