#!/usr/bin/env python
# File created on 07 Jul 2012
from __future__ import division

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2011, The QIIME project"
__credits__ = ["Greg Caporaso"]
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Development"

from glob import glob
from shutil import rmtree
from os.path import exists, join
from cogent.util.unit_test import TestCase, main
from cogent.util.misc import create_dir, remove_files
from qiime.test import initiate_timeout, disable_timeout
from qiime.util import get_qiime_temp_dir, get_tmp_filename
from qiime.parse import parse_otu_map
from qp.functional_assignment import ParallelFunctionAssignerUsearch

class ParallelFunctionalAssignmentTests(TestCase):
    
    def setUp(self):
        """ """
        self.files_to_remove = []
        self.dirs_to_remove = []
        
        tmp_dir = get_qiime_temp_dir()
        self.test_out = get_tmp_filename(tmp_dir=tmp_dir,
                                         prefix='qiime_parallel_tests_',
                                         suffix='',
                                         result_constructor=str)
        self.dirs_to_remove.append(self.test_out)
        create_dir(self.test_out)
        
        self.refseqs1_fp = get_tmp_filename(tmp_dir=self.test_out,
                                            prefix='qiime_refseqs',
                                            suffix='.fasta')
        refseqs1_f = open(self.refseqs1_fp,'w')
        refseqs1_f.write(refseqs1)
        refseqs1_f.close()
        self.files_to_remove.append(self.refseqs1_fp)
        
        self.inseqs1_fp = get_tmp_filename(tmp_dir=self.test_out,
                                            prefix='qiime_inseqs',
                                            suffix='.fasta')
        inseqs1_f = open(self.inseqs1_fp,'w')
        inseqs1_f.write(inseqs1)
        inseqs1_f.close()
        self.files_to_remove.append(self.inseqs1_fp)
        
        initiate_timeout(60)

    
    def tearDown(self):
        """ """
        disable_timeout()
        remove_files(self.files_to_remove)
        # remove directories last, so we don't get errors
        # trying to remove files which may be in the directories
        for d in self.dirs_to_remove:
            if exists(d):
                rmtree(d)

class ParalleFunctionalAssignmentUsearchTests(ParallelFunctionalAssignmentTests):

    def test_parallel_function_assigner_usearch(self):
        """ parallel_function_assigner_usearch functions as expected """
        
        params = {'refseqs_fp':self.refseqs1_fp,
          'min_percent_id':0.97,
          'evalue':1e-10,
          'max_accepts':1,
          'max_rejects':32,
          'queryalnfract':0.35,
          'targetalnfract':0.0
        }
        
        app = ParallelFunctionAssignerUsearch()
        r = app(self.inseqs1_fp,
                self.test_out,
                params,
                job_prefix='PTEST',
                poll_directly=True,
                suppress_submit_jobs=False)
        otu_map_fp = glob(join(self.test_out,'*fmap.txt'))[0]
        fmap = parse_otu_map(open(otu_map_fp,'U'))
        self.assertEqual(len(fmap[0]),2)
        self.assertEqualItems(fmap[1],['eco:b0015', 'eco:b0122'])
        self.assertEqualItems(fmap[2],['eco:b0015-pr', 'eco:b0122-pr'])

refseqs1 = """>eco:b0001-pr
MKRISTTITTTITITTGNGAG
>eco:b0015-pr dnaJ
MAKQDYYEILGVSKTAEEREIRKAYKRLAMKYHPDRNQGDKEAEAKFKEIKEAYEVLTDS
QKRAAYDQYGHAAFEQGGMGGGGFGGGADFSDIFGDVFGDIFGGGRGRQRAARGADLRYN
MELTLEEAVRGVTKEIRIPTLEECDVCHGSGAKPGTQPQTCPTCHGSGQVQMRQGFFAVQ
QTCPHCQGRGTLIKDPCNKCHGHGRVERSKTLSVKIPAGVDTGDRIRLAGEGEAGEHGAP
AGDLYVQVQVKQHPIFEREGNNLYCEVPINFAMAALGGEIEVPTLDGRVKLKVPGETQTG
KLFRMRGKGVKSVRGGAQGDLLCRVVVETPVGLNERQKQLLQELQESFGGPTGEHNSPRS
KSFFDGVKKFFDDLTR
>eco:b0122-pr
MKTFFRTVLFGSLMAVCANSYALSESEAEDMADLTAVFVFLKNDCGYQNLPNGQIRRALV
FFAQQNQWDLSNYDTFDMKALGEDSYRDLSGIGIPVAKKCKALARDSLSLLAYVK
"""

inseqs1 = """>eco:b0001 thrL; thr operon leader peptide; K08278 thr operon leader peptide (N)
atgaaacgcattagcaccaccattaccaccaccatcaccattaccacaggtaacggtgcg
ggctga
>eco:b0015 dnaJ; chaperone Hsp40, co-chaperone with DnaK; K03686 molecular chaperone DnaJ (N)
atggctaagcaagattattacgagattttaggcgtttccaaaacagcggaagagcgtgaa
atcagaaaggcctacaaacgcctggccatgaaataccacccggaccgtaaccagggtgac
aaagaggccgaggcgaaatttaaagagatcaaggaagcttatgaagttctgaccgactcg
caaaaacgtgcggcatacgatcagtatggtcatgctgcgtttgagcaaggtggcatgggc
ggcggcggttttggcggcggcgcagacttcagcgatatttttggtgacgttttcggcgat
atttttggcggcggacgtggtcgtcaacgtgcggcgcgcggtgctgatttacgctataac
atggagctcaccctcgaagaagctgtacgtggcgtgaccaaagagatccgcattccgact
ctggaagagtgtgacgtttgccacggtagcggtgcaaaaccaggtacacagccgcagact
tgtccgacctgtcatggttctggtcaggtgcagatgcgccagggattcttcgctgtacag
cagacctgtccacactgtcagggccgcggtacgctgatcaaagatccgtgcaacaaatgt
catggtcatggtcgtgttgagcgcagcaaaacgctgtccgttaaaatcccggcaggggtg
gacactggagaccgcatccgtcttgcgggcgaaggtgaagcgggcgagcatggcgcaccg
gcaggcgatctgtacgttcaggttcaggttaaacagcacccgattttcgagcgtgaaggc
aacaacctgtattgcgaagtcccgatcaacttcgctatggcggcgctgggtggcgaaatc
gaagtaccgacccttgatggtcgcgtcaaactgaaagtgcctggcgaaacccagaccggt
aagctattccgtatgcgcggtaaaggcgtcaagtctgtccgcggtggcgcacagggtgat
ttgctgtgccgcgttgtcgtcgaaacaccggtaggcctgaacgaaaggcagaaacagctg
ctgcaagagctgcaagaaagcttcggtggcccaaccggcgagcacaacagcccgcgctca
aagagcttctttgatggtgtgaagaagttttttgacgacctgacccgctaa
>eco:b0122
atgaagacgtttttcagaacagtgttattcggcagcctgatggccgtctgcgcaaacagt
tacgcgctcagcgagtctgaagccgaagatatggccgatttaacggcagtttttgtcttt
ctgaagaacgattgtggttaccagaacttacctaacgggcaaattcgtcgcgcactggtc
tttttcgctcagcaaaaccagtgggacctcagtaattacgacaccttcgacatgaaagcc
ctcggtgaagacagctaccgcgatctcagcggcattggcattcccgtcgctaaaaaatgc
aaagccctggcccgcgattccttaagcctgcttgcctacgtcaaataa
"""

if __name__ == "__main__":
    main()