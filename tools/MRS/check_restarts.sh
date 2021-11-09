#!/bin/bash

# Compares ocean.stats for 12 and 02 restart stages

PASS='\033[0;32mPASS\033[0m'
FAIL='\033[0;31mFAIL\033[0m'
expt=$(echo $1 | sed 's:/12.ignore.*::')

new_answer=`tail -1 $1 | sed 's/ *[0-9]*,//'`
right_answer=`tail -1 $2 | sed 's/ *[0-9]*,//'`

if [ "$new_answer" != "$right_answer" ]; then
  echo -e ${FAIL} : restart test for ${expt}
  cat $2 | sed "s,^,$2: ,"
  cat $1 | sed "s,^,$1: ,"
  exit 1
fi

echo -e ${PASS} : restart test for ${expt}
