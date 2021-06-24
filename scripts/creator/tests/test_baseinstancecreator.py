# -*- coding: utf-8 -*-

import unittest
import os, glob
import filecmp
from filecmp import dircmp
from shutil import rmtree, copy2
from distutils.dir_util import copy_tree
import math
#import sys
#sys.path.insert(0,'..')
import sys

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

import base_instance_creator as c
import generator as g


# Specify the folderpaths used during testing
tmpfolder = "./tmp_creatortest"
tmpcopyfolder = "./tmp_copy_creatortest"



class TestBaseInstanceCreator(unittest.TestCase):

    def setUp(self):
        # SetUp will be called before every test.
        # Makes sure, that the folders ./tmp_creatortest and ./tmp_copy_creatortest exists. 
        os.makedirs(tmpfolder, exist_ok=True)   
        os.makedirs(tmpcopyfolder, exist_ok=True) 

        
    def tearDown(self):
        # Will be run after every test.
        # Makes sure that the temporary directories are deleted.
        # Makes sure that all cnf-files are deleted.
        rmtree(tmpfolder)
        rmtree(tmpcopyfolder)
        for f in glob.glob("./gen_*.cnf"):
            os.remove(f)
        

    def test_okay(self):
        # Test if the test framework works properly.
        self.assertTrue(True)
        print("Test Framework okay.")
        #print(os.getcwd())

###############################################################################################

    def get_header(self, filename, n_lines):
        # Diese Methode liest die ersten n_lines Zeilen einer Datei ausgeführt
        # und liefert sie als Liste zurück.
        lines = []
        with open(filename, 'r') as file:
            for _ in range(n_lines):
                lines.append(file.readline())
        return lines

###############################################################################################
###############################################################################################

