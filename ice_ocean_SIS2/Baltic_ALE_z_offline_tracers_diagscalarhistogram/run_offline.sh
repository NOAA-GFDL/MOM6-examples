# Copy over the input files for the offline run
cp diag_table_offline diag_table
cp input.offline.nml input.nml
cp MOM_override_offline MOM_override

# Run the forward model
mprun ./MOM6_ocean_only
