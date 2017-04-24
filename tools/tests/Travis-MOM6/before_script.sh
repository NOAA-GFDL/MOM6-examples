#!/bin/bash -f
echo -e '#override DAYMAX=0.125\n#override ENERGYSAVEDAYS=0.01\n#override NIGLOBAL=120\n#override NJGLOBAL=60' > MOM6-examples/ocean_only/benchmark/MOM_override
