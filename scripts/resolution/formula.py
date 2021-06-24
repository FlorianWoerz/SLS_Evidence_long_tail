import clause as clause
import cython_functions as c

from collections import defaultdict
from sortedcontainers import SortedList
from itertools import chain, combinations

# Some terminology used in the comments:
#
# Definition (Tautology):
#    A clause C is a tautology if it contains two complementary literals l and -l.
# Example:
#    The clause (a ∨ b ∨ \neg b) is a tautology.
#
# Definition (Subsumption):
#    A clause C subsumes a clause D if and only if C \subseteq D.
#    We also say that D is subsumed by C.
# Example:
#    The clause (a ∨ b) subsumes the clause (a ∨ b ∨ \neg c).


class Formula:

    def __init__(self):
        self.n_variables = 0 # number of variables in the formula
        self.n_clauses = 0 # number of clauses in the formula
        self.clauses = {} # set of the clauses in the formula
        self.current_max_length = 0 # maximal length of a clause in the formula
        self.variable_dict = defaultdict(set) # dictionary keys: variables; values: indices of clauses in the `clauses` set where the variable appears
        self.length_dict = defaultdict(set) # dictionary keys: length; values: indices of clauses in the `clauses` set that have the specified length
        self.length_variable_dict = defaultdict(set) # dictionary keys: (clause_length, variable); values: indices of clauses in the `clauses` set that have the specified length and contain the specified variable
        self.clause_hash_values = set() # Set of the hash values of the clauses in the formula


    def set_n_vars(self, n):
        self.n_variables = n
        clause.Clause.init_variable_mapping(n)


    def add_clause(self, c):
        """This methods adds the clause object `c` to the formula and updates all necessary parameters."""

        if not isinstance(c, clause.Clause):
            print("Error:", c, "is not a Clause.")
            quit()

        # Insert the clause `c` in the "free" spot of the clauses set.
        # Currently there are self.n_clauses in this set, i.e. the "free" position is at index self.n_clauses
        self.clauses[self.n_clauses] = c 

        # Update the variable_dict and length_variable_dict
        for v in c.get_variables():
            self.variable_dict[v].add(self.n_clauses)
            self.length_variable_dict[(c.length, v)].add(self.n_clauses)

        # Update the length_dict
        self.length_dict[c.length].add(self.n_clauses)

        # Update the number of clauses in the formula object
        self.n_clauses += 1

        # Add the hash value of the clause to the set of hash values of the clauses in the formula
        self.clause_hash_values.add(c.hash)

        # Potentially update the current_max_length of the formula
        if c.length > self.current_max_length:
            self.current_max_length = c.length


    def remove_clause(self, index):
        """This methods removes the clause object at index `index` in the clause set from the formula and updates all necessary parameters."""

        # Obtain the clause from the clause set and remove it from the set
        c = self.clauses[index]
        self.clauses[index] = None

        if c == None:
            print("Error:", c, "is not in the clause list.")
            quit()

        # Update the variable_dict
        for v in c.get_variables():
            occurrences = self.variable_dict[v] # Obtain the occurences of variable `v`
            occurrences.remove(index) # Remove `index` from this set
            self.variable_dict[v] = occurrences # Update the respective set in the variable_dict

        # Update the clause_hash_values set
        self.clause_hash_values.remove(c.hash)
	

    def resolve_on_variable(self, index_clauseA, index_clauseB, variable, max_length=30000, parents=False):
        """
        This methods resolves the two clauses at indices `index_clauseA` and `index_clauseB` in the clauses set w.r.t. `variable`.
        The resolvent is only allowed to have `max_length` literals and to be non-tautological:

        Returns None if the resolvent is a tautology.
        Also returns None if the length of the resolvent is longer than max_length.
        """
        new_clause_vars = c.resolve(self.clauses[index_clauseA].variables, self.clauses[index_clauseB].variables,
                                    variable, max_length, self.clause_hash_values)
        if new_clause_vars is None:
            return None
            
        new_clause = clause.Clause()
        new_clause.set_variables(new_clause_vars)

        if parents:
            new_clause.set_parents(self.clauses[index_clauseA], self.clauses[index_clauseB])
        
        return new_clause
   
        
    def find_partner_clauses_on_variable(self, index_clause, variable, force_increasing_index=False, min_index=0):
        """
        This methods finds the indices of clauses in the clause set that can be resolved with the clause at index `index_clause`
        w.r.t. to `variable`.

        If force_increasing_index=True, only partner clauses with an index higher than `index_clause` and `min_index` are considered
        (this can dramatically save runtime!).
        """
        partner_clause_indices = self.variable_dict[-variable] # Find the indices of clauses containing -`variable

        if force_increasing_index:
            min_index = max(index_clause, min_index)

        if min_index > 0:
            partner_clause_indices = [index for index in partner_clause_indices if index >= min_index]
            #partner_clause_indices = partner_clause_indices[partner_clause_indices.bisect_left(min_index):]
        
        return partner_clause_indices
      

    def resolve_all_with_clause_on_variable(self, index_clause, variable, force_increasing_index=False, min_index=0, max_length=30000, parents=False):
        """
        This method returns a list of all clauses with at most `max_length` many literals
        that can be obtained by resolution of the clause at `index_clause` in the clause set w.r.t. `variable`.
        If force_increasing_index is set to True, then all clauses with a clause index less than index_clause are ignored.
        """        
        new_clauses = []
        partner_clause_indices = self.find_partner_clauses_on_variable(index_clause, variable, force_increasing_index, min_index=min_index)
        for index in partner_clause_indices:
            clause = self.resolve_on_variable(index_clause, index, variable, max_length=max_length, parents=parents)
            if clause != None:
                new_clauses.append(clause) # only add non-tautological, not-too-long clauses
           
        return new_clauses
      

    def resolve_all_with_clause(self, index_clause, force_increasing_index=False, min_index=0, max_length=30000, parents=False):
        """
        This method returns a list of all clauses with at most `max_length` many literals
        that can be obtained by resolution of the clause at `index_clause` in the clause set.
        If force_increasing_index is set to True, then all clauses with a clause index less than index_clause are ignored.
        """
        clause_vars = self.clauses[index_clause].get_variables()
        new_clauses = []
        
        for var in clause_vars:
            new_clauses.extend(self.resolve_all_with_clause_on_variable(index_clause, var, force_increasing_index, min_index=min_index, max_length=max_length, parents=parents))              
        return new_clauses
      

    def resolve_all(self, min_index=0, max_length=30000, parents=False):
        """
        This method returns a list of all clauses with at most `max_length` many literals
        that can be obtained by one resolution step from the formula (i.e. the "level 1 resolvents").
        """
        new_clauses = []
        for clause_index in range(self.n_clauses):
            new_clauses.extend(self.resolve_all_with_clause(clause_index, force_increasing_index=True, min_index=min_index, max_length=max_length, parents=parents))
            
        return new_clauses
		

    def remove_variable_from_clause(self, index, variable):
        occurrences = self.variable_dict[variable]
        self.variable_dict[variable] = None
        # occurrences = self.variable_dict.pop(variable, None)
        clause = self.clauses[index]
        self.clauses[index] = None
        # clause = self.clauses.pop(index, None)
        if occurrences == None:
            print("Error: variable", variable, "does not exist.")
            quit()
        if clause == None:
            print("Error: clause", index, "does not exist.")
            quit()

        # print("index:",index, "variable:",variable)
        # print(occurrences)
        occurrences.remove(index)  ## variable does not occur in the clause anymore - remove it.
        self.variable_dict[variable] = occurrences
        clause.remove_variable(variable)  ## variable removed from clause
        if clause.get_length() != 0:  ## if the clause became empty it does not has to be added to the clauses dict anymore. 
            self.clauses[index] = clause

        return clause.get_length() # returns 0 if the formula became unsatisfiable



    


        



            
