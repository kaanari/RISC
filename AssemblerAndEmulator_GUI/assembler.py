from pyparsing import *
# Islemciyi Implement edekren Jumplarrdaki sol biti sign extend(tum 1 kaydirilir) edip toplayin!
# ToDo: Same Label name can not be used multiple times.

import re
from exeptions import LabelError, SyntaxErrorAssembler


class Label:
    REGISTER_NAMES = ["R0","R1","R2","R3","R4","R5","R6","R7","R8","R9","R10","R11","R12","R13","R14","R15"]
    LABEL_NAMES = []

    def __init__(self,name,address,line):
        '''
        Class definition for assembly labels

        :param name: Name of Assembly Label
        :param address: Corresponding Memory Address of the Label
        '''

        if name in Label.LABEL_NAMES:
            raise LabelError(line, name, 2)

        if name in Label.REGISTER_NAMES or name in list(Instruction.OPCODE.keys()):
            raise LabelError(line, name, 1)


        self.name    = name
        self.address = address
        self.line = line

        Label.LABEL_NAMES.append(name)



    @staticmethod
    def calculate_address(label_address,current_address):
        '''
        Jump instructions works by adding offset address to PC (Program Counter).
        Offset address is a relative reference but we have absolute address which we want to jump.
        This function calculates offset address from given absolute label address and current_addres.

        :param label_address: Label address to jump into
        :param current_address: Address of jump (JUMP,JNZ,JZ) instruction
        :return: address: Calculated offset in 8-bit signed format.
        '''
        # Adding 1 due to PC+1 after fetching cycle
        current_address += 1

        # Calculating offset address
        offset = label_address - current_address

        # Find corresponding 8-bit signed equivalent of offset
        if offset > 127 or offset < -128:
            raise Exception("ERROR: Label is too far!")

        else:
            if offset >= 0:
                offset = "{:08b}".format(offset)
            else:
                complement = "{:08b}".format(abs(offset))
                complement = str(11111111 - int(complement))
                complement = int(complement,2)+1
                offset     = "{:08b}".format(complement)

        return offset


