from gui_elements import *
from assembler import *
import buttons
import memory

class OperationControlBlock:

    def __init__(self, operation, PC, registers, operation_index, memory):
        self.operation = operation
        self.operation_index = operation_index
        self.PC = PC
        self.registers = registers
        self.memory = memory.copy()

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

class EmulatorWindow(QHBoxLayout):

    def __init__(self, emulator):
        super().__init__()

        self.emulator = emulator

        self.empty = QLabel("")
        # self.button_label.setAlignment(Qt.AlignRight)
        self.empty.setFixedWidth(100)

        self.button_label = QLabel("Open Memory Preview")
        self.button_label.setStyleSheet("font-size:12px;")
        #self.button_label.setAlignment(Qt.AlignRight)
        self.button_label.setFixedWidth(130)


        self.open_memview_button = buttons.PicButton("./assets/open_arrow",(18,36))
        self.open_memview_button.setDisabled(False)
        self.open_memview_button.clicked.connect(self.open_memview)
        self.memview_opened = False

        register_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.empty)
        top_layout.addWidget(self.button_label)
        top_layout.addWidget(self.open_memview_button)

        register_layout.addLayout(top_layout)
        self.horizontal_line = QHLine()
        register_layout.addWidget(self.horizontal_line)
        self.pc_text = QLabel()
        self.pc_text.setText("PC   : ")
        self.pc_text.setStyleSheet("font-weight: bold;")
        self.pc_text.setFixedWidth(40)
        self.pc_text.setAlignment(Qt.AlignCenter)
        self.pc_value = QLineEdit()
        self.pc_value.setText("0x0000")
        self.pc_value.setAlignment(Qt.AlignCenter)
        self.pc_value.setReadOnly(True)
        self.pc_value.setFixedWidth(213)
        PC = QHBoxLayout()

        PC.addWidget(self.pc_text)
        PC.addWidget(self.pc_value)

        register_layout.addLayout(PC)

        self.register_list = []
        for i in range(8):
            horizontal_layout = QHBoxLayout()
            self.register_list.append(self.register_template(i, horizontal_layout))

            self.register_list.append(self.register_template(i, horizontal_layout, True))

            register_layout.addLayout(horizontal_layout)

        self.register_labels = [label for label,_ in self.register_list]
        self.register_list = [reg_value for _, reg_value in self.register_list]
        self.register_format = 0
        # 0 -> HEX, 1 -> Unsigned Int, 2 -> Signed Int
        self.vertical_line = QVLine()

        self.addWidget(self.vertical_line)
        self.addLayout(register_layout)
        self.hide()

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

        return register_label,register_value
    # Move it to EmulatorWindow
    def update_registers(self, program_counter, register_values):

        if self.register_format == 0 or self.register_format == 1:
            for idx, reg_value in enumerate(register_values):
                if reg_value < 0:
                    # 2's Complement
                    register_values[idx] = 65535-abs(reg_value)+1



        if self.register_format == 0:
            string_format = "0x{:04X}"

        else:
            string_format = "{:5d}"


        self.pc_value.setText(string_format.format(program_counter))

        for reg,reg_value in zip(self.register_list,register_values):
            new_value = string_format.format(reg_value)
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

    def open_memview(self):
        print("asd")
        if not self.memview_opened:
            self.open_memview_button.change_image("./assets/close_arrow")
            self.emulator.memory_view.show()
        else:
            self.open_memview_button.change_image("./assets/open_arrow")
            self.emulator.memory_view.hide()

        self.open_memview_button.hide()
        self.open_memview_button.show()
        self.memview_opened = not self.memview_opened
        pass

    def hide(self):
        self.empty.hide()
        self.button_label.hide()
        self.open_memview_button.hide()
        self.horizontal_line.hide()
        self.pc_text.hide()
        self.pc_value.hide()
        self.vertical_line.hide()

        self.open_memview_button.change_image("./assets/open_arrow")
        self.memview_opened = False

        [label.hide() for label in self.register_labels]
        [value.hide() for value in self.register_list]

    def show(self):
        self.empty.show()
        self.button_label.show()
        self.open_memview_button.show()
        self.horizontal_line.show()
        self.pc_text.show()
        self.pc_value.show()
        self.vertical_line.show()

        [label.show() for label in self.register_labels]
        [value.show() for value in self.register_list]


