#!/opt/software/Python3/bin/python3.6

import sys
import os
import re
import pandas as pd
import numpy as np
import multiprocessing as mp
import pathlib
from datetime import datetime
from Entrez_Lookup import GeneLookup


# Change the dir to the script's location e.g. /opt/scripts/...
dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir)

# Receive the input we wish to check
# If the input starts with 'rs' or 'chr', we do not run the Entrez_Lookup.py
# Instead we do a filtering on the datasets themselves...meh, just keep on
# reading. I don't feel like explaining right now, it's 18th December 2018,
# Tuesday, weather is shitty and I'm REALLY hungry...
# Anyway, it is Thursday, 17th January 2019. We check for sys.args. If there
# are any, we use sys.argv[1] i.e. the first specified gene, regardless of how
# many there are in use. 
if len(sys.argv) > 0:
    input_gene = sys.argv[1]
    input_gene = input_gene.strip()
else:
    input_gene = input('***\n\nPlease input the gene of interest for the GWAS REsults Lookup:\n')
    input_gene = input_gene.strip()


# If the user inputs the 'rs' command, we proceed with several expectations
# i.e. we will not do an online checkup for the SNP location, we will extract
# the SNP location from each dataset seperately
if (input_gene.startswith('rs')) and (input_gene.upper()!='RS'):
    gene_name = input_gene
# If the user inputs the 'chr' command, we extract the genome location from the
# input itself i.e. the chromosome and the bp location
elif (input_gene.startswith('chr')) and (input_gene.upper()!='CHR'):
    gene_name = input_gene
    chromosome = str((gene_name.split(':')[0]).split('chr')[1])
    transcr_start = int(gene_name.split(':')[1])
    transcr_stop = transcr_start
    gene_name = "chr" + str(chromosome) + "-" + str(transcr_start)

# Else we run a Entrez_Lookup script so that the gene information is fetched
# from Entrez API.
else:
    gene_information = GeneLookup(gene = input_gene)
    gene_id = gene_information.get_gene_id()
    chromosome, transcr_start, transcr_stop = \
        gene_information.get_gene_position(gene_id)
    chromosome = str(chromosome)
    gene_name = gene_information.gene_name

# Define our region of interest i.e. +-250kbp around our gene of interest
# Relevant only if input of 'gene' does not start with 'rs'
# If it starts with 'chr', we already know the region of interest from name
if (not gene_name.startswith('rs')) and (gene_name.upper()!="RS"):
    if (int(transcr_start) - 500000 < 0):
        upstream_limit = 1
    else:
        upstream_limit = int(transcr_start) - 500000
    downstream_limit = int(transcr_stop) + 500000


#####################
### MAIN FUNCTION ###
#####################