class Instruction:
    '''
    Class definition for RISC-V Instructions
    '''

    OPCODE = {
                "ADD" : "0000",
                "SUB" : "0001",
                "AND": "0010",
                "OR": "0011",
                "NOT": "0100",
                "XOR": "0101",
                "CMP": "0110",
                "SHL": "0111",
                "SHR": "1000",
                "LOAD": "1001",
                "STORE": "1010",
                "JUMP": "1011",
                "NOP": "1100",
                "JZ": "1101",
                "JNZ": "1110",
                "LOADI": "1111",
                }

    def __init__(self, opcodeType, **kwargs):
        self.type = opcodeType
        self.opcode = kwargs['opcode']
        self.operand1 = ""
        self.operand2 = ""
        self.operand3 = ""
        self.address = kwargs['address']
        self.line = kwargs['line']
        self.machineCode = ""

        if opcodeType != 0:

            self.operands = kwargs['operand']
            if opcodeType == 1:
                self.operand1 = self.operands
            else:
                self.operand1 = self.operands[0]

            if opcodeType != 1:
                self.operand2 = self.operands[1]

            if opcodeType == 3:
                self.operand3 = self.operands[2]

        self.calc_machine_code()

    def calc_machine_code(self):
        '''

        :return:  Calculated Binary Machine Code template for corresponding instruction object
        '''
        # Gathering binary code for 4 bit opcode
        opcode_bin = Instruction.OPCODE[self.opcode]

        if self.type == 0:
            # Fill NOP Instruction format
            '''
            NOP:
            +----------+----------------------------------------------------------------+
            |  OPCODE  |                               Unused                           |
            |  (4-bit) |                               (12-bit)                         |
            +----------+----------------------------------------------------------------+
            '''
            self.machineCode =  opcode_bin + 12*"0"

        elif self.type == 1:  # JUMP (ToDo: Label Address)
            '''
            JUMP:
            +----------+------------------------+---------------------------------------+
            |  OPCODE  |         Unused         |       8-bit offset (Immediate)        |
            |  (4-bit) |         (4-bit)        |                (8-bit)                |
            +----------+------------------------+---------------------------------------+
            '''
            self.machineCode = opcode_bin + 4*"0"

        elif self.type == 2:
            op1 = self.encode_register(self.operand1)

            if self.opcode in ["NOT","SHL","SHR","LOAD","STORE"]:
                op2 = self.encode_register(self.operand2)

            else:
                op2 = self.operand2

            if self.opcode in ["NOT","SHL","SHR"]:
                '''
                NOT, SHL, SHR:
                +----------+------------------------+-------------------+-------------------+
                |  OPCODE  |  Destination Register  |      Unused       | Source Register 2 |
                |  (4-bit) |         (4-bit)        |      (4-bit)      |      (4-bit)      |
                +----------+------------------------+-------------------+-------------------+
                '''
                self.machineCode = opcode_bin + op1 + 4*"0" + op2

            elif self.opcode == "LOAD":
                '''
                LOAD:
                +----------+------------------------+-------------------+-------------------+
                |  OPCODE  |  Destination Register  | Source Register 1 |      Unused       |
                |  (4-bit) |         (4-bit)        |      (4-bit)      |      (4-bit)      |
                +----------+------------------------+-------------------+-------------------+
                '''
                self.machineCode = opcode_bin + op1 + op2 + 4*"0"

            elif self.opcode == "STORE":
                '''
                STORE:
                +----------+------------------------+-------------------+-------------------+
                |  OPCODE  |         Unused         | Source Register 1 | Source Register 2 |
                |  (4-bit) |         (4-bit)        |      (4-bit)      |      (4-bit)      |
                +----------+------------------------+-------------------+-------------------+
                '''
                self.machineCode = opcode_bin + 4*"0" + op1 + op2

            elif self.opcode in ["JZ", "JNZ"]: # (ToDo: Label Address)
                '''
                JZ, JNZ:
                +----------+------------------------+---------------------------------------+
                |  OPCODE  | Register to be checked |       8-bit offset (Immediate)        |
                |  (4-bit) |         (4-bit)        |                (8-bit)                |
                +----------+------------------------+---------------------------------------+
                '''
                self.machineCode = opcode_bin + op1

            else:
                '''
                LOADI:
                +----------+------------------------+---------------------------------------+
                |  OPCODE  |  Destination Register  |        8-bit data (Immediate)         |
                |  (4-bit) |         (4-bit)        |                (8-bit)                |
                +----------+------------------------+---------------------------------------+
                '''
                self.machineCode = opcode_bin + op1 + "{:08b}".format(int(op2))
        else:
            '''
            ADD, SUB, AND, OR, XOR, CMP:
            +----------+------------------------+-------------------+-------------------+
            |  OPCODE  |  Destination Register  | Source Register 1 | Source Register 2 |
            |  (4-bit) |         (4-bit)        |      (4-bit)      |      (4-bit)      |
            +----------+------------------------+-------------------+-------------------+
            '''
            op1 = self.encode_register(self.operand1)
            op2 = self.encode_register(self.operand2)
            op3 = self.encode_register(self.operand3)

            self.machineCode = opcode_bin + op1+op2+op3


    def encode_register(self,register):
        '''
        :param register: Register Name (R0,R1,...,R15)
        :return: 4-bit Register Binary Code (0000,0001,....,1111)
        '''

        return "{:04b}".format(int(register[1:]))

    def __str__(self):
        '''
        :return:Formatted Instruction String to print nice looking representation of assembler result

        '''
        return "{:#06x}: {} | {} {} {} {}".format(self.address,self.machineCode,self.opcode,self.operand1,self.operand2,self.operand3)


