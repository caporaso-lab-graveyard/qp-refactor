#!/usr/bin/env python
# File created on 13 Jul 2012
from __future__ import division

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2011, The QIIME project"
__credits__ = ["Greg Caporaso"]
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Development"

from cogent.util.unit_test import TestCase, main
from qp.util import ParallelWrapper


class ParallelWrapperTests(TestCase):

    def setUp(self):
        """ """
        # instantiating the abstract class to test some of the more 
        # stand-alone methods
        self.pw = ParallelWrapper()

    def test_merge_to_n_commands_even(self):
        """ _merge_to_n_commands functions as expected (even number of cmds)"""
        commands = ['pick_otus.py -h ; mv somthing.txt something_else.txt',
                    'pick_otus.py -g',
                    'pick_otus.py -f',
                    'pick_otus.py -w']
                    
        expected = ['/bin/bash ; pick_otus.py -h ; mv somthing.txt something_else.txt ; pick_otus.py -g ; pick_otus.py -f ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,1)
        self.assertEqual(actual,expected)
        
        expected = [
         '/bin/bash ; pick_otus.py -h ; mv somthing.txt something_else.txt ; pick_otus.py -g ; exit',
         '/bin/bash ; pick_otus.py -f ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,2)
        self.assertEqual(actual,expected)
        
        # rounds to 2 jobs to start
        expected = [
         '/bin/bash ; pick_otus.py -h ; mv somthing.txt something_else.txt ; pick_otus.py -g ; exit',
         '/bin/bash ; pick_otus.py -f ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,3)
        self.assertEqual(actual,expected)
        
        expected = ['/bin/bash ; pick_otus.py -h ; mv somthing.txt something_else.txt ; exit',
                    '/bin/bash ; pick_otus.py -g ; exit',
                    '/bin/bash ; pick_otus.py -f ; exit',
                    '/bin/bash ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,4)
        self.assertEqual(actual,expected)
        
        self.assertRaises(ValueError,self.pw._merge_to_n_commands,commands,0)
        self.assertRaises(ValueError,self.pw._merge_to_n_commands,commands,-42)
        
        # jobs to start is much higer than actual jobs
        expected = ['/bin/bash ; pick_otus.py -h ; mv somthing.txt something_else.txt ; exit',
                    '/bin/bash ; pick_otus.py -g ; exit',
                    '/bin/bash ; pick_otus.py -f ; exit',
                    '/bin/bash ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,100)
        self.assertEqual(actual,expected)
        
        self.assertRaises(ValueError,self.pw._merge_to_n_commands,commands,0)
        self.assertRaises(ValueError,self.pw._merge_to_n_commands,commands,-42)
        
        
    def test_merge_to_n_commands_odd(self):
        """ _merge_to_n_commands functions as expected (odd number of cmds)"""
        commands = ['pick_otus.py -h',
                    'pick_otus.py -g',
                    'pick_otus.py -w']
                    
        expected = ['/bin/bash ; pick_otus.py -h ; pick_otus.py -g ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,1)
        self.assertEqual(actual,expected)
                    
        # rounds to 1 job to start
        expected = ['/bin/bash ; pick_otus.py -h ; pick_otus.py -g ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,2)
        self.assertEqual(actual,expected)
                    
        expected = ['/bin/bash ; pick_otus.py -h ; exit',
                    '/bin/bash ; pick_otus.py -g ; exit',
                    '/bin/bash ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,3)
        self.assertEqual(actual,expected)
        
        expected = ['/bin/bash ; pick_otus.py -h ; exit',
                    '/bin/bash ; pick_otus.py -g ; exit',
                    '/bin/bash ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,4)
        self.assertEqual(actual,expected)
        
        expected = ['/bin/bash ; pick_otus.py -h ; exit',
                    '/bin/bash ; pick_otus.py -g ; exit',
                    '/bin/bash ; pick_otus.py -w ; exit']
        actual = self.pw._merge_to_n_commands(commands,100)
        self.assertEqual(actual,expected)
        
        self.assertRaises(ValueError,self.pw._merge_to_n_commands,commands,0)
        self.assertRaises(ValueError,self.pw._merge_to_n_commands,commands,-42)    
        
    def test_merge_to_n_commands_alt_params(self):
        """ _merge_to_n_commands functions with alt params"""
        commands = ['pick_otus.py -h',
                    'pick_otus.py -g',
                    'pick_otus.py -w']
                    
        expected = ['pick_otus.py -h ; pick_otus.py -g ; pick_otus.py -w']
        actual = self.pw._merge_to_n_commands(commands,2,command_prefix='',command_suffix='')
        self.assertEqual(actual,expected)
                    
        expected = ['pick_otus.py -h ! pick_otus.py -g ! pick_otus.py -w']
        actual = self.pw._merge_to_n_commands(commands,2,command_prefix='',
         command_suffix='',delimiter=' ! ')
        self.assertEqual(actual,expected)
        
        commands = map(str,range(10))
        actual = self.pw._merge_to_n_commands(commands,5,command_prefix='',
         command_suffix='',delimiter=',')
        expected = ['0,1','2,3','4,5','6,7','8,9']
        self.assertEqual(actual,expected)

    def test_merge_to_n_commands_w_prefix(self):
        """ _merge_to_n_commands functions as expected (w prefix/suffix)"""
        commands = ['/bin/bash ; pick_otus.py -h ; exit',
                    '/bin/bash;pick_otus.py -g;exit',
                    '/bin/bash ; pick_otus.py -h ; exit ; /bin/bash ; pick_otus.py -w ; exit']
        expected = ['/bin/bash ; pick_otus.py -h ; pick_otus.py -g ; pick_otus.py -h ; pick_otus.py -w ; exit']
        
        actual = self.pw._merge_to_n_commands(commands,2,command_prefix='/bin/bash ;',command_suffix='; exit')
        self.assertEqual(actual,expected)
        actual = self.pw._merge_to_n_commands(commands,2)
        self.assertEqual(actual,expected)

if __name__ == "__main__":
    main()