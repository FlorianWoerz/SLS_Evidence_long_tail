# -*- coding: utf-8 -*-

import unittest
import os, glob
from shutil import rmtree, copy2
import sys
from copy import deepcopy
from more_itertools import powerset
import sys
sys.path.insert(0,'..')

import pyximport; pyximport.install(setup_args={})
import parse_formula as pf
import more_resolution_formula as r




# Specify the folderpaths used during testing
tmpfolder = "./tmp_resolution"


class TestResolution(unittest.TestCase):

    def setUp(self):
        # SetUp will be called before every test.
        # Makes sure, that the folders ./tmp_resolution exists. 
        os.makedirs(tmpfolder, exist_ok=True)   

        
    def tearDown(self):
        # Will be run after every test.
        # Makes sure that the temporary directories are deleted.
        # Makes sure that all cnf-files are deleted.
        rmtree(tmpfolder)
        for f in glob.glob("./gen_*.cnf"):
            os.remove(f)
        

    def test_okay(self):
        # Test if the test framework works properly.
        print(sys._getframe(  ).f_code.co_name)
        self.assertTrue(True)
        print("Test Framework okay.")
        print(os.getcwd())

    ###############################################################
    ###### Tests for the function resolve_all_add_to_formula ######
    ###############################################################

    #python3 -m unittest tests.test_resolution.TestResolution.test_parents

    def read_cnf(self, path):
        filepath = os.path.realpath(path)
        self.formula, _, _ = pf.parse_formula(filepath)
        self.cnf = r.MoreResolutionFormula(form=self.formula)
        return self.cnf


    def assert_parents(self, results):
        result_p1_p2 = []

        for x in results:
            p1, p2 = x.get_parents()
            p1, p2 = str(p1).strip().split(" "), str(p2).strip().split(" ")
            p1 = [int(i) for i in p1]
            p2 = [int(i) for i in p2]
            p1.remove(0)
            p2.remove(0)

            result_p1_p2.append( (list(x.variables), p1, p2) )


        for i in range(len(result_p1_p2)-1,-1,-1):
            tupel = result_p1_p2[i]

            second_tuple_elements = [a_tuple[1] for a_tuple in result_p1_p2[:i+1]]
            third_tuple_elements = [a_tuple[2] for a_tuple in result_p1_p2[:i+1]]


            self.assertIn(tupel[1], second_tuple_elements)
            self.assertIn(tupel[2], third_tuple_elements)



    def test_parents(self):
        print(sys._getframe(  ).f_code.co_name)

        resolvents = self.obtain_resolvents_with_min_index_converge\
            (path="./tests/test_instanzen/input_res_10.cnf", min_index=9, parents=True)

        results = []        
        for level_results in resolvents.values():
            results.extend(level_results)

        self.assert_parents(results)

        ##

        resolvents2 = self.obtain_resolvents_with_min_index_converge\
            (path='./tests/test_instanzen/uf250-01.cnf', min_index=3, parents=True)

        results = []        
        for level_results in resolvents.values():
            results.extend(level_results)

        self.assert_parents(results)




    def test_not_too_long_clauses(self):
        print(sys._getframe(  ).f_code.co_name)
        filepath = os.path.realpath('./tests/test_instanzen/uf250-01.cnf')
        self.formula, _, _ = pf.parse_formula(filepath)
        self.cnf = r.MoreResolutionFormula(form=self.formula)

        length_to_test = [1,2,3,4,5,6,7,8]

        for length in length_to_test: 
            cnf = deepcopy(self.cnf)           
            resolvents = cnf.resolve_all_add_to_formula(max_length=length)
            for cls in resolvents:
                self.assertLessEqual(len(cls.variables), length)

        length_to_test = [4, 3]
        self.cnf = r.MoreResolutionFormula(form=self.formula) 
        for length in length_to_test:          
            resolvents = self.cnf.resolve_all_add_to_formula(max_length=length)
            for cls in resolvents:
                self.assertLessEqual(len(cls.variables), length)


    def test_clauses_are_added_to_the_formula_object(self):
        print(sys._getframe(  ).f_code.co_name)
        filepath = os.path.realpath('./tests/test_instanzen/uf250-01.cnf')
        self.formula, _, _ = pf.parse_formula(filepath)
        self.cnf = r.MoreResolutionFormula(form=self.formula)
        resolvents = self.cnf.resolve_all_add_to_formula(max_length=4)
        clauses = self.cnf.clauses.values()
        for resolvent in resolvents:
            self.assertIn(resolvent, clauses)


        resolvents = self.cnf.resolve_all_add_to_formula(max_length=5)
        clauses = self.cnf.clauses.values()
        for resolvent in resolvents:
            self.assertIn(resolvent, clauses) 

    


    def obtain_resolvents_with_min_index(self, path, min_index):
        self.cnf = self.read_cnf(path)
        return self.cnf.resolve_all_add_to_formula(min_index=min_index)
    
    def assert_resolvents_equal_expected(self, resolvents, expected_results):
        for result in resolvents:
            self.assertIn(result, expected_results)
        for expected in expected_results:
            self.assertIn(expected, resolvents)

    
    def test_min_index(self):
        print(sys._getframe(  ).f_code.co_name)
        resolvents = self.obtain_resolvents_with_min_index\
            ('./tests/test_instanzen/resolution.cnf', 7)

        expected_results = [[2,5], [-4], [3]]
        actual_results = [sorted(x.variables) for x in resolvents]
        self.assert_resolvents_equal_expected(actual_results, expected_results)


        resolvents = self.obtain_resolvents_with_min_index\
            ('./tests/test_instanzen/k3-n500-m2100-r4.200-s1367145976.cnf', 2098)

        expected_results = [[27, 209, 290, -349], [27, 209, 312, 201], [27, 209, 158, 40],
            [27, 209, -50, -425], [27, 209, -183, 342], [27, 209, -167, -382],
            [27, 209, -432, -494], [27, 209, 2, 373],
            [27, -59, 179, 222], [27, -59, -325, -301], [27, -59, -475, -210],
            [209, -59, -282, -248], [209, -59, -8, 33], [209, -59, -359, 286],
            [-152, 396, 311, -6], [-152, 396, 256, -476], [-152, 396, 71, 319],
            [-152, 396, 15, -47], [-152, 396, -286, 159], [-152, 396, 247, -289],
            [-152, 396, 452, 441],
            [328, -152, -155, -459], [328, -152, -37, 181], [328, -152, 344, -300],
            [328, -152, -476, -488], [328, -152, 322, -74], [328, -152, 294, 54],
            [328, -152, -241, -446], [328, -152, 450, -103],
            [328, 396, -311, -276], [328, 396, 310, -224], [328, 396, -292, -205],
            [328, 396, -422, -278], [328, 396, -147, -102] ]
        expected_results = [sorted(x) for x in expected_results]
        actual_results = [sorted(x.variables) for x in resolvents]
        self.assert_resolvents_equal_expected(actual_results, expected_results)

    
    def obtain_resolvents_with_min_index_converge(self, path, min_index, parents=False):
        self.cnf = self.read_cnf(path)
        return self.cnf.resolve_to_convergence(min_index, parents)

    def test_resolve_to_convergence(self):
        print(sys._getframe(  ).f_code.co_name)
        resolvents = self.obtain_resolvents_with_min_index_converge\
            ("./tests/test_instanzen/input_res_10.cnf", 9)
        results = []
        for level_results in resolvents.values():
            results.extend(level_results)
        results = [set(x.variables) for x in results]
        expected = list(powerset(range(1,11)))
        expected = [set(x) for x in expected if x != (1,2,3,4,5,6,7,8,9,10)]

        self.assert_resolvents_equal_expected(results, expected)

        resolvents = self.obtain_resolvents_with_min_index_converge\
            ("./tests/test_instanzen/input_res_14.cnf", 13)
        results = []
        for level_results in resolvents.values():
            results.extend(level_results)
        results = [set(x.variables) for x in results]
        expected = list(powerset(range(1,15)))
        expected = [set(x) for x in expected if x != (1,2,3,4,5,6,7,8,9,10,11,12,13,14)]
        self.assert_resolvents_equal_expected(results, expected)
        


  
###############################################################################################
###############################################################################################

        
if sys._getframe(  ).f_code.co_name == '__main__':
    unittest.main()