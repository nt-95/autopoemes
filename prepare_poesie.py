#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import os


def load_file(corpus, output):
	"""
	corpus : fichier texte (poeme) extrait de Wikisource
	fonction qui ajoute BEGIN NOW et END au debut et a la fin cree un nouveau fichier texte 
	"""
	stream = open(corpus, encoding='utf-8')
	out = open(output, "w", encoding='utf-8')
	numbers = "1234567890"
	for line in stream:
			if len(line) > 5 and line !="\n" and line.isupper() == False and line[0] not in numbers and line[4] not in numbers and "UTC+" not in line and "http" not in line:#"1" not in line and "2" not in line:	#derniere exception pour eviter les numeros de pages apres 100 ou 200	
				#line = line.strip("\n").split()
				out.write("BEGIN NOW "+line.strip("\n").strip(" ").strip("»").strip("«").strip(" ").strip(" ")+" END\n")

				#print(line)
	stream.close()


# ----- MAIN ----------------------- 

if __name__ == '__main__':

	usage = """
		   Script qui charge un fichier issu de wikisource, et le traite afin d'etre utilisable par le generateur.py."
		   """

	parser=argparse.ArgumentParser(usage=usage)

	# DEFINITION DES OPTIONS
	parser.add_argument('corpus_poeme', help = "Fichier texte issu de Wikisource (poeme)", default='.')
	parser.add_argument("-output", '--output', help="Nom du fichier d'output")
	args = parser.parse_args()
	corpus = args.corpus_poeme
	output = args.output

	load_file(corpus, output) 
