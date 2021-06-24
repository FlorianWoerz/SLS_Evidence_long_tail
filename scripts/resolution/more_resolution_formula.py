import clause as clause
import formula as formula
import cython_functions

from collections import defaultdict
from itertools import combinations, chain
from sys import stderr


def find_combinations(rights_candidate, subset_occ):
    return rights_candidate.intersection(subset_occ)

class MoreResolutionFormula(formula.Formula):

    def __init__(self, form = None):
        formula.Formula.__init__(self)
        self.max_length = None
        self.multiple_lit_occ_dict = {}
        self.already_resolved = set()
        # A set containing the clauses which were deregisted.
        self.deregistered_clauses = set()
        if form != None:
            self.n_variables = form.n_variables
            self.n_clauses = form.n_clauses
            self.clauses = form.clauses
            self.variable_dict = form.variable_dict
            self.current_max_length = form.current_max_length
            self.length_dict = form.length_dict
            self.clause_hash_values = form.clause_hash_values
            self.length_variable_dict = form.length_variable_dict






    def build_multiple_occ_dict(self, max_length):
        # The maximal intersection size is given by
        # i + j - max_length - 2, where i and j are the length of the corresponding clauses.
        # However, there are some additional requirements outlined in the following.
        self.max_length = max_length
        if max_length >= self.current_max_length:
            # This is what we consider the standard case. The resolvents may be longer than the original clauses.
            self.needed_intersect = max_length-2
        else:
            # Otherwise, we have the following additional requirement:
            # intersection_size <= min(i,j)-1. 
            # The intersection between two resolvable clauses is at most
            # the number of variables in the shorter clause - 1 (because of the resolving variable.)
            self.needed_intersect = 2*self.current_max_length-max_length-2
            if self.needed_intersect >= self.current_max_length:
                self.needed_intersect = -1
                # We test every possible combination of i and j to find the largest needed intersection size 
                # meeting the requirement described above.
                # There might be a smarter way to do this though.
                for i in range(1, self.current_max_length+1):
                    for j in range(i, self.current_max_length+1):
                        temp_intersect = i + j - 2 - max_length
                        # As said before, we have intersection_size <= min(i,j)-1.
                        # By definition of the variables i <= j, and i is an integer. 
                        # Therefore this inequality is equivalent to intersection_size < i.
                        if temp_intersect < i:
                            # This means, the constraint was met.
                            # We chosse the maximum of the current maximum and the calculated temp_intersect.
                            self.needed_intersect = max(self.needed_intersect, temp_intersect)

        for l in range(1, self.needed_intersect+1):
            self.multiple_lit_occ_dict[l] = defaultdict(set)
        for i in range(self.n_clauses):
            self.add_clause_to_multiple_occ_dict(i, self.needed_intersect)

            

    def add_clause_to_multiple_occ_dict(self, index, intersect):
        clause_vars = self.clauses[index].variables
        for l in range(1, intersect+1):
            for var_subset in combinations(clause_vars, l):
                self.multiple_lit_occ_dict[l][frozenset(var_subset)].add(index)

    def add_all_clauses(self, clauses):
        """
        This methods adds the clauses in the list `clauses` to the formula object.
        The method checks for every clause that it is not already present in the formula
        by calculating the hash value of the clause.
        """
        added_clauses = []
        for c in clauses:
            if not c.hash in self.clause_hash_values:
                self.add_clause(c)
                added_clauses.append(c)

        for i in self.clauses:
            if i in self.deregistered_clauses:
                continue
            c_vars = self.clauses[i].variables
            for var_combination in chain.from_iterable(
                    combinations(c_vars, r) for r in range(1, len(c_vars))):
                if cython_functions.hash_value(var_combination) in self.clause_hash_values:
                    #print("subsumed clause:", c_vars, "subsumed by:", list(var_combination))
                    self.deregister_clause(i)
                    break
                
        return added_clauses


    def add_clause(self, c):
        super().add_clause(c)
        if not (self.max_length is None):
            self.add_clause_to_multiple_occ_dict(self.n_clauses-1, self.needed_intersect)

    def deregister_clause(self, clause_index):
        # This method should be called if no further resolvents of this clause are wanted.
        # The clause is resolved if it is in the length_variable_dict.
        # Thus, removing it from this dict is sufficient.
        self.deregistered_clauses.add(clause_index)
        c = self.clauses[clause_index]
        length = len(c.variables)
        for v in c.variables:
            self.length_variable_dict[(length, v)].remove(clause_index)

        if not (self.max_length is None):
            for l in range(1, self.needed_intersect + 1):
                for var_subset in combinations(c.variables, l):
                    self.multiple_lit_occ_dict[l][frozenset(var_subset)].remove(clause_index)

    def resolve_all_add_to_formula(self, min_index=0, max_length=4):
        resolvents = self.resolve_all(min_index=min_index, max_length=max_length)
        return self.add_all_clauses(resolvents)

    def resolve_all(self, min_index=0, max_length=4, parents=False):
        if self.max_length is None:
            self.build_multiple_occ_dict(max_length)

        resolvents = []
        for i in range(1, self.current_max_length+1):
            clauses_left = self.length_dict[i]
            for j in range(1, self.current_max_length+1):
                min_intersect = i+j-2-self.max_length
                # If the min_intersect is greater than the maximal needed intersection,
                # then resolution cannot produce clauses meeting the max_length requirement.
                # The maximal needed intersection is calculated in build_multiple_occ_dict.
                if min_intersect > self.needed_intersect:
                    continue
                clauses_right = self.length_dict[j]
                for lit in range(-self.n_variables, self.n_variables+1):
                    lefts = self.length_variable_dict[(i, lit)]
                    if min_intersect <= 0:
                        rights = self.length_variable_dict[(j, -lit)]
                        resolvents.extend(self.resolve_two_sets(lefts, rights, lit, min_index=min_index, max_length=max_length, parents=parents))
                    else:
                        for left in filter(lambda x: x >= min_index, lefts):
                            for C in combinations(self.clauses[left].variables, min_intersect):
                                rights = self.length_variable_dict[(j, -lit)].intersection(self.multiple_lit_occ_dict[min_intersect][frozenset(C)])
                                resolvents.extend(self.resolve_clause_with_set(left, rights, lit, max_length, parents))

        return resolvents
                    

    def resolve_two_sets(self, lefts, rights, literal,min_index=0, max_length=4, parents=False):
        if len(lefts) == 0 or len(rights) == 0:
            return []
        resolvents = []
        for left in filter(lambda x: x >= min_index, lefts):
            for right in rights:
                if (left, right) in self.already_resolved or (right, left) in self.already_resolved:
                    continue
                self.already_resolved.add((left, right))
                resolvent = self.resolve_on_variable(left, right, literal, max_length, parents)
                if resolvent is not None:
                    resolvents.append(resolvent)
        return resolvents

    def resolve_clause_with_set(self, left, rights, literal, max_length=4, parents=False):
        resolvents = []
        for right in rights:
            if (left, right) in self.already_resolved or (right, left) in self.already_resolved:
                continue
            self.already_resolved.add((left, right))
            resolvent = self.resolve_on_variable(left, right, literal, max_length, parents)
            if resolvent is not None:
                resolvents.append(resolvent)
        return resolvents

   
            
    def resolve_multiple_times(self, times=2, max_length=4, parents=False):
        result_dict = {}
        old_n_clauses = self.n_clauses
        result = self.resolve_all(max_length=max_length, min_index=0, parents=parents)
        result = self.add_all_clauses(result)
        i = 1
        while i < times and len(result) > 0:
            unit_counter = 0
            binary_counter = 0
            ternary_counter = 0
            for c in result:
                if c.length == 3:
                    ternary_counter += 1
                elif c.length == 2:
                    binary_counter += 1
                elif c.length == 1:
                    unit_counter += 1
            print(
                f"level {i} complete, learnt {len(result)} clauses. Learned {unit_counter} unit, "
                f"{binary_counter} binary, and {ternary_counter} ternary clauses this level. "
                f"In total {self.n_clauses} clauses and {len(self.deregistered_clauses)} subsumed clauses.")
            result_dict[i] = result
            result = self.resolve_all(max_length=max_length, min_index=old_n_clauses, parents=parents)
            old_n_clauses = self.n_clauses
            result = self.add_all_clauses(result)
            i += 1


        result = self.add_all_clauses(result)
        result_dict[i] = result
        return result_dict

    def resolve_to_convergence(self, max_length=4, parents=False):
        return self.resolve_multiple_times(times=float('inf'), max_length=max_length, parents=parents)
