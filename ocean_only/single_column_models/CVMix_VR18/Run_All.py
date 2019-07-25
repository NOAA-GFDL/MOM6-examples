import sys
import sys, os
import shutil

EXEC = '/net/bgr/Models/MOM6/MOM6-examples_TRUNK/build/intel/ocean_only/repro/MOM6'

# Cases to Setup
# Options: 'CEW','CWB','DC','FC','FCE','FCML','HW','WNF'
cases_to_run = ['CEW','CWB','DC','FC','FCE','FCML','HW','WNF']
# Mixing to Setup
# Options: 'KPP', EPBL'
mixing_to_run = ['EPBL','KPP']

for ci in range(len(cases_to_run)):
    for ti in range(len(mixing_to_run)):
        PWD = os.getcwd()
        DIR = PWD+'/'+cases_to_run[ci]+'/'+mixing_to_run[ti]
        if (not os.path.exists(DIR)):
            print("Not locating the test case.  Are you sure this case/mixing exists?")
            sys.exit()
        else:
            print('-'*40+'\n'*10)
            print('Working on Case: '+cases_to_run[ci]+'/'+mixing_to_run[ti])
            print('\n'*10+'-'*40)
        os.chdir(DIR)
        try:
            if not os.path.exists('RESTART'):
                os.mkdir('RESTART')
            os.system(EXEC)
        except:
            "Execution Failed"
        os.chdir(PWD)
