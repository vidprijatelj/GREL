#!/usr/bin/bash

CURRENT_DIR=$(realpath "$0")
PARENT_DIR=$( dirname "$( dirname "$( realpath "$0" )" )" )
DATASETS="${PARENT_DIR}/Datasets/"
HOME_DIR=$(realpath ~)
LOCUSZOOM="$HOME_DIR/locuszoom_results/"


# Function create_datasets
# When calling it, an argument should always be the home folder of the datasets location
# i.e. "Datasets", in our case "$DATASETS"
## Arguments:
# $1 - Datasets location
## Returns:
# Nothing
## Effect:
# Creates "Datasets.txt" file at "~/locuszoom_results/"
create_datasets () {
	local DIR=$1
	for f in `find $DIR -type f`;
	do
		echo $f | grep -v 'Original_Data' | grep -v '.bcp' | grep -v '.py' | grep '.txt' >> "${LOCUSZOOM}Datasets.txt"
	done	
}

if [ -d "$LOCUSZOOM" ]
then
	if [ ! -f "${LOCUSZOOM}Datasets.txt" ]
	then
		create_datasets "$DATASETS"
	fi
else
	mkdir "$LOCUSZOOM"
	create_datasets "$DATASETS"
fi

sort "${LOCUSZOOM}Datasets.txt" >> "${LOCUSZOOM}Datasetst.txt"
mv "${LOCUSZOOM}Datasetst.txt" "${LOCUSZOOM}Datasets.txt"
