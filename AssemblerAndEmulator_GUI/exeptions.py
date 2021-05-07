
class LabelError(Exception):

    def __init__(self,line,name,error_type = 0):


        if error_type == 0:
            self.message = "Label {} can't be found in line {}!".format(name,line)
        elif error_type == 1:
            self.message = "Invalid label name in line {} : Label name can not be a register or instruction name!".format(line)
        else:
            self.message = "Same name for multiple label can not be used! Resolve conflict in line {}.".format(line)

        self.line = line
        self.name = name
        super().__init__(self.message)


class SyntaxError(Exception):

    def __init__(self,line):
        self.message = "Syntax Error in Line {}!".format(line)
        self.line = line
        super().__init__(self.message)