class Emulator:

    def __init__(self,controller):

        self.controller = controller
        self.emulator_buttons = controller.emulator_buttons
        self.emulator_window = EmulatorWindow(self)

        self.program_counter = 0
        self.register_values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        self.run_period = 0  # 100ms

        self.instructions = []
        self.instruction_index = 0
        self.instructions_bin = None

        self.operation_stack = OperationStack()
        self.memory = memory.Memory()
        self.memory_view = memory.MemoryView(self.memory)

        self.running = False
        self.isInitialized = False

        self.timer = QTimer()
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
        self.controller.command_line.insertPlainText("Compiling is starting...")
        self.controller.command_line.hide()
        self.controller.command_line.show()

        try:
            bin = asm.assembly()
            instructions_bin = list(map(''.join, zip(*[iter(bin)]*16)))
            instructions_bin = [int(instruction_bin,2) for instruction_bin in instructions_bin]
            self.instructions_bin = instructions_bin
            # Write instructions to memory
            starting_address = 0
            self.memory.block_write(starting_address, instructions_bin)
            self.memory_view.update_values()
            self.memory_view.hide()
            self.emulator_window.show()

            self.controller.command_line.insertPlainText("Compiling is done successfully.")
            self.controller.command_line.hide()
            self.controller.command_line.show()

            if asm.instructions == None:
                return None

            self.instructions = asm.instructions
            self.instruction_index = 0
            self.operation_stack.clear()

            self.controller.code_box.setPlainText(self.controller.code_box.toPlainText().rstrip() + "\n")
            self.controller.code_box.set_cursor_to_line(self.instructions[0].line - 1)

            self.controller.control_buttons.save_button.on_click()

            self.emulator_buttons.back_button.setDisabled(True)
            self.emulator_buttons.stop_run_button.setDisabled(False)
            self.emulator_buttons.forward_button.setDisabled(False)
            self.emulator_buttons.reset_button.setDisabled(True)
            #self.controller.control_buttons.save_button.setDisabled(True)

            self.isInitialized = True

            return asm.instructions

        except Exception as err:

            self.controller.command_line.insertPlainText(str(err)+"\n")
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
            Rs1 = int(instruction.operand2[1:])

            self.register_values[Rd] = self.memory.read(self.register_values[Rs1])

        elif op_code == "STORE":
            Rs1 = int(instruction.operand1[1:])
            Rs2 = int(instruction.operand2[1:])

            self.memory.write(self.register_values[Rs1], self.register_values[Rs2])

        elif op_code == "JUMP":
            jump_offset = instruction.machineCode[-8:]
            self.jump(jump_offset)

        elif op_code == "NOP":
            pass
        elif op_code == "JZ":
            Rd = int(instruction.operand1[1:])

            if self.register_values[Rd] == 0:
                jump_offset = instruction.machineCode[-8:]

                self.jump(jump_offset)

        elif op_code == "JNZ":
            Rd = int(instruction.operand1[1:])

            if self.register_values[Rd] != 0:
                jump_offset = instruction.machineCode[-8:]

                self.jump(jump_offset)

        elif op_code == "LOADI":
            Rd = int(instruction.operand1[1:])
            Rs1 = int(instruction.operand2)

            self.register_values[Rd] = Rs1

        self.program_counter += 1
        self.instruction_index += 1
        self.emulator_window.update_registers(self.program_counter, self.register_values)

        print(self.register_values,self.program_counter)

    def jump(self,offset):
        self.program_counter += 1

        if offset[0] == '1':
            complement = int(str(11111111 - int(offset)), 2) + 1
            offset_temp = -complement

        else:
            offset_temp = int(offset, 2)

        self.program_counter += offset_temp
        self.instruction_index = self.program_counter

        if self.instruction_index != len(self.instructions) - 1:
            print("ERROR")
            pass

        self.program_counter -= 1
        self.instruction_index -= 1


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
                                        self.instruction_index,self.memory)

            self.operation_stack.push(OCB)
            self.execute()

            if self.instruction_index <= len(self.instructions)-1:
                self.controller.code_box.set_cursor_to_line(self.instructions[self.instruction_index].line-1, run)

            else:
                # Set to last block
                self.controller.code_box.set_cursor_last_line()

        elif self.instruction_index == len(self.instructions)-1:
            self.controller.code_box.set_cursor_to_line(current_block + 1, run)
            OCB = OperationControlBlock(self.instructions[self.instruction_index],
                                        self.program_counter, self.register_values.copy(),
                                        self.instruction_index, self.memory)

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
        self.memory.block_write(0, OCB.memory)

        if self.instruction_index == 0:
            self.emulator_buttons.back_button.setDisabled(True)

        self.emulator_window.update_registers(self.program_counter, self.register_values)
        self.memory_view.update_values()
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

        if not self.instructions_bin == None:
            # Write instructions to memory
            self.memory.reset()
            starting_address = 0
            self.memory.block_write(starting_address, self.instructions_bin)
            self.memory_view.update_values()

        self.emulator_buttons.stop_run_button.setDisabled(False)
        self.emulator_buttons.back_button.setDisabled(True)

    def close(self):

        self.reset()
        self.isInitialized = False
        self.controller.code_box.setReadOnly(False)
        self.emulator_buttons.hide()
        self.memory_view.hide()
        self.emulator_window.hide()


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
        if QMouseEvent.button() == Qt.LeftButton:
            val = self.pixel_pos_to_range(QMouseEvent.pos())
            self.setValue(val)

    def pixel_pos_to_range(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1;
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
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

