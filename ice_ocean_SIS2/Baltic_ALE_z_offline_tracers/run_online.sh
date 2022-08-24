# Copy over the input files for the forward run
cp diag_table_online diag_table
cp input.online.nml input.nml
cp MOM_override_online MOM_override

# Run the forward model
mprun ./MOM6_coupled

# Make the directory where online fields will be stored and copy diagnostics
mkdir ONLINE
mv *off_snap* ONLINE/
mv *off_sum* ONLINE/
mv *off_avg* ONLINE/
