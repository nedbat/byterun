#!/bin/bash
me=${BASH_SOURCE[0]}

STOP_ONERROR=${STOP_ONERROR:-1}

typeset -i BATCH=${BATCH:-0}
if (( ! BATCH )) ; then
    isatty=$(/usr/bin/tty 2>/dev/null)
    if [[ -n $isatty ]] && [[ "$isatty" != 'not a tty' ]] ; then
	BATCH=0
    fi
fi


function displaytime {
  local T=$1
  local D=$((T/60/60/24))
  local H=$((T/60/60%24))
  local M=$((T/60%60))
  local S=$((T%60))
  (( $D > 0 )) && printf '%d days ' $D
  (( $H > 0 )) && printf '%d hours ' $H
  (( $M > 0 )) && printf '%d minutes ' $M
  (( $D > 0 || $H > 0 || $M > 0 )) && printf 'and '
  printf '%d seconds\n' $S
}

# Test directory setup
srcdir=$(dirname $me)
cd $srcdir
fulldir=$(pwd)

XPYTHON=${XPYTHON:-xpython}

if [[ -n $1 ]] ; then
    files=$1
else
    files=$(echo test_*.py */test_*.py)
fi


for file in $files ; do
    echo ==== $(date +%X) $file ====
    ${XPYTHON} $file;
    echo ==== $(date +%X) $file ====
    (( rc != 0 && allerrs++ ))
    if (( STOP_ONERROR && rc )) ; then
	echo "** Ran $i tests before failure. Skipped $skipped test for known failures. **"
	exit $allerrs
    fi
done

typeset -i ALL_FILES_ENDTIME=$(date +%s)

(( time_diff =  ALL_FILES_ENDTIME - ALL_FILES_STARTTIME))

printf "Ran $i unit-test files, $allerrs errors; Elapsed time: "
displaytime $time_diff
