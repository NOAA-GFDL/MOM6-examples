import sys
import sys, os
import shutil
import numpy as np

# CASES_TO_SETUP
# Options: 'HF-m500_WS-5', 'HF-m300_WS-5', 'HF-m200_WS-5', 'HF-m100_WS-5',
#          'HF-m50_WS-5',  'HF-m50_WS-8',  'HF-m50_WS-10', 'HF-m25_WS-5',
#          'HF-m25_WS-8',  'HF-m25_WS-10', 'HF-m10_WS-5',  'HF-m5_WS-5',
#          'HF-m5_WS-8',   'HF-m5_WS-10',  'HF-m5_WS-5_fL20',
#          'HF-25_WS-5',   'HF-50_WS-5'
CASES_TO_SETUP = ['HF-m500_WS-5', 'HF-m300_WS-5', 'HF-m200_WS-5', 'HF-m100_WS-5',
          'HF-m50_WS-5',  'HF-m50_WS-8',  'HF-m50_WS-10', 'HF-m25_WS-5',
          'HF-m25_WS-8',  'HF-m25_WS-10', 'HF-m10_WS-5',  'HF-m5_WS-5',
          'HF-m5_WS-8',   'HF-m5_WS-10',  'HF-m5_WS-5_fL20',
          'HF-25_WS-5',   'HF-50_WS-5']
# WAVES_TO_SETUP
# Options:  'no_waves', 'DHH85_waveage-0p6', 'DHH85_waveage-0p8', 'DHH85_waveage-1p0'
#           'DHH85_waveage-1p2'
WAVES_TO_SETUP = ['no_waves','DHH85_waveage-0p6', 'DHH85_waveage-0p8', 'DHH85_waveage-1p0',
                  'DHH85_waveage-1p2']
# TURB_TO_SETUP
# Options: 'ePBL','ePBL-LT','ePBL-LTbbl','ePBL-LT2','KPP_CVMix','KPP_CVMix-LTLF17'
TURB_TO_SETUP = ['ePBL-OM4','ePBL-RH18','ePBL-RL19','KPP_CVMix','KPP_CVMix-LTLF17']


GEN_NEW_OVERRIDES = True
CLEAN_EXPERIMENTS = True

for CASES in CASES_TO_SETUP:
    for WAVES in WAVES_TO_SETUP:
        for TURB in TURB_TO_SETUP:

            #Check for TURB common file
            if not os.path.exists('./common/MOM_mixing_'+TURB):
                print('Missing MOM_mixing_'+TURB)
                sys.exit()
            else:
                print('-'*40)
                print('Working on Case: '+CASES+'/'+WAVES+'/'+TURB)
                print('-'*40)

            PWD = os.getcwd()
            DIR = PWD+'/'+CASES+'/'+WAVES+'/'+TURB
            DIR_ovr = PWD+'/'+CASES+'/'+WAVES

            # First make the full directory
            if not os.path.exists(DIR):
                os.makedirs(DIR)


            # Check for override and if not exists, create
            if ( (not os.path.exists(DIR_ovr+'/MOM_override')) or
                 (GEN_NEW_OVERRIDES)):
                os.chdir(DIR_ovr)
                if os.path.exists('./MOM_override'):
                    os.remove('MOM_override')
                if GEN_NEW_OVERRIDES:
                    print('New overrides requirest, creating...')
                else:
                    print('No MOM_override found, creating...')
                F0=0.000103130958351
                # Check if not default value of 'f'
                if (CASES[-4:]=='fL20'):
                    F0 = 0.5 * F0
                    #Trim away FL20
                    CASEStmp=CASES[0:-5]
                    HFSTR = CASEStmp[CASEStmp.find('HF-')+3:CASEStmp.find('_WS')]
                    WNDSTR = CASEStmp[CASEStmp.find('WS-')+3:]
                else:
                    HFSTR = CASES[CASES.find('HF-')+3:CASES.find('_WS')]
                    WNDSTR = CASES[CASES.find('WS-')+3:]
                if HFSTR[0]=='m':
                    HF = -np.double(HFSTR[1:])
                else:
                    HF = np.double(HFSTR)
                if WNDSTR=='5':
                    MFLUXSTR='0.036'
                elif WNDSTR=='8':
                    MFLUXSTR='0.09216'
                elif WNDSTR=='10':
                    MFLUXSTR='0.144'

                FH = open('MOM_override',"w")
                FH.write('F_0 = '+'{:.8e}'.format(F0)+'\n')
                FH.write(r'WIND_CONFIG = "const"'+'\n')
                FH.write('CONST_WIND_TAUX = '+MFLUXSTR+'\n')
                FH.write('CONST_WIND_TAUY = 0.0'+'\n')
                FH.write(r'BUOY_CONFIG = "const"'+'\n')
                FH.write('SENSIBLE_HEAT_FLUX = '+str(HF)+'\n')
                if not(WAVES=='no_waves'):
                    waveage = WAVES[-3]+'.'+WAVES[-1]
                    print(waveage)
                    FH.write('USE_WAVES = True\n')
                    FH.write(r'WAVE_METHOD = "DHH85"'+'\n')
                    if waveage=='1.2':
                        FH.write('DHH85_AGE_FP = False\n')
                    else:
                        FH.write('DHH85_AGE_FP = True\n')
                    FH.write('DHH85_AGE = '+waveage+'\n')
                    FH.write('DHH85_WIND_SPEED = '+WNDSTR+'\n')
                    FH.write('DHH85_WIND_DIR = 0.\n')
                FH.close()
                os.chdir(PWD)

            #Link the override file
            if not os.path.exists(DIR+'/MOM_override'):
                print('no MOM_override linked, linking now ...')
                os.chdir(DIR)
                os.symlink('../MOM_override','MOM_override')
                os.chdir(PWD)

            #Link the mixing parameterization
            for FILE in ['MOM_mixing_'+TURB]:
                if not os.path.exists(DIR+'/MOM_mixing'):
                    print('no '+FILE+' found, linking to common')
                    os.chdir(DIR)
                    try:
                        os.symlink(PWD+'/common'+'/'+FILE,'MOM_mixing')
                    except:
                        print('No '+FILE+' to link to in common/'+TURB)
                    os.chdir(PWD)

            #Link the rest of the files sequentially:
            for FILE in ['MOM_input','diag_table','input.nml']:
                if not os.path.exists(DIR+'/'+FILE):
                    print('no '+FILE+' found, linking to common')
                    os.chdir(DIR)
                    try:
                        os.symlink(PWD+'/common'+'/'+FILE,FILE)
                    except:
                        print('No '+FILE+' to link to in common/'+TURB)
                    os.chdir(PWD)

            if CLEAN_EXPERIMENTS:
                for FILE in ['available_diags.000000','logfile.000000.out','MOM_parameter_doc.all','ocean.stats','surffluxes.nc',
                             'zgrid.nc','CPU_stats','MOM_IC.nc','MOM_parameter_doc.debugging','ocean.stats.nc','time_stamp.out',
                             'MOM_parameter_doc.layout','prog.nc','Vertical_coordinate.nc','exitcode','waves.nc',
                             'MOM_parameter_doc.short','prog_z.nc','visc.nc','ocean_geometry.nc','zgrid.cdl','RESTART/MOM.res.nc',
                             'RESTART/ocean_solo.res']:
                    if os.path.exists(DIR+'/'+FILE):
                        os.chdir(DIR)
                        os.remove(FILE)
                        os.chdir(PWD)
