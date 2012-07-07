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

from qp.pick_otus_uclust_ref import PickOtusUclustRef

class FunctionAssignerUsearch(PickOtusUclustRef):
    _script_name = 'functional_assignment.py'
    _job_prefix = 'FUAS'
    
    def _get_job_commands(self,
                          fasta_fps,
                          output_dir,
                          params,
                          job_prefix,
                          working_dir,
                          command_prefix='/bin/bash; ',
                          command_suffix='; exit'):
        # Create basenames for each of the output files. These will be filled
        # in to create the full list of files created by all of the runs.
        out_filenames = [job_prefix + '.%d_otus.log', 
                         job_prefix + '.%d_otus.txt',
                         job_prefix + '.%s_failures.txt']
    
        # Create lists to store the results
        commands = []
        result_filepaths = []
        
        # Iterate over the input files
        for i,fasta_fp in enumerate(fasta_fps):
            # Each run ends with moving the output file from the tmp dir to
            # the output_dir. Build the command to perform the move here.
            rename_command, current_result_filepaths = self._get_rename_command(
                [fn % i for fn in out_filenames],
                working_dir,
                output_dir)
            result_filepaths += current_result_filepaths
            
            command = \
             '%s %s -i %s -r %s -m usearch -o %s --min_percent_id %s --max_accepts %d --max_rejects %d --queryalnfract %f --targetalnfract %f --min_aligned_percent %f --evalue %f %s %s' %\
             (command_prefix,
              self._script_name,
              fasta_fp,
              params['refseqs_fp'],
              working_dir,
              params['min_percent_id'],
              params['max_accepts'],
              params['max_rejects'],
              params['queryalnfract'],
              params['targetalnfract'],
              params['min_aligned_percent'],
              params['evalue'],
              rename_command,
              command_suffix)

            commands.append(command)

        return commands, result_filepaths
