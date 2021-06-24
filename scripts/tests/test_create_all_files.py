import unittest
import os, glob
import filecmp
from os.path import isfile
from shutil import rmtree, copy2, copytree
import sys

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

import pyximport; pyximport.install(setup_args={})
import create_all_files as create_all

# The test folder that will be used:
test_folder = "./tests/tmp_test"
test_folder_copy = "./tests/tmp_test_copy"

# The names as in the folder structure:
instances_folder = "instances"
resolvents_folder = "resolvents"
mod_folder = "mod"

# Some of these tests take a long time to run.
# If you want to run only selected test, you can use:
# python3 -m unittest tests.test_create_all_files.TestCreateAll.test_NAME

class TestCreateAll(unittest.TestCase):
    
    def setUp(self):
        # Delete any manually created folder before the first test.
        # For a explanation see tearDown. 
        rmtree(test_folder, ignore_errors=True)
        rmtree(test_folder_copy, ignore_errors=True)


    def tearDown(self):
        # It is very important to delete the root folder we are working in.
        # Otherwise the tests will get interrupted by the fail-safe prompt asking the user if he wants to overwrite this folder.
        # Thus, we simply make use the folder doesn't exist at the beginning of any test.
        rmtree(test_folder, ignore_errors=True)
        rmtree(test_folder_copy, ignore_errors=True)


    def assertRaisesTypeError(self, N=10, ns=None, r=None, k=3, s=42, output_base_path=test_folder, ps=None, q=None, more=False, converge=True, times=2, max_length=4, shuffle=True, M=5000, c=None):
        with self.assertRaises(TypeError):
            create_all(N=N, ns=ns, r=r, k=k, s=s, output_base_path=output_base_path, ps=ps, q=q, more=more, converge=converge, times=times, max_length=max_length, shuffle=shuffle, M=M, c=c)


    # python3 -m unittest tests.test_create_all_files.TestCreateAll.test_valid_parameters
    def test_valid_parameters(self):
        print(sys._getframe(  ).f_code.co_name)
        # We test whether only valid parameter combinations are accepted.
        # We start with testing by passing parameters of the wrong type.
        self.assertRaisesTypeError()
        self.assertRaisesTypeError(N=1.0)
        self.assertRaisesTypeError(N="f")
        self.assertRaisesTypeError(N = [1, 2, 3])

        self.assertRaisesTypeError(N = 10, ns = 1)
        self.assertRaisesTypeError(N = 13, ns = 1.2)
        self.assertRaisesTypeError(N = 15, ns = "f")

        self.assertRaisesTypeError(N = 10, ns = [1, 2, 3], r = 4)

        # Note, that invalid parameters should be caught by the programs called in create_all_files.py
        # Thus, we do not test any further.


    def basic_folder_paths(self, root_folder):
        """Returns the paths to the folders of the original instance, the resolvents, and the modified files, as a tuple."""
        return os.path.join(root_folder, instances_folder), os.path.join(root_folder, resolvents_folder), os.path.join(root_folder, mod_folder)


    def assert_folder_structure(self, N=10, ns=None, r=None, k=3, s=42, output_base_path=test_folder, ps=None, q=None, more=False, converge=True, times=2, max_length=4, shuffle=True, M=5000, c=None):
        """Checks the basic folder structure as descriped in create_all_files.py"""

        create_all.main(N=N, ns=ns, r=r, k=k, s=s, output_base_path=output_base_path, ps=ps, q=q, more=more, converge=converge, times=times, max_length=max_length, shuffle=shuffle, M=M, c=c)

        # Check if there is a root folder
        root_folder = output_base_path
        self.assertTrue(os.path.isdir(root_folder))

        # Check if there are folders for the instances, resolvents, and modified instances
        instances_folder_path, resolvents_folder_path, mod_folder_path = self.basic_folder_paths(root_folder)

        self.assertTrue(os.path.isdir(instances_folder_path))
        self.assertTrue(os.path.isdir(resolvents_folder_path))
        self.assertTrue(os.path.isdir(mod_folder_path))

        # Check if there are subfolders for each n in the instances, resolvents, and modified instances folders, respectively
        for n in ns:
            self.assertTrue(os.path.isdir(os.path.join(instances_folder_path, f"n{n}")))
            self.assertTrue(os.path.isdir(os.path.join(resolvents_folder_path, f"n{n}")))
            self.assertTrue(os.path.isdir(os.path.join(mod_folder_path, f"n{n}")))

        # Check if there are folders in each n-folder of the modified instance folders, that are named after the instances in the instance folder
        # (Please see create_all_files.py for a description of the folder structure)
        for n in ns:
            dir = os.path.join(instances_folder_path, f"n{n}")
            for file in os.listdir(dir):
                self.assertTrue(os.path.isdir(os.path.splitext(os.path.join(os.path.join(mod_folder_path, f"n{n}"), file))[0]))


    def test_folder_structure(self):
        print(sys._getframe(  ).f_code.co_name)

        # This was also (accidentally) tested with M=5000!

        N = 10
        ns = [7, 16]
        r = 3.07
        k = 3
        s = 172
        o = test_folder
        M = 2

        self.assert_folder_structure(N=N, ns=ns, r=r, k=k, s=s, output_base_path=o, M=M)


    def assert_files_in_folder_equals(self, path, expected_value):
        """Asserts that the number of objects in `path` equals `expected_value`."""
        self.assertEqual(len(os.listdir(path)), expected_value)


    def test_count_files(self):
        print(sys._getframe(  ).f_code.co_name)

        N = 5
        ns = [10, 11]
        r = 3.2
        k = 3
        o = test_folder
        more = True
        times = 2
        M = 3

        print("Creating the files. Please stand by...")
        create_all.main(N=N, ns=ns, r=r, k=k, output_base_path=o, more=more, times=times, M=M)
        print("Finished creating the files. Checking conditions...")

        instances_folder_path, resolvents_folder_path, mod_folder_path = self.basic_folder_paths(o)

        for n in ns:
            # Count the objects in each subfolder of the instances folder
            # There should be N instances for each n in ns
            dir = os.path.join(instances_folder_path, f"n{n}")            
            self.assert_files_in_folder_equals(dir, N)

            # Count the objects in each subfolder of the resolvents folder
            # There should be N instances for each n in ns
            dir = os.path.join(resolvents_folder_path, f"n{n}")
            self.assert_files_in_folder_equals(dir, N)

            # Count the objects in each sub-subfolder of the modified instances folder
            dir = os.path.join(instances_folder_path, f"n{n}")
            for file in os.listdir(dir):
                # Calculate the name of the sub-subfolders in the modified instances folder
                # These are based on the names of the instances in the instance folder (without the ".cnf")
                dir2 = os.path.join(os.path.splitext(os.path.join(os.path.join(mod_folder_path, f"n{n}"), file))[0])
                self.assert_files_in_folder_equals(dir2, M)


    def test_reproducibility(self):
        print(sys._getframe(  ).f_code.co_name)

        N = 6
        ns = [11, 13]
        r = 3.02
        k = 3
        s = 1234
        o = test_folder
        M = 4

        # Create the files
        print("Creating the files. Please stand by...")
        create_all.main(N=N, ns=ns, r=r, k=k, s=s, output_base_path=o, M=M)

        # Copy the whole folder to a new location
        print("Copying the folder...")
        copytree(test_folder, test_folder_copy)

        # Cleaning the old folder
        # This ensures that the user is not queried (y/n) whether he/she wants to overwrite the old files;
        # the test just continues.
        rmtree(test_folder)

        # Create the files again
        print("Creating the files again. Please stand by...")
        create_all.main(N=N, ns=ns, r=r, k=k, output_base_path=o, M=M)

        # Compare the directories
        result = filecmp.dircmp(test_folder, test_folder_copy)
        self.assertTrue(result)    
        

    def test_correct_file_names(self):
        """In mod_instances, the beginning of the filenames should match the folder name.
        Furthermore, after this beginning, there should be a "mod".
        And all endings of the files (apart from the seeds) in one directory should be the same."""

        print(sys._getframe(  ).f_code.co_name)

        # Generate all files
        N = 4
        ns = [9, 13]
        r = 3.17
        k = 3
        s = 172
        o = test_folder
        M = 4
        
        create_all.main(N=N, ns=ns, r=r, k=k, s=s, output_base_path=o, M=M)

        # Get the paths of the instances and modifies instances folder
        instances_folder_path, _, mod_folder_path = self.basic_folder_paths(o)

        for n in ns:
            dir = os.path.join(instances_folder_path, f"n{n}")
            for instance in os.listdir(dir):
                dir2 = os.path.join(os.path.splitext(os.path.join(os.path.join(mod_folder_path, f"n{n}"), instance))[0])
                new_ending = ""
                count = 0
                # Iterate over all files in the sub-subdirectories of the modified instances folder
                for file2 in os.listdir(dir2):
                    # print(file2)
                    # e.g.:
                    # gen_n13_m41_k3SAT_seed1513000902_mod_s919069808_p0.0004617117117117117.cnf
                    beginning = "_".join(file2.split("_")[0:5]) # This yields e.g. gen_n13_m41_k3SAT_seed1513000902
                    self.assertEqual(beginning, instance.split(".")[0]) # The beginning of the files should match the folder name (which is based on the original instance name)

                    # Check for the "mod" in the middle
                    self.assertEqual(file2.split("_")[5], "mod")

                    # Check for the same endings, e.g. p0.0004617117117117117
                    old_ending = new_ending
                    new_ending = file2.split("_")[-1]                    

                    if count > 0: # It makes only sense to check if the second file's ending matches the first one's, etc...                   
                        self.assertEqual(old_ending, new_ending)

                    count += 1


    def get_all_clauses(self, filename):
        """Get all clauses that are written in `filename`. This will exclude the "c"-lines and "p"-line."""
        with open(filename, 'r') as file:
            lines = file.readlines()
        body = []
        for line in lines:
            if not (line.startswith("c") or line.startswith("p")):
                body.append(line)

        return body


    def test_correct_files_were_combined(self):
        """First, we check if all the original clauses of the instance can be found in the modified file.
        Secondly, we test, if all clauses in the modified file are from the original instance or resolvents."""

        print(sys._getframe(  ).f_code.co_name)

        # Generate all files
        N = 5
        ns = [12, 15]
        r = 3.03
        k = 3
        s = 1234
        o = test_folder
        M = 5

        create_all.main(N=N, ns=ns, r=r, k=k, s=s, output_base_path=o, M=M)

        # Get the paths of the instances and modifies instances folder
        instances_folder_path, resolvents_folder_path, mod_folder_path = self.basic_folder_paths(o)

        for n in ns:
            dir = os.path.join(instances_folder_path, f"n{n}")
            for instance in os.listdir(dir):
                dir2 = os.path.join(os.path.splitext(os.path.join(os.path.join(mod_folder_path, f"n{n}"), instance))[0])
                for mod_instance in os.listdir(dir2):
                    mod_clauses = self.get_all_clauses(os.path.join(dir2, mod_instance))
                    res_clauses = self.get_all_clauses( os.path.join(os.path.splitext(os.path.join(os.path.join(resolvents_folder_path, f"n{n}"), instance))[0]) + ".resolvents" )
                    original_clauses = self.get_all_clauses(os.path.join(dir, instance))

                    # Get rid of all possible "\n" in the clauses.
                    # Note: The clause validity of all files will be tested in `test_proper_clauses`. 
                    mod_clauses = set(map(lambda x: x.rstrip(), mod_clauses))
                    res_clauses = set(map(lambda x: x.rstrip(), res_clauses))
                    original_clauses = set(map(lambda x: x.rstrip(), original_clauses))

                    # First test: we check if all the original clauses of the instance can be found in the modified file.
                    for clause in original_clauses:                        
                        self.assertIn(clause, mod_clauses)

                    # Second test: we test, if all clauses in the modified file are from the original instance or resolvents.
                    for clause in mod_clauses:
                        self.assertIn(clause, original_clauses.union(res_clauses)) 


    def get_header(self, filename):
        """This method returns the header of a specified file as a list of strings.
        The header are all lines starting with 'c' (comment line) or 'p'
        until a line starts with neither."""

        lines = []
        with open(filename, 'r') as file:
            line = file.readline()
            while line and (line.startswith("c") or line.startswith("p")):
                lines.append(line)
                line = file.readline()
        return lines


    def is_int_max(self, x, m):
        """Checks whether x can be converted to int AND the absolute value of
        int(x) is at most m."""
        try:
            if abs(int(x)) <= m:
                return True
            else:
                return False
        except ValueError:
            return False          
                

    def assert_proper_clauses(self, file, check_p_line=True):
        """This method ensures that the clauses (apart from the last one) in the body are actually clauses in the right format.
        To be precise: Every clause needs to have the form: int int ... int 0
        where each int is at most n (the number of variables).
        Furthermore, tautologies are not allowed, i.e., x int ... int -x should not occur.
        Finally, double literals are also not admissible, i.e., x int ... int x.
        If check_p_line = False, checks regarding the maximum number of variables are omitted.
        This is useful for checking resolvent files, which do not contain a parameter line."""       

        # Get the parameter line (this is the last line of the header).
        parameter_line = self.get_header(file)[-1]

        # The parameter line has the form: p cnf n_variables m_clauses
        # We require n_variables
        if check_p_line:
            n_variables = int(parameter_line.split()[2])

        body = self.get_all_clauses(file)

        # We omit the last clause in our checks, because the original files' last clauses do not end with "\n".
        # This could be improved in future versions of these programs.
        for clause in body[ :-1]:
            # First, we check whether each clause ends with " 0\n"
            self.assertTrue(clause.endswith(" 0\n"))

            # We then omit the suffix " 0\n".
            literals = clause.split()[:-1]

            if check_p_line:
                for literal in literals:
                    # We assert whether each literal can be casted to an int with absolute value at most n_variables
                    self.assertTrue(self.is_int_max(literal, n_variables))

            # Finally, we convert the literals to a set, such that each literal is mapped to its absolute value.
            lit_set = set( [ abs((int(s))) for s in literals ] )
            # If the clause is either a tautology or double literals occur, then the length of the set
            # will not match the length of the literals list.
            # Otherwise, this test is passed.
            self.assertEqual(len(literals), len(lit_set))


    def test_proper_clauses(self):

        print(sys._getframe(  ).f_code.co_name)

        N = 8
        ns = [7, 10]
        r = 3.276
        k = 3
        s = 65
        o = test_folder
        M = 5

        create_all.main(N=N, ns=ns, r=r, k=k, s=s, output_base_path=o, M=M)

        instances_folder_path, resolvents_folder_path, mod_folder_path = self.basic_folder_paths(o)

        for n in ns:
            dir = os.path.join(instances_folder_path, f"n{n}")            
            for file in os.listdir(dir):
                self.assert_proper_clauses(os.path.join(dir, file))

            dir = os.path.join(resolvents_folder_path, f"n{n}")
            for file in os.listdir(dir):
                self.assert_proper_clauses(file=os.path.join(dir, file), check_p_line=False) # The resolvent files do not contain a parameter line.

            dir = os.path.join(instances_folder_path, f"n{n}")
            for file in os.listdir(dir):
                dir2 = os.path.join(os.path.splitext(os.path.join(os.path.join(mod_folder_path, f"n{n}"), file))[0])
                for file in os.listdir(dir2):
                    self.assert_proper_clauses(os.path.join(dir2, file))


        
        
if __name__ == 'main':
    unittest.main()