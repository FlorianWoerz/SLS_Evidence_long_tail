import random
from itertools import chain, combinations

cdef dict variable_mapping = {}

cpdef init_variable_mapping(int n_vars, int seed):
    global variable_mapping
    rng = random.Random()
    rng.seed(seed)
    cdef list sample = random.sample(range(2**32-1), 2*n_vars)
    cdef int i = 0
    cdef int l
    for l in range(1, n_vars+1):
        variable_mapping[l] = sample[i]
        variable_mapping[-l] = sample[i+1]
        i += 2

cdef long calculate_hash_value(variables):
    return sum(map(lambda x: variable_mapping[x], variables))

cpdef long hash_value(variables):
    return calculate_hash_value(variables)

cdef int get_absolute_set_length(set variables):
    return len(set(map(abs, variables)))

cpdef resolve(set vars_clauseA, set vars_clauseB, int variable, int max_length, set hash_values):
        cdef set new_clause_vars = vars_clauseA.union(vars_clauseB)
        #new_clause_vars = new_clause_vars.update(vars_clauseB)
        #
        if len(new_clause_vars)-2 > max_length: # after resolving the two literals `variable` and -`variable` will be gone
            return None # The resolvent would be above allowed `max_length`


        # #if len(set(map(abs, new_clause_vars))) < len(new_clause_vars)-1:
        if get_absolute_set_length(new_clause_vars) < len(new_clause_vars)-1:
            return None # The resolvent would be tautological

        new_clause_vars = new_clause_vars.difference({variable, -variable})
        # # Subsumption check:
        # # We iterate over all possible subsets S of the literals in the resolvent R which satisfy 1 <= |S| <= |R|.
        # # If the hash value of S is alread present in the set of hash values of the formula F, we know that R is subsumed
        # # by another clause of the formula F.
        cdef int r
        cdef list comb
        for r in range(len(new_clause_vars), 0, -1):
            comb = list(combinations(new_clause_vars, r))
            for var_combination in comb:
                if calculate_hash_value(var_combination) in hash_values:
                    return None

        return new_clause_vars

