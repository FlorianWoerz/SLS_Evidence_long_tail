import unittest
import sys
sys.path.insert(0,'..')

import resolution.parse_formula as f

class ParseTest(unittest.TestCase):

    def test_line(self):
        self.assertEqual(f.parse_line("1 -2 5 0"), [1, -2, 5])
        self.assertEqual(f.parse_line("c 1 -2 5 0"), None)
        self.assertEqual(f.parse_line("p cnf 1000 4199"), None)

    def test_parse_length(self, filepath='./tests/test_instanzen/uf250-01.cnf', n=250, m=1067):
        with open(filepath, 'r') as file:
            lines = file.readlines()
            (n_test,m_test) = f.parse_length(lines)
            self.assertEqual(n, n_test )
            self.assertEqual(m, m_test)

    def test_parse_formula(self, filepath='./tests/test_instanzen/uf250-01.cnf', n=250, m=1067):
        (formula, n_test, m_test) = f.parse_formula(filepath)
        self.assertEqual(n,formula.n_variables)
        self.assertEqual(m, formula.n_clauses)
        self.assertEqual(sorted(formula.clauses[0].get_variables()), sorted([-248, -113, -236]))
        self.assertEqual(sorted(formula.clauses[m_test-1].get_variables()),sorted([-166, 239, -39]))
        self.assertEqual(formula.variable_dict[-1], {54, 340, 644, 974})
        
if __name__ == '__main__':
    unittest.main()