#python3 -m unittest tests.test_baseinstancecreator.TestBaseInstanceCreator.test_NAME

    def test_ns_parameter(self):
        print(sys._getframe(  ).f_code.co_name)
        # Check if non-list ns get rejected
        ns = 3
        r = 3.2
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r)


        ns = "clearlynotalist"
        r = 3.1
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r)


        # Check if non-int lists as ns get rejected 
        ns = [3, 5, 8.0]
        r = 7.2
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r)


        # Check if non-positive entries in the list get rejected
        ns = [7, 8, 0]
        r = 4.0
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r)


        ns = [7, 8, -1]
        r = 78.326787
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r)



    def test_r_parameter(self):
        print(sys._getframe(  ).f_code.co_name)
        # Check if non-floats as r get rejected
        ns = [5, 8, 700]
        r = "f"
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r)

        ns = [8, 900, 2]
        r = 3
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r)


    def test_N_k_s_parameters(self):
        print(sys._getframe(  ).f_code.co_name)
        # Check if non-ints for N, k, s are rejected
        ns = [5, 8, 700]
        r = 89.43

        N = "f"
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, N=N)

        N = 3.1
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, N=N)

        k = "s"
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, k=k)

        k = 3.1
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, k=k)

        s = "string"
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, s=s)

        s= 5.4
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, s=s)

        # Check if non-positive k and N get rejected
        k = 0
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, k=k)

        k = -1
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, k=k)

        k = -2.5
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, k=k)

        N = 0
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, N=N)

        N = -1
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, N=N)

        N = -5.6
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, N=N)


    def test_o_parameter(self):
        print(sys._getframe(  ).f_code.co_name)
        # Test if non-strings as o get rejected
        ns = [1000, 5, 98]
        r = 7.4
        o = 34.2
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, o=o)


    def test_ps_q_value_switch(self):
        print(sys._getframe(  ).f_code.co_name)
        # Test if a Value Error is raised if both a p-value list and a q parameter are given.
        # print("Started: test_p_q_value_switch")        
        ns = [3, 4, 5]
        r = 7.898
        ps = [1.0, 1.0, 1.0]
        q = 0.4
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, ps=ps, q=q)


    def test_ps_parameter(self):
        print(sys._getframe(  ).f_code.co_name)
        # Test if ps gets rejected if it contains non-float values
        ns = [1, 2, 3]
        r = 7.1
        ps = [1, 2]
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, ps=ps)

        ps = ["f", 6]
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, ps=ps)

        # Test if non-iterables as ps get rejected
        ps = 7
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, ps=ps)

        ps = "sg"
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, ps=ps)

        # Test if ps gets rejected if it contains entries <0
        ps = [1.0, 0.5, -0.1]
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, ps=ps)

        # Test if ps gets rejected if it contains entries >1
        ps = [1.0, 1.1]
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, ps=ps)

        # Test if we check for: len(ps) matches k
        ns = [1, 2, 3]
        r = 7.2
        k = 6
        ps = [1.0]*5
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, k=k, ps=ps)

        ps = [1.0]*4
        with self.assertRaises(ValueError):
            c.create_instances(ns=ns, r=r, k=k, ps=ps)


    def test_q_parameter(self):
        print(sys._getframe(  ).f_code.co_name)
        # Check if non-float q gets rejected
        ns = [1, 2, 3]
        r = 76.977
        q = "f"
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, q=q)

        q = 1
        with self.assertRaises(TypeError):
            c.create_instances(ns=ns, r=r, q=q)


    def test_correct_m_calculated(self):
        print(sys._getframe(  ).f_code.co_name)
        ns = [28, 30]
        r = 13.2
        o = tmpfolder

        c.create_instances(ns=ns, r=r, o=o)

        for n in ns:
            correct_m = str(round(n*r))
            path = os.path.join(o, f"n{n}")
            files = [file_ for file_ in os.listdir(path) if os.path.isfile(os.path.join(path,file_)) and file_ != ".DS_Store"]
            for file_ in files:
                pos = file_.find('_m') # Get the index of "-m" in the file name
                self.assertNotEqual(pos, -1) # .find returns the lowest index of the substring if it is found in given string. If it’s not found then it returns -1.
                m_in_filename = file_[pos:pos+len(correct_m)+2]
                self.assertEqual(m_in_filename, "_m"+correct_m)            


    def test_different_seeds(self):
        print(sys._getframe(  ).f_code.co_name)
        print("This test might take a minute...")
        ns = [100, 200, 300]
        r = 5.2
        N = 100
        s = 420
        o = tmpfolder

        c.create_instances(ns=ns, r=r, N=N, s=s, o=o)
      
        # Are the seeds different?
        for n in ns:
            path = os.path.join(o, f"n{n}")
            files = [file_ for file_ in os.listdir(path) if os.path.isfile(os.path.join(path,file_)) and file_ != ".DS_Store"]
            seeds = []
            for file_ in files:
                pos1 = file_.find('_seed')
                pos2 = file_.find('.cnf')
                seeds.append(file_[pos1+5:pos2])
                self.assertEqual(len(seeds), len(set(seeds)))

        # Could be that the file is just overwritten when a duplicate seed is used.
        # Thus we count the files in the folder as well.
        number_of_files_in_dirs = []
        for n in ns:
            path = os.path.join(o, f"n{n}")
            number_of_files_in_dirs.append(len([file_ for file_ in os.listdir(path) if os.path.isfile(os.path.join(path,file_)) and file_ != ".DS_Store"]))

        self.assertEqual(number_of_files_in_dirs, [N]*len(ns))


    def test_number_of_instances_N(self):
        # This test will check if there are N files in each n-Folder
       
        print("Started: test_number_of_instances_N") 

        ns = [100, 200] 
        r = 4.5
        N = 13
        k = 4
        s = 42524
        o = tmpfolder        
        ps = [0.76, 0.8, 0.33, 1.0]

        c.create_instances(ns=ns, r=r, N=N, k=k, s=s, o=o, ps=ps)

        number_of_files_in_dirs = []

        for n in ns:
            path = os.path.join(o, f"n{n}")
            number_of_files_in_dirs.append(len([file_ for file_ in os.listdir(path) if os.path.isfile(os.path.join(path,file_)) and file_ != ".DS_Store"]))

        self.assertEqual(number_of_files_in_dirs, [N]*len(ns))


    def test_for_not_wanted_files(self):
        print(sys._getframe(  ).f_code.co_name)
        ns = [100, 200] 
        r = 4.5
        N = 13
        k = 4
        s = 42524
        o = tmpfolder        
        ps = [0.76, 0.8, 0.33, 1.0]

        c.create_instances(ns=ns, r=r, N=N, k=k, s=s, o=o, ps=ps)

        for root, dirs, files in os.walk(tmpfolder):
            for name in files:
                if name.endswith((".cnf")):
                    pass
                else:
                    if name != ".DS_Store":
                        assert False, "There are non-cnf-files in the folder that shouldn't be there."


    def test_same_file_by_manual_call(self):
        print(sys._getframe(  ).f_code.co_name)
        # Check if we get the same file by calling the command that is written in the header
        ns = [100] 
        r = 4.5
        N = 13
        k = 4
        s = 42524
        o = tmpfolder        
        ps = [0.76, 0.8, 0.33, 1.0]

        c.create_instances(ns=ns, r=r, N=N, k=k, s=s, o=o, ps=ps)

        path = os.path.join(o, f"n{100}")
        files = [file_ for file_ in os.listdir(path) if os.path.isfile(os.path.join(path,file_)) and file_ != ".DS_Store"]

        os.makedirs(f"{tmpcopyfolder}/n100", exist_ok=True)  
        copy_path = os.path.join(tmpcopyfolder, f"n{100}")

        for file_ in files:
            copy2(os.path.join(path,file_), os.path.join(copy_path,file_))

        for f in files:
            #   "c Created by python3 generator.py -n int -m int -k int -p int ... int -s int -o ./tmp_test"
            file_ = os.path.join(copy_path,f)

            call_line = self.get_header(file_, 6)[1]

            n_pos = call_line.find("-n")
            m_pos = call_line.find("-m")
            k_pos = call_line.find("-k")
            p_pos = call_line.find("-p")
            s_pos = call_line.find("-s")
            o_pos = call_line.find("-o")

            # Extract the values from the call line
            n_ex = call_line[n_pos+3 : m_pos]
            m_ex = call_line[m_pos+3 : k_pos]
            k_ex = call_line[k_pos+3 : p_pos]
            p_ex = call_line[p_pos+3 : s_pos]
            s_ex = call_line[s_pos+3 : o_pos]
            o_ex = call_line[o_pos+3 : ] # won't use, but hey...

            p_list = [float(p) for p in p_ex.split(" ")[:-1]]
            
            g.main(n = int(n_ex), m = int(m_ex), k = int(k_ex), p = p_list, s = int(s_ex), o = tmpfolder)

            self.assertTrue(filecmp.cmp(file_, os.path.join(path,f)))

    def test_reproducibility_all_files(self):
        print(sys._getframe(  ).f_code.co_name)
        # Check if calls with identical parameters generate identical files.

        # Create the files.
        ns = [50, 100, 200]
        r = 3.7
        N = 7
        k = 3
        s = 425624
        o = tmpfolder        
        ps = [0.74, 0.65, 0.33234234]

        c.create_instances(ns=ns, r=r, N=N, k=k, s=s, o=o, ps=ps)

        # First, copy all the files and folders inside tmpfolder to a new folder.
        copy_tree(tmpfolder, tmpcopyfolder)

        # Remove the whole folder with the originals
        rmtree(tmpfolder)

        # Generate the files again, with the same parameters as before
        c.create_instances(ns=ns, r=r, N=N, k=k, s=s, o=o, ps=ps)

        # Iterate through all subfolders, and all files in these folders and compare.
        for n in ns:

            path = os.path.join(o, f"n{n}")
            files = [file_ for file_ in os.listdir(path) if os.path.isfile(os.path.join(path,file_)) and file_ != ".DS_Store"]

            for file_ in files:
                orgpath = os.path.join(o, f"n{n}")
                copypath = os.path.join(tmpcopyfolder, f"n{n}")
                orgfile = os.path.join(orgpath, file_)
                copyfile = os.path.join(copypath, file_)
                # filecmf.cmp(_,_) überprüft ob zwei Dateien identisch sind.
                # Allerdings werden nur die Statistiken (Hash-Werte etc.) verglichen.
                # Für einen Byte-für-Byte Vergleich muss shallow=False gesetzt werden.
                self.assertTrue(filecmp.cmp(orgfile, copyfile))   


    def test_q_given_correct_ps_calculated(self):
        print(sys._getframe(  ).f_code.co_name)
        # Test if, given a q, the ps list gets calculated correctly.
        # For this we will have a direct look into the files
        ns = [28, 30]
        r = 3.2
        q = 1.0
        k = 3
        o = tmpfolder

        c.create_instances(ns=ns, r=r, k=3, o=o, q=q)

        # Calculate the correct ps that should be used
        denominator = ((1+q) ** k) - 1
        ps = []
        for i in range(1, k+1):
            ps.append((q**i)/denominator)

        for n in ns:
            path = os.path.join(o, f"n{n}")        
            files = [file_ for file_ in os.listdir(path) if os.path.isfile(os.path.join(path,file_)) and file_ != ".DS_Store"]
            for file_ in files:
                filepath = os.path.join(path,file_)
                call_line = self.get_header(filepath, 6)[1]

                p_pos = call_line.find("-p")
                s_pos = call_line.find("-s")

                # Extract the values from the call line
                p_ex = call_line[p_pos+3 : s_pos]

                p_list = [float(p) for p in p_ex.split(" ")[:-1]]

                self.assertEqual(ps, p_list)


    def test_golden_ratio(self):
        print(sys._getframe(  ).f_code.co_name)
        # Test if q-hidden instances with q = \Phi = (\sqrt{5}-1)/2 are generated, if q = None and ps = None.

        ns = [28, 300]
        r = 3.2
        o = tmpfolder

        c.create_instances(ns=ns, r=r, o=o)

        # Generate the files with correct ps
        q = (math.sqrt(5)-1)/2.0
        c.create_instances(ns=ns, r=r, o=tmpcopyfolder, q=q)

        for n in ns:

            path = os.path.join(o, f"n{n}")
            copypath = os.path.join(tmpcopyfolder, f"n{n}")
            files = [file_ for file_ in os.listdir(path) if os.path.isfile(os.path.join(path,file_)) and file_ != ".DS_Store"]

            for file_ in files:                
                orgfile = os.path.join(path, file_)
                copyfile = os.path.join(copypath, file_)
                
                call_line_org = self.get_header(orgfile, 6)[1]
                call_line_copy = self.get_header(copyfile, 6)[1]

                p_pos_org = call_line_org.find("-p")
                s_pos_org = call_line_org.find("-s")

                p_pos_copy = call_line_copy.find("-p")
                s_pos_copy = call_line_copy.find("-s")

                # Extract the values from the call line
                p_ex_org = call_line_org[p_pos_org+3 : s_pos_org]
                p_ex_copy = call_line_copy[p_pos_copy+3 : s_pos_copy]                

                self.assertEqual(p_ex_org, p_ex_copy) 


        

###############################################################################################
###############################################################################################

        
if sys._getframe(  ).f_code.co_name == '__main__':
    unittest.main()