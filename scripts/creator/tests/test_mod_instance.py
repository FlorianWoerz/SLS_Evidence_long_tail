import unittest
import os, glob
import filecmp
from os.path import isfile
from shutil import rmtree, copy2
from scipy.stats import binom_test
import sys

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

#from random import randint, seed
import random

import mod_instance as g

class TestModInstance(unittest.TestCase):

    def setUp(self):
        os.makedirs("./tests/tmp_test", exist_ok=True)
        os.makedirs("./tests/tmp_test_2", exist_ok=True)

    def tearDown(self):
        rmtree("./tests/tmp_test")
        rmtree("./tests/tmp_test_2")

    def assertRaisesTypeError(self, orig, resolvents, s=1, M=10, o='./test_instances/out',p=None):
        with self.assertRaises(TypeError):
            g.modify_instance(orig, resolvents, seed=s, M=M, outputPath=o, p=p)

    # python3 -m unittest tests.test_mod_instance.TestModInstance.test_valid_parameters
    def test_valid_parameters(self):
        print(sys._getframe(  ).f_code.co_name)
        # We test whether only valid parameter combinations are accepted.

        # We start with testing by passing parameters of the wrong type.
        res_path = "./tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents"
        orig = "./tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf"
        self.assertRaisesTypeError(17.0, res_path)
        self.assertRaisesTypeError(orig, 43)
        self.assertRaisesTypeError(orig, res_path, s=1.0)
        self.assertRaisesTypeError(orig, res_path, M=13.0)
        self.assertRaisesTypeError(orig, res_path, o=17)
        self.assertRaisesTypeError(orig, res_path, p=1)

        # Next parameters of the right type but with invalid values are tested.
        # The p-value must be in (0.0, 1.0]
        with self.assertRaises(ValueError):
            g.modify_instance(orig, res_path, p=1.1)
        with self.assertRaises(ValueError):
            g.modify_instance(orig, res_path, p=-0.1)
        with self.assertRaises(ValueError):
            g.modify_instance(orig, res_path, p=0.0)

        # The M-value must be positive.
        with self.assertRaises(ValueError):
            g.modify_instance(orig, res_path, M=-1)
        with self.assertRaises(ValueError):
            g.modify_instance(orig, res_path, M=0)

        # Finally, the two paths, orig and resolvents, should point to existing files.
        with self.assertRaises(FileNotFoundError):
            g.modify_instance("./tests/test_instances/does_not_exist.cnf", res_path)
        with self.assertRaises(FileNotFoundError):
            g.modify_instance(orig, "./tests/test_instances/does_not_exist.cnf")


    def create_file(self, orig, res, base_path='./modified/', s=1, p=None, shuffle=False):
        if p is None:
            number_orig_clauses = len(self.get_body(orig))
            number_resolvents = len(self.get_body(res))
            p = float(number_orig_clauses)/(10.0*number_resolvents)
        g.modify_single(orig, res, outputPath=base_path, seed=s, p=p, shuffle=shuffle)
        mod_name = os.path.basename(orig)
        mod_name = mod_name.replace(".cnf", "") + f"_mod_s{s}_p{p}.cnf"
        mod_name = os.path.join(base_path, mod_name)
        return mod_name


    def assert_filename_equals(self, orig, res, base_path='./modified/', s=1, p=None):
        mod_name = self.create_file(orig, res, base_path=base_path, s=s, p=p)  
        self.assertTrue(os.path.isfile(mod_name))


    def test_generated_name(self):
        # Checks whether the generated files have the correct name and whether they
        # are generated in the correct folder.
        
        # If no path is specified the files should be generated in './modified/'

        print(sys._getframe(  ).f_code.co_name)

        # The filename should be './modified/k3-n500-m2100-r4.200-s1367145976_mod_s{seed}_p0.05.cnf'
        orig = "./tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf"
        res = "./tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents"
        s=13
        p=0.05
        self.assert_filename_equals(orig, res, s=13, p=0.05)

        # If p is not specified, then it should be set to number_orig_clauses/(number_resolvents * 10) by default.
        # Thus the filename should be set accordingly.
        # We also test, whether non-existing base folder is created.
        rmtree('./tests/mod2/', ignore_errors=True)
        self.assert_filename_equals(orig, res, base_path='./tests/mod2/', s=17)
        rmtree("./tests/mod2/")

    def test_reproducibility(self):
        # Check whether calls with identical parameters yield identical files.
        
        print(sys._getframe(  ).f_code.co_name)

        o = "./tests/tmp_test"      

        orig = "./tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf"
        res = "./tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents"

        path1 = self.create_file(orig, res, s=1909, p=0.3)
        path2 = os.path.join(o, os.path.basename(path1))

        copy2(path1, path2)
        os.remove(path1)
        path1 = self.create_file(orig, res, s=1909, p=0.3)
        # filecmf.cmp(_,_) überprüft ob zwei Dateien identisch sind.
        # Allerdings werden nur die Statistiken (Hash-Werte etc.) verglichen.
        # Für einen Byte-für-Byte Vergleich muss shallow=False gesetzt werden.
        if not filecmp.cmp(path1, path2):
            print(path1, path2)
        self.assertTrue(filecmp.cmp(path1, path2))
        os.remove(path1)
        os.remove(path2)

        # We test whether this also works if the p-value is not passed.
        path1 = self.create_file(orig, res, s=999)
        path2 = os.path.join(o, os.path.basename(path1))
        copy2(path1, path2)
        os.remove(path1)
        path1 = self.create_file(orig, res, s=999)
        self.assertTrue(filecmp.cmp(path1, path2))
        os.remove(path1)
        os.remove(path2)

        # Finally, we test whether several files can be reproduced.
        orig = './tests/test_instances/uf250-01.cnf'
        res = './tests/test_instances/uf250-01.resolvents'
        s = 9
        M = 10
        o_second = "./tests/tmp_test_2"

        g.modify_instance(orig, res, M=M, seed=s, outputPath=o)
        for file in os.listdir(o):
            file_path = os.path.join(o, file)
            if isfile(file_path):
                copy2(file_path, o_second)
                os.remove(file_path)

        g.modify_instance(orig, res, M=M, seed=s, outputPath=o)
        for file in os.listdir(o):
            file_path_orig = os.path.join(o, file)
            file_path_copy = os.path.join(o_second, file)
            # Above we iterate over all files and folders in the directory `o`.
            # Thus, we have to distinguish between folders and files.
            if isfile(file_path_orig):
                self.assertTrue(filecmp.cmp(file_path_orig, file_path_copy))
                os.remove(file_path_orig)
                os.remove(file_path_copy)

    def test_reproducibility_with_shuffle_flag(self):
        print(sys._getframe(  ).f_code.co_name)
        # Test the shuffle flag
        orig = './tests/test_instances/uf250-01.cnf'
        res = './tests/test_instances/uf250-01.resolvents'
        s = 934
        M = 14
        o = './tests/tmp_test'
        o_second = './tests/tmp_test_2'
        g.modify_instance(orig, res, M=M, seed=s, outputPath=o, shuffle=True)
        for file in os.listdir(o):
            file_path = os.path.join(o, file)
            if isfile(file_path):
                copy2(file_path, o_second)
                os.remove(file_path)

        g.modify_instance(orig, res, M=M, seed=s, outputPath=o, shuffle=True)
        for file in os.listdir(o):
            file_path_orig = os.path.join(o, file)
            file_path_copy = os.path.join(o_second, file)
            # Above we iterate over all files and folders in the directory `o`.
            # Thus, we have to distinguish between folders and files.
            if isfile(file_path_orig):
                self.assertTrue(filecmp.cmp(file_path_orig, file_path_copy))
                os.remove(file_path_orig)
                os.remove(file_path_copy)


    def get_header(self, filename):
        # This method returns the header of a specified file as a list of strings.
        # The header are all lines starting with 'c' (comment line) or 'p' until
        # a line starts with neither.
        lines = []
        with open(filename, 'r') as file:
            line = file.readline()
            while line and (line.startswith("c") or line.startswith("p")):
                lines.append(line)
                line = file.readline()
        return lines

    def get_body(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
        body = []
        for line in lines:
            if not (line.startswith("c") or line.startswith("p")):
                body.append(line)

        return body
        
    def get_all_lines(self, filename):
        # This method simply retuns all lines of a specified file as a list of strings.
        with open(filename, 'r') as file:
            lines = file.readlines()
        return lines

    def assert_right_header(self, orig, res, s=1, p=None):
        path = self.create_file(orig, res, s=s, p=p)

        # The number of resolvents is needed for checking the header.
        # This is not the most elegant solution. But (I suppose) it works.
        n_resolvents = len(self.get_body(res))
        # Also, the header of the original .cnf file is necessary.
        orig_header = self.get_header(orig)
        # And, obviously, the header of the modified file is needed.
        mod_header = self.get_header(path)

        if p is None:
            # The number of original clauses is the last element in the last line
            # of the original header.
            p = float(orig_header[-1].split()[-1]) / (10.0 * n_resolvents)

        # The header should have the following form:
        # 'c Modified by xyzFancyModifier'
        # 'c Used with seed {s} and p {p}'
        # 'c Sampled from {n_resolvents} resolvents'
        # 'c Original cnf file {basename(orig)}'
        # 'c Resolvent file {(basename(res))}'
        # ... the original header
        # 'p cnf orig_n_variables {m_orig_clauses + X_sampled_clauses}'
        self.assertEqual(mod_header[0], 'c Modified by xyzFancyModifier\n')
        self.assertEqual(mod_header[1], f'c Used with seed {s} and p {p}\n')
        self.assertEqual(mod_header[2], f'c Sampled from {n_resolvents} resolvents\n')
        self.assertEqual(mod_header[3], f'c Original cnf file {os.path.basename(orig)}\n')
        self.assertEqual(mod_header[4], f'c Resolvent file {os.path.basename(res)}\n')
        i = 1
        # The last line, i.e., the parameter line has to be checked separately.
        for orig_line in orig_header[:-1]:
            self.assertEqual(mod_header[4 + i], orig_line)
            i += 1

        # The original parameter line should be:
        # 'p cnf {n_orig} {m_orig_clauses + X_sampled_clauses}'
        # Thus, X_sampled_clauses has to be >= 0.
        mod_parameter_line = mod_header[-1]

        # We first check whether the parameter line has the right format.
        self.assertRegex(mod_parameter_line, "^p cnf ([1-9][\d]*) ([1-9][\d]*)\n$")
        # Secondly, we check whether the first three elements match.
        mod_parameter_line_chunks = mod_parameter_line.split()
        orig_parameter_line_chunks = orig_header[-1].split()
        for i in range(len(mod_parameter_line_chunks) - 1):
            self.assertEqual(mod_parameter_line_chunks[i], orig_parameter_line_chunks[i])
        # Finally, we check whether the last element in the modified header
        # is at least as big as the last chunk in the original header.
        self.assertGreaterEqual(int(mod_parameter_line_chunks[-1]), int(orig_parameter_line_chunks[-1]))

        os.remove(path)
        
    def test_header(self):
        print(sys._getframe(  ).f_code.co_name)
        # This method checks whether the header is generated as specified.
        orig = './tests/test_instances/uf250-01.cnf'
        res = './tests/test_instances/uf250-01.resolvents'
        s = 19
        p = 0.03
        self.assert_right_header(orig, res, s=s, p=p)

        orig = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf'
        res = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents'
        s = 1111
        p = None
        self.assert_right_header(orig, res, s=s, p=p)


    def assert_clauses_from_orig_and_resolvents(self, orig, res, s=1, p=None, shuffle=False):
        path = self.create_file(orig, res, s=s, p=p, shuffle=shuffle)

        resolvents = set(self.get_body(res))
        orig_body = set(self.get_body(orig))
        mod_body = set(self.get_body(path))

        # Each clause should be from either the resolvents or the original clauses.
        for clause in mod_body:
            # This allow reshuffeling of the clauses, i.e, the clauses do not have to appear in the same order.
            in_set = (clause in orig_body) or (clause in resolvents)
            self.assertTrue(in_set)

        # Each clause of the original clauses should appear in the modified file.
        for clause in orig_body:
            self.assertIn(clause, mod_body)

        os.remove(path)


    def test_clauses_from_orig_and_resolvents(self):
        print(sys._getframe(  ).f_code.co_name)

        orig = './tests/test_instances/uf250-01.cnf'
        res = './tests/test_instances/uf250-01.resolvents'
        s = 199
        p = None
        self.assert_clauses_from_orig_and_resolvents(orig, res, s=s, p=p)

        orig = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf'
        res = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents'
        s = 111
        p = 0.5
        self.assert_clauses_from_orig_and_resolvents(orig, res, s=s, p=p)

        orig = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf'
        res = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents'
        s = 112
        p = 0.7
        self.assert_clauses_from_orig_and_resolvents(orig, res, s=s, p=p, shuffle=True)


    def assert_right_number_of_clauses(self, orig, res, s=1, p=None):
        # The header contains the parameter line:
        # p cnf n m
        # m specifies the number of clauses.
        # This method checks whether m is actually the number of clauses.
        path = self.create_file(orig, res, s=s, p=p)

        # The parameter line is the last line of the header.
        parameter_line = self.get_header(path)[-1]

        # The last element of the parameter line is the expected number of clauses.
        expected_m_clauses = int(parameter_line.split()[-1])
        actual_m_clauses = len(self.get_body(path))

        self.assertEqual(expected_m_clauses, actual_m_clauses)
        os.remove(path)


    def test_right_number_of_clauses(self):
        print(sys._getframe(  ).f_code.co_name)

        orig = './tests/test_instances/uf250-01.cnf'
        res = './tests/test_instances/uf250-01.resolvents'
        s = 1000
        p = None
        self.assert_right_number_of_clauses(orig, res, s=s, p=p)

        orig = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf'
        res = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents'
        s = 1010
        p = 0.99
        self.assert_right_number_of_clauses(orig, res, s=s, p=p)

    def is_int_max(self, x, m):
        # Checks whether x can be converted to int AND the absolute value of
        # int(x) is at most m.
        try:
            if abs(int(x)) <= m:
                return True
            else:
                return False
        except ValueError:
            return False
        
    def assert_proper_clauses(self, orig, res, s=1, p=None, shuffle=False):
        # This method ensures that the clauses in the body are actually clauses in the right format.
        # To be precise: Every clause needs to have the form: int int ... int 0
        # where each int is at most n (the number of variables).
        # Furthermore, tautologies are not allowed, i.e., x int ... int -x should not occur.
        # Finally, double literals are also not admissible, i.e., x int ... int x.

        path = self.create_file(orig, res, s=s, p=p, shuffle=shuffle)

        # The parameter line is the last line of the header.
        parameter_line = self.get_header(path)[-1]

        # The parameter line has the form: p cnf n_variables m_clauses
        # We require n_variables
        n_variables = int(parameter_line.split()[2])

        body = self.get_body(path)
        for clause in body:
            # First, we check whether each clause ends with " 0\n"
            self.assertTrue(clause.endswith(" 0\n"))
            # We then omit the suffix " 0\n".
            literals = clause.split()[:-1]
            for literal in literals:
                # We assert whether each literal can be casted to an int with absolute value at most n_variables
                self.assertTrue(self.is_int_max(literal, n_variables))
            # Finally, we convert the literals to a set, such that each literal is mapped to its absolute value.
            lit_set = set( [ abs((int(s))) for s in literals ] )
            # If the clause is either a tautology or double literals occur, then the length of the set
            # will not match the length of the literals list.
            # Otherwise, this test is passed.
            self.assertEqual(len(literals), len(lit_set))

        os.remove(path)


    def test_proper_clauses(self):
        print(sys._getframe(  ).f_code.co_name)
        # Test whether...
        # 1) ... the clauses are in the proper DIMACS format.
        # 2) ... there are no tautological clauses.
        # 3) ... there are no clauses with double literals.
        orig = './tests/test_instances/uf250-01.cnf'
        res = './tests/test_instances/uf250-01.resolvents'
        s = 1001
        p = 0.2
        self.assert_proper_clauses(orig, res, s=s, p=p)

        orig = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf'
        res = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents'
        s = 1011
        p = None
        self.assert_proper_clauses(orig, res, s=s, p=p)

        orig = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf'
        res = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents'
        s = 123
        p = None
        shuffle = True
        self.assert_proper_clauses(orig, res, s=s, p=p, shuffle=shuffle)

        orig = './tests/test_instances/gen_n12_m36_k3SAT_seed4150886330.cnf'
        res = './tests/test_instances/gen_n12_m36_k3SAT_seed4150886330.resolvents'
        s = 1234
        p = 0.000503919372900336
        shuffle = False
        self.assert_proper_clauses(orig, res, s=s, p=p, shuffle=shuffle)

        orig = './tests/test_instances/gen_n12_m36_k3SAT_seed4150886330.cnf'
        res = './tests/test_instances/gen_n12_m36_k3SAT_seed4150886330.resolvents'
        s = 1234
        p = 0.000503919372900336
        shuffle = True
        self.assert_proper_clauses(orig, res, s=s, p=p, shuffle=shuffle)




    def check_probabilities(self, orig, res, s=1, p=None):
        # Each resolvent should be added with probability p.
        # Here, we check whether this is actually the case.
        # This is a "soft" check relying on a statistical test,
        # meaning that this check fails in 5% of the cases even if the assumption is true.
        # Therefore, this test should be performed repeatedly.

        #print("check probabilites")
        path = self.create_file(orig, res, s=s, p=p)

        # To assess the assumption, we need ...
        # ... the number of resolvents, and ...
        n_resolvents = len(self.get_body(res))
        # ... the number of original clauses, and ...
        n_original = len(self.get_body(orig))
        # ... the number of clauses in the modified file.
        n_mod = len(self.get_body(path))

        # Furthermore, the actual p-value is necessary.
        if p is None:
            p = float(n_original)/(10.0*n_resolvents)

        # We perform the binomial test.
        # The null hypothesis is that each clause is accepted with probability p.
        # See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom_test.html#scipy.stats.binom_test
        # and https://en.wikipedia.org/wiki/Binomial_test
        # for more information.
        # Note, that the p_value is not correlated to p.
        p_value = binom_test(n_mod-n_original, n_resolvents, p)

        if p_value < 0.05:
            print("WARNING for instance", orig)
            print("The binomial test failed, indicating a possible problem in the generation")
        else:
            print("Everything looks fine. The binomial test was passed for instance", orig)
        print("p-value", p_value)

        os.remove(path)

        
    def test_probabilities(self):
        print(sys._getframe(  ).f_code.co_name)
        orig = './tests/test_instances/uf250-01.cnf'
        res = './tests/test_instances/uf250-01.resolvents'
        rngtest = random.Random()
        for i in range(1, 20):
            s = rngtest.randint(1, 2**32 - 1)
            p = 0.05
            self.check_probabilities(orig, res, s=s, p=p)

        orig = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.cnf'
        res = './tests/test_instances/k3-n500-m2100-r4.200-s1367145976.resolvents'
        s = rngtest.randint(1, 2**32 - 1)
        p = None
        self.check_probabilities(orig, res, s=s, p=p)

    def test_shuffle(self):
        # Test the shuffle flag
        print(sys._getframe(  ).f_code.co_name)

        # Specify the original and copy directory
        o = './tests/tmp_test' 
        o_second = './tests/tmp_test_2'

        # Specify the instance and resolvents file, as well as the parameters to use
        orig = './tests/test_instances/uf250-01.cnf'
        res = './tests/test_instances/uf250-01.resolvents'
        s = 984
        M = 14
        
        # Create the files without shuffeling the clauses
        g.modify_instance(orig, res, M=M, seed=s, outputPath=o, shuffle=False)

        # Copy the files to `o_second` and delete them in `o`
        for file in os.listdir(o):
            file_path = os.path.join(o, file)
            if isfile(file_path):
                copy2(file_path, o_second)
                os.remove(file_path)

        # Create the files again, but this time *with* shuffeling
        g.modify_instance(orig, res, M=M, seed=s, outputPath=o, shuffle=True)

        for file in os.listdir(o):
            file_path_orig = os.path.join(o, file)
            file_path_copy = os.path.join(o_second, file)
            # Above we iterate over all files and folders in the directory `o`.
            # Thus, we have to distinguish between folders and files.
            if isfile(file_path_orig):
                # Compare if the files are not the same (this should be the case because of the shuffling)
                #print(file_path_orig)
                #print(file_path_copy)
                self.assertFalse(filecmp.cmp(file_path_orig, file_path_copy))

                # Next, compare if the files contain the same clauses (just in a different order... w.h.p.)
                unshuffled_clauses = set(self.get_body(file_path_orig))
                shuffled_clauses = set(self.get_body(file_path_copy))                
                for clause in unshuffled_clauses:                    
                    in_set = (clause in shuffled_clauses)
                    self.assertTrue(in_set)
                for clause in shuffled_clauses:
                    in_set = (clause in unshuffled_clauses)
                    self.assertTrue(in_set)

                # Finally, remove the files
                os.remove(file_path_orig)
                os.remove(file_path_copy)

        
        
if __name__ == 'main':
    unittest.main()