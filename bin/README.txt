********************************
GWAS Results Lookup (GREL) v0.1.0
2019-03-20
********************************

1. 
Introduction
This tool was created with ease-of-lookup of locally provided GWAS summary statistics in mind.
In its basicality it is a streamlined/batch lookup for LOCUSZOOM program ( http://locuszoom.org ) with a capability of doing so across several different datasets and several different genomic annotations.
At the moment the only provided GWAS summary statistic datasets come from the GEFOS website ( http://www.gefos.org ).

2. 
Before first usage, a script will return a following output:
***PROBLEM***
$DATASETS file not found!
Running "Find_Databases.sh"
Re-run the script!
*************

This will in turn create a folder "locuszoom_results" located at /home/$MSN/locuszoom_results/ ($MSN = microsectienummer).
In the same folder a file "Datasets.txt" will be created. This is important to know and is referenced further down.

3. 
Usage

3.1. 
The alias itself for the script should already be exported server-wide.
The basic command follows the formula:

	`grel [gene name -OR- name of text file with gene names separated by newlines]`

3.2.
Gene name(s) should be:
	- Officials Gene Symbol as provided by HGNC ( https://www.genenames.org )
		--e.g. TGFB1
	- Aliases for the gene as provided by NCBI ( https://www.ncbi.nlm.nih.gov )
		--e.g. for TGFB1: CED; LAP; DPD1; TGFB; TGFbeta
	- rsID for SNPs of interest, aligned to GRCh37
		--e.g. rs1800468
	- Genomic position, as denoted by chrn:i, where n...chromosome and i...bp on said chromosome
		--e.g. chr19:41860587
If you need to check several genes in a "batch", you can list them in a (text) file, each gene separated by a newline, e.g.
TGFB1
FDF23
ESR1
...

3.3.
Output(s) will be written to "locuszoom_results" folder.

3.4.
"Datasets.txt" file contains dirlinks to the locally provided datasets of GWAS summary statistics.
If you do not wish to scan a specific dataset, edit the "Datasets.txt" file by putting the "#" character in front of the very same dataset dirlink.
e.g.
/home/$MSN/Datasets/Adult_Lean_Mass_2017/appendicularleanmass_FINAL.txt 
...is a dirlink to Adult Lean mass GWAS (2017) dataset.
By putting a hash sign (#) in front of it, the script will not analyze it 
i.e.
#/home/$MSN/Datasets/Adult_Lean_Mass_2017/appendicularleanmass_FINAL.txt
...thus the dataset will be ignored.

4.
Output
For each individual gene name a subfolder will be made inside the "locuszoom_results" folder.
The naming schema:
yy-mm-dd--hh-mm-gene_name/
yy...last two digits of the year the lookup for this specific gene was ran (e.g. "19")
mm...two digit designation of the month the lookup for this specific gene was ran (e.g. "03")
dd...two digit designation of the day the lookup for this specific gene was ran (e.g. "20")
hh...a 24-hour designation of the hour the lookup for this specific gene was ran (e.g. "15")
mm...two digit designation of the minutes of the hour the lookup for this specific gene was ran (e.g. "03")
gene_name...gene name under which the gene under 3.2 was called.

Inside each such subfolder there will be two files for each analyzed dataset.
	1. A locuszoom graph file
		a. Naming schema: gene_name-dataset_file_additional
			- gene_name...gene name under which the gene under 3.2 was called
			- dataset_file...a name of the dataset text file (e.g. "appendicularleanmass_FINAL.txt")
		b. Area of interest is +-500kb from the gene, referenced under 3.2, transcription start and stop
	2. A filtered dataset file
		a. SNPs within +-500kb from the gene, reference under 3.2, transcription start and stop are filtered out

5.
Misc
For any additional questions/problems, send me an e-mail at: v.prijatelj@erasmusmc.nl

