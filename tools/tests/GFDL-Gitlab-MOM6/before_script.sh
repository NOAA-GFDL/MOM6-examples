#!/bin/bash -f

echo -n "Before script started at " && date
# Record environment (for debugging gitlab pipelines)
env > gitlab_session.log

# Pre-process land and set up link to datasets
test -d MOM6-examples/src/LM3 || make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.clone clone_gfdl -s
make -f MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/Makefile.clone MOM6-examples/.datasets -s

# Build a manifest of runs to make with PE counts
bash MOM6-examples/tools/tests/GFDL-Gitlab-MOM6/generate_manifest.sh > manifest.mk

echo -n "Before script finished at " && date
