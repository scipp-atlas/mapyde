from __future__ import annotations
import typing as T

def runner(config: dict):
    if not config['madgraph']['skip']:
        #./test/wrapper_mgpy.py config_file

    if not config['delphes']['skip']:
        #./test/wrapper_delphes.py config_file

    if not config['ana']['skip']:
        # recompute XS, override XS if needed,
        # add XS to config, re-dump config file
        # probably want to move this to wrapper_ana.py script

        #./test/wrapper_ana.py config_file

    if not config['pyhf']['skip']:
        #./test/wrapper_pyhf.py config_file
