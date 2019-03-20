#!/opt/software/Python3/bin/python3.6

import urllib.request as REQ
import xml.etree.ElementTree as ET
import sys


class GeneLookup:

    # Base URL from which all requests are done
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


    def __init__(self, gene, organism = 'HOMO+SAPIENS'):
        self.gene = gene.strip()
        self.organism = organism
        print('\n*** Gene lookup in progress ***\n')
        print('Lookup based on input string ' + self.gene)


    def get_gene_id(self):
        ###
        #   Description:
        #       Search url that will return us a search XML
        #       Always include '&sort=relevance' to the term!
        ###
        #   Returns:
        #       gene_id: int
        #           a gene ID for our most relevant gene of interest
        ###

        search_url = 'esearch.fcgi?db=gene&term=' + self.gene + '+' + self.organism + \
        '&usehistory=y' + '&sort=relevance'
        # Our search url result - an XML that we transform into an XML
        # tree-like element 
        search_content = REQ.urlopen(self.base_url + search_url).read()
        search_root = ET.fromstring(search_content)
        
        # Check if our result is from HOMO SAPIENS
        for term in search_root.findall('TranslationSet'):
            translation = term.find('Translation')
            homo = translation.find('From').text
            if homo == 'HOMO SAPIENS':
                print('\nHOMO SAPIENS CONFIRMED!\n')
            else:
                print(homo + ' SPECIES!\n')

        # Find all the gene IDs and choose the first one i.e. the most relevant
        # one
        for id in search_root.findall('IdList'):
            gene_id = id.findall('Id')[0].text

        return gene_id


    def get_gene_position(self, gene_id):
        ###
        #   Description:
        #       Given gene ID (as a variable gene_id) returns its chromosome
        #       position, start bp and end bp position
        ###
        #   Returns:
        #       chromosome: int
        #           chromosome position for our gene ID
        #       transcription_start: int
        #           bp position of our transcription start
        #       transcription_stop: int
        #           bp position of our transcription stop
        #
        #       NOTE: TRANSCRIPTION START IS ALWAYS SMALLER, EVEN IF
        #       TRANSCRIPTION ITSELF IS IN ANTISENSE DIRECTION
        ###

        summary_url = 'esummary.fcgi?db=gene&id=' + gene_id
        # Our summary url result - an XML that we transform into an XML
        # tree-like element
        summary_content = REQ.urlopen(self.base_url + summary_url).read()
        summary_root = ET.fromstring(summary_content)

        # Find our gene name, other aliases, summary, and chromosome
        self.gene_name = summary_root.find('DocumentSummarySet').find('DocumentSummary') \
                    .find('Name').text
        other_aliases = summary_root.find('DocumentSummarySet') \
                    .find('DocumentSummary').find('OtherAliases').text
        description = summary_root.find('DocumentSummarySet') \
                    .find('DocumentSummary').find('Summary').text
        chromosome = summary_root.find('DocumentSummarySet') \
                    .find('DocumentSummary').find('Chromosome').text

        # Find the assembly build 37 i.e. GRCh37.p13
        location_history = summary_root.find('DocumentSummarySet') \
                    .find('DocumentSummary').find('LocationHist')
        for type in location_history:
            if type.find('AnnotationRelease').text == '105':
                if type.find('AssemblyAccVer').text == 'GCF_000001405.25':
                    transcription_start = type.find('ChrStart').text
                    transcription_stop = type.find('ChrStop').text

        # Some genes can be transcribed anti-sense. Sort!
        if transcription_start > transcription_stop:
            transcription_start, transcription_stop = transcription_stop, \
            transcription_start

        print('ENTREZ gene name: ' + self.gene_name, '\n\n' + 'Other aliases: ' \
        +  str(other_aliases), '\n' + '\nDescription:\n' + str(description) + '\n')

        return chromosome, transcription_start, transcription_stop


def main():

    if len(sys.argv) < 2:
        print('Non compliant number of arguments. Please include one gene!')
        print('Gene should always be in the second position!')
        sys.exit()
    else:
        gene = sys.argv[1].upper()

    gene_information = GeneLookup(gene = gene)
    gene_id = gene_information.get_gene_id()
    gene_chromosome, gene_transcription_start, gene_transcription_stop = \
    gene_information.get_gene_position(gene_id)
    print(gene_chromosome, gene_transcription_start, gene_transcription_stop)
    print(gene_information.gene_name)

if __name__ == "__main__":
    main()
