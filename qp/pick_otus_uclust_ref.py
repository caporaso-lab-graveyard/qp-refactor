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

from qp.util import ParallelWrapper

class PickOtusUclustRef(ParallelWrapper):
    _script_name = "pick_otus.py"
    _job_prefix = 'POTU'
    _input_splitter = ParallelWrapper._split_fasta
    _process_run_results_f =\
         'qiime.parallel.pick_otus_uclust_ref.parallel_uclust_ref_process_run_results_f'
    
    def _identify_files_to_remove(self,job_result_filepaths,params):
        """ Select the files to remove: by default remove all files
        """
        if params['save_uc_files']:
            # keep any .uc files that get created
            result =\
             [fp for fp in job_result_filepaths if not fp.endswith('.uc')]
        else:
            result = [job_result_filepaths]
        
        return result
    
    def _get_job_commands(self,
                          fasta_fps,
                          output_dir,
                          params,
                          job_prefix,
                          working_dir,
                          command_prefix='/bin/bash; ',
                          command_suffix='; exit'):
        """Generate pick_otus commands which should be run
        """
        # Create basenames for each of the output files. These will be filled
        # in to create the full list of files created by all of the runs.
        out_filenames = [job_prefix + '.%d_otus.log', 
                         job_prefix + '.%d_otus.txt',
                         job_prefix + '.%s_failures.txt']
    
        # Create lists to store the results
        commands = []
        result_filepaths = []
    
        if params['enable_rev_strand_match']:
            enable_rev_strand_match_str = '-z'
        else:
            enable_rev_strand_match_str = ''
            
        if params['optimal_uclust']:
            optimal_uclust_str = '-A'
        else:
            optimal_uclust_str = ''
            
        if params['exact_uclust']:
            exact_uclust_str = '-E'
        else:
            exact_uclust_str = ''
            
        if params['stable_sort']:
            stable_sort_str = ''
        else:
            stable_sort_str = '--suppress_uclust_stable_sort'
            
        if params['save_uc_files']:
            save_uc_files_str = ''
            out_filenames += [job_prefix + '%d_clusters.uc']
        else:
            save_uc_files_str = '-d'
        
    
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
             '%s %s -i %s -r %s -m uclust_ref --suppress_new_clusters -o %s -s %s %s %s %s --max_accepts %s --max_rejects %s --stepwords %d --w %d %s %s %s %s' %\
             (command_prefix,
              self._script_name,\
              fasta_fp,\
              params['refseqs_fp'],\
              working_dir,\
              params['similarity'],\
              enable_rev_strand_match_str,
              optimal_uclust_str,
              exact_uclust_str,
              params['max_accepts'],
              params['max_rejects'],
              params['stepwords'],
              params['word_length'],
              stable_sort_str,
              save_uc_files_str,
              rename_command,
              command_suffix)

          
            commands.append(command)

        return commands, result_filepaths

    def _get_poller_command(self,
                               expected_files_filepath,
                               merge_map_filepath,
                               deletion_list_filepath,
                               command_prefix='/bin/bash; ',
                               command_suffix='; exit'):
        """Generate command to initiate a poller to monitior/process completed runs
        """

        result = '%s poller.py -f %s -p %s -m %s -d %s -t %d %s' % \
         (command_prefix,
          expected_files_filepath,
          self._process_run_results_f,
          merge_map_filepath,
          deletion_list_filepath,
          self._seconds_to_sleep,
          command_suffix)
  
        return result, []

    def _write_merge_map_file(self,
                              input_file_basename,
                              job_result_filepaths,
                              output_dir,
                              merge_map_filepath,
                              failures=False):
        """ 
        """
        f = open(merge_map_filepath,'w')
    
        otus_fps = []
        log_fps = []
        failures_fps = []
    
        if not failures:
            out_filepaths = [
             '%s/%s_otus.txt' % (output_dir,input_file_basename),
             '%s/%s_otus.log' % (output_dir,input_file_basename)]
            in_filepaths = [otus_fps,log_fps]
        else:
            out_filepaths = [
             '%s/%s_otus.txt' % (output_dir,input_file_basename),
             '%s/%s_otus.log' % (output_dir,input_file_basename),
             '%s/%s_failures.txt' % (output_dir,input_file_basename)]
            in_filepaths = [otus_fps,log_fps,failures_fps]
    
        for fp in job_result_filepaths:
            if fp.endswith('_otus.txt'):
                otus_fps.append(fp)
            elif fp.endswith('_otus.log'):
                log_fps.append(fp)
            elif fp.endswith('_failures.txt'):
                failures_fps.append(fp)
            else:
                pass
    
        for in_files, out_file in\
         zip(in_filepaths,out_filepaths):
            f.write('\t'.join(in_files + [out_file]))
            f.write('\n')
        f.close()

