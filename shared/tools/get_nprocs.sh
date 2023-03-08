#!/bin/sh

nx=$(grep -oP "(?<=^NIPROC = )[0-9]*" $1/MOM_parameter_doc.layout)
ny=$(grep -oP "(?<=^NJPROC = )[0-9]*" $1/MOM_parameter_doc.layout)

masktable=INPUT/$(grep -oP "(?<=^MASKTABLE = \")[^\"]*" $1/MOM_parameter_doc.layout)
if [ -f ${masktable} ]; then
    read -r nmask < ${masktable}
else
    nmask=0
fi

np=$(( nx * ny - nmask ))

echo $np
