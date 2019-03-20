#!/usr/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#echo "$DIR"
GREL=$DIR/Grel.py
#echo "$GREL"
WD=`pwd`
#echo "$WD"
FILENAME=$WD/$1
#echo "$FILENAME"
DATASETS="$(realpath ~)/locuszoom_results/Datasets.txt"

if [[ ! -f $DATASETS ]]
then
	echo
	echo "***PROBLEM***"
	echo "$DATASETS file not found!"
	echo "Running \"Find_Databases.sh\""
	${DIR}/Find_Databases.sh
	echo "Re-run the script!"
	echo "*************"
	echo
	exit 1
fi

if [[ -f $FILENAME ]]
then
	while read -r line; do
		gene="$line"
		python3.6 $GREL $line
	done < $FILENAME
fi

if [[ ! -f $FILENAME ]] && [[ -n "$1" ]]
then
	python3.6 $GREL $1
fi

if [[ ! -n "$1" ]]
then
	python3.6 $GREL
fi
