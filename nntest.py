
class Operation:

    def __init__(self, input_nodes=[]):
        self.input_nodes = input_nodes
        self.output_nodes = []
        for node in input_nodes:
            node.output_nodes.append(self)

    def compute(self):
        pass


class Add(Operation):
    def __init__(self, x, y):
        super().__init__([x, y])

    def compute(self, xvar, yvar):
        self.inputs = [xvar, yvar]
        return xvar + yvar


class Multiply(Operation):
    def __init__(self, x, y):
        super().__init__([x, y])

    def compute(self, xvar, yvar):
        self.inputs = [xvar, yvar]
        return xvar * yvar


class Matmul(Operation):
    def __init__(self, x, y):
        super().__init__([x, y])

    def compute(self, xvar, yvar):
        self.inputs = [xvar, yvar]
        return xvar.dot(yvar)




