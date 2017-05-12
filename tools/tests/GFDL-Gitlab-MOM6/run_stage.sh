#!/bin/bash -f

# This script creates a job script that is launched once and in turns creates tar files
# of the model output after various runs.
# This script *assumes* that MOM6-examples is complete (has all relevent stats files) when
# this script is invoked.

echo -n "Run stage started at " && date

# Make a job script
cat > job.sh << 'EOF'
# Run non-symmetric executables
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run clean_gnu clean_intel clean_pgi -s
echo -n "Non-symmetric runs started at " && date
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run gnu_all -s -j
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run intel_all -s -j
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run pgi_all -s -j
echo -n "Non-symmetric runs finished at " && date
tar cf non_symmetric.tar `find MOM6-examples -name ocean.stats.gnu -o -name ocean.stats.intel -o -name ocean.stats.pgi`

# Run symmetric executables
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run clean_gnu clean_intel clean_pgi -s
echo -n "Symmetric runs started at " && date
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run gnu_all MEMORY=dynamic_symmetric -s -j
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run intel_all MEMORY=dynamic_symmetric -s -j
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run pgi_all MEMORY=dynamic_symmetric -s -j
echo -n "Symmetric runs finished at " && date
tar cf symmetric.tar `find MOM6-examples -name ocean.stats.gnu -o -name ocean.stats.intel -o -name ocean.stats.pgi`

# Run static executables
echo -n "Static runs started at " && date
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run clean_gnu clean_intel clean_pgi -s
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.run gnu_static_ocean_only MEMORY=static -s -j
echo -n "Static runs finished at " && date
tar cf static.tar `find MOM6-examples -name ocean.stats.gnu -o -name ocean.stats.intel -o -name ocean.stats.pgi`
EOF

echo -n "Run stage waiting for submitted job as of " && date
msub -l partition=c3,nodes=15,walltime=00:34:00,qos=norm -q debug -S /bin/tcsh -j oe -A gfdl_o -z -o job.log -N mom6_regression -K job.sh

# Show output
echo -n "Submitted job returned control at " && date
cat job.log

echo -n "Run stage finished at " && date