# Run the LocusZoom program with relevant information
def run_locus_zoom(filename):

    # UGLY; LOOK AWAY! #
    global gene_name
    global chromosome
    global transcr_start
    global transcr_stop
    global upstream_limit
    global downstream_limit
    # UGLY; LOOK AWAY! #

    # Remove special characters from the line i.e. '\r' and/or '\t'
    # hence returning the full path to the dataset .txt file
    file = filename.rstrip()

    # Define the most-right word of the full path of the dataset .txt file
    # as a title for our LocusZoom plot
    title = file.split('/')[len(file.split('/')) - 1]
    print('*******************')
    print('Working on:', title)
    print('Working with:', gene_name)

    # Dataset parsing, cleaning, defining
    dataset_file = pd.read_table(file, sep = '\t', dtype = {'Chromosome' : str, \
        'bp' : np.int32})

    # Since we skipped annotating the 'rs' information above (we only defined
    # the genome position for genes starting with 'chr' and de facto gene names),
    # this is the position where we define our chromosome and bp position for
    # 'rs' information
    empty = False
    if (gene_name.startswith('rs')) and (gene_name.upper()!="RS"):
        temp_df = dataset_file[dataset_file['MarkerName'] == gene_name]
        if temp_df.empty:
            empty = True
        else:
            chromosome = str(temp_df.iloc[0]['Chromosome'])
            if (int(temp_df.iloc[0]['bp']) - 500000) < 0:
                upstream_limit = 1
            else:
                upstream_limit = int(temp_df.iloc[0]['bp']) - 500000
            downstream_limit = int(temp_df.iloc[0]['bp']) + 500000


    # If our input starts with 'chr', we do a proxy naming scheme via genome
    # position i.e. we translate the 'chr' to 'rs' naming convention. If we
    # have no SNPs with this specific location, we leave it as it is i.e.
    # chrN:position
    if gene_name.startswith('chr'):
        x_gene_name = dataset_file[(dataset_file['Chromosome'] == chromosome) & \
            (dataset_file['bp'] == transcr_start)]
        if not x_gene_name.empty:
            gene_name = x_gene_name.iloc[0]['MarkerName']
            #gene_name = str(gene_name)

    # We filter our dataframe to +-250kbp; pruning the data footprint
    if empty == False:
        dataset_file = dataset_file[dataset_file['Chromosome'] == chromosome]
        dataset_file = dataset_file[(dataset_file['bp'] > upstream_limit) & \
            (dataset_file['bp'] < downstream_limit)]
    else:
        dataset_file = pd.DataFrame()

    # We keep 'MarkerName' and 'P-value' columns since LocusZoom knows how
    # to work with these only
    if not dataset_file.empty:
        save_file = dataset_file
        dataset_file = dataset_file.iloc[:,[0,3]]
        MarkerName = str(dataset_file.columns.values[0])
        P_value = str(dataset_file.columns.values[1])
        print(MarkerName, P_value)

    # Create a temporary file for LocusZoom; there is no direct way to pipe
    # our dataframe to LocusZoom directly
    # Save the temporary file to the user's home dir and later on delete it
    if not dataset_file.empty:
        temp_file = f'{user_dir}/{title}_temp'
        dataset_file.to_csv(temp_file, sep = '\t', index = False)

    # Define the variable column names of the dataset file, since LocusZoom otherwise
    # requires the columns to be static i.e. a constant 'MarkerName' or 'P-value'. Our datasets
    # do not have a unified naming convention.

    # Debugging purposes since I cannot be bothered with a proper IDE
    if not dataset_file.empty:
        print(gene_name, chromosome, upstream_limit, downstream_limit)

    if not dataset_file.empty:
    # Run LocusZoom from the user's home location/folder
    # Population: EUR
    # Reference build: hg19 (update it? Commented 12-12-2018)
    # Source for LD score: 1000 Genomes, March 2012 (update it? Commented 12-12-2018)
    # SNP source: temporary file created and defined as 'temp_file' variable
    # Chromosome: Defined by our gene of interest
    # Start position: 250kb upstream from our gene of interest
    # End position: 250kb downstream from our gene of interest
    # P value column: defined as a 'P_value' variable; different for each .txt
    #   dataset file
    # Output prefix: using our gene of interest name + title of each plot i.e.
    #   the name of the .txt dataset file

        # Running locuszoom with 'rs' naming convention i.e. inputs beginning
        # with 'rs' and 'chr'
        if gene_name.startswith('rs'):
            os.system(f'/opt/locuszoom/bin/locuszoom --pop EUR --build hg19 \
                --source 1000G_March2012 --metal {temp_file} \
                --chr {chromosome} --start {upstream_limit} \
                --end {downstream_limit} --markercol {MarkerName} \
                --pvalcol {P_value} --prefix {gene_name+title} \
                signifLine=7.3,5 title="{gene_name} {title}" \
                --refsnp {gene_name} --plotonly > /dev/null 2>&1')
        else:
        # Running locuszoom with all the other posibilities i.e. de facto gene
        # names/aliases/other...
            os.system(f'/opt/locuszoom/bin/locuszoom --pop EUR --build hg19 \
                --source 1000G_March2012 --metal {temp_file} \
                --chr {chromosome} --start {upstream_limit} \
                --end {downstream_limit} --markercol {MarkerName} \
                --pvalcol {P_value} --prefix {gene_name+title} \
                signifLine=7.3,5 title="{gene_name} {title}" --plotonly \
                > /dev/null 2>&1')

        save_file.to_csv(f'{gene_name+title}.csv', sep = '\t', index = False)

    else:
        print(f'Gene {gene_name} not contained in dataset {line}')

    # Remove the temporary file used for LocusZoom
    if not dataset_file.empty:
        os.system(f'rm {temp_file}')

    print()
    print('Done with:', title, '\n')


###########################
### CALLING THE PROGRAM ###
###########################


# Define datasets_file variable, that holds the full path to all the .txt 
# dataset files in '../Datasets/' folder
user_dir = os.path.expanduser('~')
datasets_file = user_dir + '/locuszoom_results/Datasets.txt'

with open(datasets_file, 'r') as f:
    
    # We define the default user folder i.e. '~' for each user seperately
    # We define a current date and time in a format:
    #   year (2 digits) - month - day -- hour - minute
    # We define a folder name in which all locuszoom output will be saved
    #   the output folder will hence be '~/locuszoo_results/datetime-gene/'
    #   and results of each dataset will be seperately saved in a new folder
    #   'gene_name+dataset title'
    user_dir = os.path.expanduser('~')
    date_time_creation = datetime.now().strftime('%y-%m-%d--%H-%M')
    locuszoom_folder_name = f'{date_time_creation}-{gene_name}'
    pathlib.Path(user_dir+'/locuszoom_results/'+locuszoom_folder_name).mkdir(parents=True, \
        exist_ok=True)
    os.chdir(user_dir+'/locuszoom_results/'+locuszoom_folder_name)
    
    for line in f:
        if not line.startswith('#'):
            run_locus_zoom(line)
