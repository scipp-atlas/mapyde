from __future__ import annotations
import typing as T

def run_madgraph(config: dict):
    #./test/wrapper_mgpy.py config_file
    pass

def run_delphes(config: dict):
    #./test/wrapper_delphes.py config_file
    pass

def run_ana(config: dict):
    # recompute XS, override XS if needed,
    # add XS to config, re-dump config file
    # probably want to move this to wrapper_ana.py script
    
    #./test/wrapper_ana.py config_file
    pass

def run_pyhf(config: dict):
    #./test/wrapper_pyhf.py config_file
    pass

