import formula

from collections import defaultdict
import numpy as np

class LocalSearchAssignment:

    def __init__(self, form):
        self.form = form
        self.assign = {}
        self.break_values = defaultdict(int)


    def assign_variable(self, variable, value):
        self.assign[np.abs(variable)] = value


    def flip_variable(self, variable):
        self.assign[np.abs(variable)] *= -1


    def set_variable_break(self, variable):
        if np.sign(variable) != np.sign(self.assign[variable]):
            print("nothing to change")
            return
        for index in self.form.variable_dict[variable]:
            clause = self.form.clause[index]
            for var in clause.variables:

