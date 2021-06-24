import unittest
import os.path
import sys
sys.path.insert(0,'..')

import pyximport; pyximport.install(setup_args={})
import parse_formula as f   # import your stuff




#import parse_formula as f




class ParseTest(unittest.TestCase):


    #filepath = './test_instanzen/uf250-01.cnf'
    filepath = os.path.realpath('./tests/test_instanzen/uf250-01.cnf')
    formula, _, _ = f.parse_formula(filepath)
        
    def test_resolve_on_variable(self):
        # Check general resolution
        # Klausel 161: 38 -210 1
        # Klausel 340: -1 -98 87
        # Ergebnis: -210 -98 38 87
        resolvent = self.formula.resolve_on_variable(161, 340, -1)
        resolvent = list(resolvent.variables)
        resolvent.sort()
        self.assertEqual(resolvent, [-210, -98, 38, 87])
        
        # Check if a redundant literal is omitted
        # Klausel 0:  -248 -113 -236 
        # Klausel 1065:  -200 113 -236
        # Ergebnis: -248 -236 -200
        resolvent = self.formula.resolve_on_variable(0, 1065, 113)
        resolvent = list(resolvent.variables)
        resolvent.sort()
        self.assertEqual(resolvent, [-248, -236, -200])
        
        # Check if multiple redundant literals are omitted
        # Klausel 3: 166 239 -39
        # Klausel 1066: -166 239 -39
        # Ergebnis: -39 239
        resolvent = self.formula.resolve_on_variable(3, 1066, -166)
        resolvent = list(resolvent.variables)
        resolvent.sort()
        self.assertEqual(resolvent, [-39, 239])

            
    def test_find_partner_clauses_on_variable(self):
        ### Test non-increasing ###
        # Klausel 10: 87 61 109
        # Klauseln mit -87: 35, 142, 318, 532, 549, 756, 1001, 1032
        indices = self.formula.find_partner_clauses_on_variable(10,87)
        self.assertEqual(set(indices), set([35, 142, 318, 532, 549, 756, 1001, 1032]))
        
        # Klauseln mit -61: 107, 129, 305, 572, 620, 711, 902
        indices = self.formula.find_partner_clauses_on_variable(10,61)
        self.assertEqual(set(indices), set([107, 129, 305, 572, 620, 711, 902]))        
        
        # Klauseln mit -109: 78, 98, 435, 663, 750, 752, 779 
        indices = self.formula.find_partner_clauses_on_variable(10,109)
        self.assertEqual(set(indices), set([78, 98, 435, 663, 750, 752, 779]))
        
        
        ### Test increasing ###
        # Klausel 812: -173 -235 164
        # Klauseln mit 173: (61, 399, 480, 575, 672,) 820, 917, 1059
        indices = self.formula.find_partner_clauses_on_variable(812,-173, force_increasing_index=True)
        self.assertEqual(set(indices), set([820, 917, 1059]))
        
        # Klauseln mit 235: (35, 57, 72, 310, 346, 430, 462,) 1052
        indices = self.formula.find_partner_clauses_on_variable(812,-235, force_increasing_index=True)
        self.assertEqual(set(indices), set([1052]))
        
        # Klauseln mit -164: (169, 608, 725,) 872, 1006
        indices = self.formula.find_partner_clauses_on_variable(812,164, force_increasing_index=True)
        self.assertEqual(set(indices), set([872, 1006]))

    def test_resolve_all_with_clause(self):
        clause_results  = []
        ### Test non-increasing ###
        # Klausel 10: 87 61 109
        clause_index = 10
        # Klauseln mit -87: 35, 142, 318, 532, 549, 756, 1001, 1032
        variable = 87
        indices = [35, 142, 318, 532, 549, 756, 1001, 1032]
        for index in indices:
            clause_results.append(set(self.formula.resolve_on_variable(clause_index, index, variable).variables))
        
        # Klauseln mit -61: 107, 129, 305, 572, 620, 711, 902
        variable = 61
        indices = [107, 129, 305, 572, 620, 711, 902]
        for index in indices:
            clause_results.append(set(self.formula.resolve_on_variable(clause_index, index, variable).variables))        
        
        # Klauseln mit -109: 78, 98, 435, 663, 750, 752, 779 
        variable = 109
        indices = [78, 98, 435, 663, 750, 752, 779]
        for index in indices:
            clause_results.append(set(self.formula.resolve_on_variable(clause_index, index, variable).variables))

        test_result = self.formula.resolve_all_with_clause(clause_index)
        test_result = [set(x.variables) for x in test_result]
        self.assertCountEqual(test_result, clause_results) # checks if two lists are equal. Ignores order.
        
        
        ### Test increasing ###
        clause_results  = []
        # Klausel 812: -173 -235 164
        clause_index = 812
        # Klauseln mit 173: (61, 399, 480, 575, 672,) 820, 917, 1059
        variable = -173
        indices = [820, 917, 1059]
        for index in indices:
            clause_results.append(set(self.formula.resolve_on_variable(clause_index, index, variable).variables))
        
        # Klauseln mit 235: (35, 57, 72, 310, 346, 430, 462,) 1052
        variable = -235
        indices = [1052]
        for index in indices:
            clause_results.append(set(self.formula.resolve_on_variable(clause_index, index, variable).variables))
        
        # Klauseln mit -164: (169, 608, 725,) 872, 1006
        variable = 164
        indices = [872, 1006]
        for index in indices:
            clause_results.append(set(self.formula.resolve_on_variable(clause_index, index, variable).variables))
        
        test_result = self.formula.resolve_all_with_clause(clause_index, True)
        test_result = [set(x.variables) for x in test_result]
        self.assertCountEqual(test_result, clause_results) # checks if two lists are equal. Ignores order.
  
    def test_resolve_all(self, path='./tests/test_instanzen/resolution.cnf'):
        formula, _, _ = f.parse_formula(path)
        # [-4,1,2] is a possible resolvent, but it is subsumed by [-4, 1] which is already in the original formula.
        # Hence, [-4, 1, 2] is not generated.
        expected_result = [ [2,5], [1,4,5], [1,2,-3], [-2,1,5], \
                            [-5,-4,-3], [-2, 4], [-5,-3], \
                            [-4], [2,-5,1], [3]   \
                          ]
        expected_result = [sorted(x) for x in expected_result]
        
        clauses = formula.resolve_all()
        actual_result = [sorted(x.variables) for x in clauses]
        print(actual_result)
        self.assertCountEqual(expected_result, actual_result)# checks if two lists are equal. Ignores order.

  
if __name__ == '__main__':
    unittest.main()