class Assembler:

    instructionList = []
    ThreeOpInst = ["ADD", "SUB", "AND", "OR", "XOR", "CMP"]
    TwoOpInst = ["NOT", "SHL", "SHR", "LOAD", "STORE", "JZ", "JNZ", "LOADI"]
    OneOpInst = ["JUMP"]
    NoOpInst = ["NOP"]

    instructionList.extend(ThreeOpInst)
    instructionList.extend(TwoOpInst)
    instructionList.extend(OneOpInst)
    instructionList.extend(NoOpInst)

    register = Word(alphas + nums)

    Instruction3Operand = oneOf(" ".join(ThreeOpInst)) + register + "," + register + "," + register
    Instruction2Operand = oneOf(" ".join(TwoOpInst)) + register + "," + register
    Instruction1Operand = oneOf(" ".join(OneOpInst)) + register
    InstructionNoOperand = oneOf(" ".join(NoOpInst))
    LabelTemplate = Word(alphas) + (Word(nums) | Word(alphas)) + ':'


    label_reg = "[a-zA-Z]+\w*( |\s)*:"


    def __init__(self, file):
        # Read File
        code = open(file).read()

        # ====== PREPROCESSING ======
        # Convert all chars to uppercase for string operations.
        code = code.upper()
        self.code_lines = code.splitlines() # Split lines

        self.labels = []
        self.instructions = []

    def assembly(self,print = False):
        '''
        Convert Assemly Code to Machine Language
        '''
        Label.LABEL_NAMES = []
        self.lexer()
        self.label_correct()
        if print:
            self.output()
        return self.raw_output()

    def lexer(self):
        '''
        Lexer tokenizes the input assembly code.
        Distributes labels and instructions in corresponding class
        '''
        currentAddress = 0

        for lineCount, st in enumerate(self.code_lines):
            action = Group(
                Assembler.Instruction3Operand | Assembler.Instruction2Operand |
                Assembler.Instruction1Operand | Assembler.InstructionNoOperand)

            try:
                parsedInstruction = action.parseString(st)[0]

            except ParseException as pe:
                if st.isspace() or st == '':
                    # Empty Line
                    continue

                else:
                    # Syntax Error
                    res = re.search(Assembler.label_reg, st)
                    if res != None: #Label
                        label = Label(res.group()[:-1].strip(), currentAddress,lineCount+1)
                        self.labels.append(label)
                        continue
                    else:
                        raise SyntaxErrorAssembler(lineCount+1)

            if parsedInstruction[0] in Assembler.ThreeOpInst:
                operands = (parsedInstruction[1], parsedInstruction[3], parsedInstruction[5])
                instruction = Instruction(3, opcode=parsedInstruction[0], operand=operands, address=currentAddress, line = lineCount+1)
                self.instructions.append(instruction)

            elif parsedInstruction[0] in Assembler.TwoOpInst:
                operands = (parsedInstruction[1], parsedInstruction[3])
                instruction = Instruction(2, opcode=parsedInstruction[0], operand=operands, address=currentAddress, line = lineCount+1)
                self.instructions.append(instruction)

            elif parsedInstruction[0] in Assembler.OneOpInst:
                operands = (parsedInstruction[1])
                instruction = Instruction(1, opcode=parsedInstruction[0], operand=operands, address=currentAddress, line = lineCount+1)
                self.instructions.append(instruction)

            elif parsedInstruction[0] in Assembler.NoOpInst:
                instruction = Instruction(0, opcode=parsedInstruction[0], address=currentAddress, line = lineCount+1)
                self.instructions.append(instruction)


            currentAddress += 1

    def label_correct(self):
        '''
        label_correct function fills jump instructions after lexer.
        The reason why we can not in place completion of jump instruction is we can not know
        further label and its corresponding memory location address.
        '''
        if len(self.labels) != 0:
            label_names = {label.name: label.address for label in self.labels}

            for instruction in self.instructions:
                if instruction.opcode in ['JNZ', 'JZ']:
                    try:
                        jump_address = label_names[instruction.operand2]

                        instruction.machineCode += Label.calculate_address(jump_address, instruction.address)

                    except KeyError:
                        raise LabelError(instruction.line, instruction.operand2)


                elif instruction.opcode == "JUMP":
                    try:
                        jump_address = label_names[instruction.operand1]
                        instruction.machineCode += Label.calculate_address(jump_address, instruction.address)

                    except KeyError:
                        raise LabelError(instruction.line, instruction.operand2)

    def output(self):

        for instruction in self.instructions:
            print(instruction)

    def raw_output(self):
        '''
        :return: Raw Binary Output
        '''
        binary = ""
        for instruction in self.instructions:
            binary += instruction.machineCode

        return binary


if __name__ == "__main__":
    asm = Assembler("son.asm")

    try:
        bin = asm.assembly()

        with open("out.bin",'w') as bin_file:
            bin_file.write(bin)

    except Exception as err:
        print(err)