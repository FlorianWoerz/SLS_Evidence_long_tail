import random
import cython_functions as c

class Clause:


    @classmethod
    def init_variable_mapping(cls, n_vars, seed=42):
        """
        This method initializes the variable mapping:
        Each literal of the clause `cls` is uniquely mapped to a randomly chosen value in {0, ..., 2^32 - 1}.
        Parameter cls: The clause.
        Parameter n_vars: The number of variables.
        Parameter seed: The seed to initialize the random number generator.
        """
        c.init_variable_mapping(n_vars, seed)

    @classmethod
    def calculate_hash_value(cls, variables):
        return c.hash_value(variables)


    def __init__(self):
        self.variables = set()
        self.length = 0
        self.parents = set()

    def hash_clause(self):
        """
        This method calculates the sum of literals of a clause w.r.t. the above variable mapping.
        Parameter clause: The clause is a list of the form [(Boolean, int)]. The Boolean describes the polarity of the literal. 
        """
        return c.hash_value(self.variables)

    def set_variables(self, variables):
        # self.variables = variables
        self.variables.update(variables)
        self.length = len(variables)
        self.hash = self.hash_clause()

    def set_parents(self, p1, p2):
        self.parents.add(p1)
        self.parents.add(p2)

    def get_parents(self):
        return self.parents

    def add_variable(self, x):
        if x in self.variables:
            print("Error: ", x, " is already in the variable list.")
        self.variables.append(x)
        self.length += 1
        self.hash = self.hash_clause()

    def remove_variable(self, x):
        if x not in self.variables:
            print("Error: ", x, " is not in the variable list.")
        self.variables.remove(x)
        self.length -= 1
        self.hash = self.hash_clause()

    def get_variables(self):
        return self.variables

    def get_length(self):
        return self.length

    def __str__(self):
        """
        This method can be used for printing a Clause object.
        """
        return ' '.join([str(x) for x in self.variables]) + ' 0\n'