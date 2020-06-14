#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pprint 
from collections import Counter, OrderedDict, defaultdict
import numpy as np
import re

import argparse
import sys
import os
from math import log

import datetime
import time

#probabilite d'observer le mot wi(c) sachant wi-1(b) et wi-2(a) --> P(c|a,b) = #triplet(a, b, c)/#triplet(a, b, ? )


# ----- FONCTIONS ----------------

def load_file(corpus, ponct, maj):
	#charge le fichier passe en argument et retourne une liste contenant tous les tokens du corpus	
	if os.path.isfile(corpus):
		stream = open(corpus, encoding='utf-8')
		liste_tokens = []
		for line in stream.readlines():
			if ponct == False:
				line = line.strip("\n").strip('\r').strip('(').strip(')').strip('"').strip(",").strip()#.split() 
				line = re.compile("[ .,:;-]").split(line)
			else:
				line = line.strip("\n").strip('\r').strip('(').strip(')').strip('"').strip(",").split()
			#listetriplets(line) #pour analyse phrase par phrase: chaque ligne est une liste de triplets.
			#sinon pour transformer tout le texte en une longue liste de triplets :
			for token in line :
				if maj:
				#pour ajout des tokens avec des majuscules:
					if token != " ":
						liste_tokens.append(token)
				#sinon on met tout en min sauf BEGIN NOW et END:
				else:
					if token == "BEGIN" or token == "NOW" or token == "END":
						liste_tokens.append(token)
					else:
						liste_tokens.append(token.lower())
				
		stream.close()
		return liste_tokens
	else:
		print("Le fichier " + str(corpus) +" ne peut pas etre ouvert")
	
def listetriplets(liste):
	#fonction qui a partir d'une liste renvoie la liste de triplets successifs
	liste_triplets = []
	for i in range(0,len(liste)-2):	
		triplet = tuple(liste[i:i+3])
		#liste_triplets.append(tuple(liste[i-1:i+2]))  #plus rapide a ecrire mais moins clair
		liste_triplets.append(triplet)
	return liste_triplets

def build_dicts(liste_triplets):
	"""
	fonction qui a partir d'une liste de triplets (a,b,c) cree des dictionnaires d'occurences
	liste_triplets [(END, BEGIN, 1430),(BEGIN, 1430, daily)...]
	"""
	occ_abc = Counter() #occ de chque triplet (Counter() = elements of a list are stored as dictionary keys and their counts are stored as dictionary values)
	occ_abx = Counter() #compte occ de triplets avec a, b sans c
	ab2abc = {}  #contient 3e mot possible c pour chaque bigramme (a,b). ab2abc[(a,b)] = [liste des differents c possibles]
	proba_cab = {} #contient les probas de c sachant a et b

	for triplet in liste_triplets:		
		a = triplet[0] # I
		b = triplet[1] # love
		c = triplet[2] # chocolate
		occ_abc[triplet] += 1 #Counter() permet d'eviter d'avoir a faire: occ_abc[triplet] = occ_abc[triplet] +1 if triplet in occ_abc else 1
		occ_abx[(a,b)] += 1 

		if not (a,b) in ab2abc:
			ab2abc[(a,b)] = []
			ab2abc[(a,b)].append(c)
		else:			
			liste3eme = ab2abc[(a,b)]
			if c not in liste3eme:
				liste3eme.append(c)
				ab2abc[(a,b)] = liste3eme

		proba_cab[c] = occ_abc[triplet] / occ_abx[(a,b)]			
	
	return occ_abc, occ_abx, ab2abc

#Generer un element ai avec la probabilite pi correspondante
def sample_from_discrete_distrib(distrib): 
	words, probas = list(zip(*distrib.items()))
	return np.random.choice(words, p=probas)

def generate_strophe(occ_abc, occ_abx, ab2abc, nb, vb):
	strophe = ""
	rimes = []
	for i in range(nb):
		ver = gen_ver(occ_abc, occ_abx, ab2abc, rimes, vb)
		strophe += ver + "\n"
		rimes = getRime(ver, vb)
	
	return strophe

def gen_ver(occ_abc, occ_abx, ab2abc, rimes, vb):
	historique = ["BEGIN", "NOW"]
	ver = ""
	
	while historique[len(historique)-1] != "END":  #tant que le dernier terme contenu dans l'historique n'est pas 'END'
		a = historique[len(historique)-2]
		b = historique[len(historique)-1]
		distrib = {}
		
		for c in ab2abc[(a,b)]:
			proba = occ_abc[(a,b,c)]/occ_abx[(a,b)]	
			distrib[c] = proba	

		mot = sample_from_discrete_distrib(distrib)
		historique.append(mot)

		#MODIFIER L'HISTORIQUE POUR AVOIR DES RIMES
		if mot == "END" and len(rimes) > 0 :
			#si on est arrivé a la fin de la phrase / du vers
			motAvantEND = historique[len(historique)-2].strip('!').strip(',').strip('.').strip('"').strip(';').strip('»') #on retient l'avant dernier mot (avant END)			
			if motAvantEND[:-2] not in rimes :
				#s'il ne rime pas avec le dernier mot du ver précédent, on recalcule une distrib a partir des 2 mots qui le précèdent
				a = historique[len(historique)-4]
				b = historique[len(historique)-3]
				distrib = {}
				for c in ab2abc[(a,b)]:
					proba = occ_abc[(a,b,c)]/occ_abx[(a,b)]	
					distrib[c] = proba
				#on regarde les mots possibles d'apres la nouvelle distribution
				mot_possible_prec_count = 0  #variable qui enregistre le nb de lettres qui riment pour le dernier mot possible retenu
				for mot_possible in distrib.keys(): 
					if len(mot_possible) > 2 and mot_possible[-2:] == rimes[len(rimes)-1]: #si les 2 dernieres lettres du mot possible == les 2 dernieres retenues dans rimes (dernier element de la liste)
						if vb:
							print("MOT POSSIBLE APRES ",a, b," QUI RIME:", mot_possible) #si verbiose, on print les rimes possibles s'il y en a
						for i in range(len(mot_possible)):  #pour chaque mot possible, on le decoupe --> mot_possible = 'salut': 
							"""i: 0 - salut[-i:]: salut 
							   i: 1 - salut[-i:]: t 
							   i: 2 - salut[-i:]: ut
							   i: 3 - salut[-i:]: lut
							   i: 4 - salut[-i:]: alut      (on ne conserve donc que la rime la plus riche)
							"""
							if mot_possible[-i:] in rimes and i > mot_possible_prec_count:  #si on trouve une partie du mot possible dans la liste de rimes ET qu'elle est plus riche que celle du mot_possible précedent retenu
								if vb:
									print("RIME AVEC x",rimes[0],":", mot_possible)
								newMot = mot_possible 
								historique[len(historique)-2] = newMot	
								mot_possible_prec_count = i			
				
	
	for mot in historique:
		if mot != "BEGIN" and mot !="NOW" and mot !="END":
			ver += mot + " "	

	return ver

def getRime(ver, vb):
	"""
	'ver' = str, un ver ou 'phrase' du poeme 
	return : str, le dernier mot de ce ver (avant 'END')
	Fonction qui split le dernier ver obtenu (str) en liste, et renvoie le mot juste avant END (str)
	"""
	rimes = []   # salut --> [alut, lut, ut]
	ver_list = ver.split()
	derMot = ver_list[len(ver_list)-1]
	derMot = derMot.strip('!').strip(',').strip('.').strip('"').strip(';').strip('»') #suppression de la ponctuation a la fin du mot
	if len(derMot) > 2:
		for i in range(len(derMot)-1, 1,-1): # pour i décroissant allant de la taille du mot - 1, à 2. 'salut' --> [alut, lut, ut]
			rime = derMot[-i:]
			rimes.append(rime)	
	if vb:
		print("DERNIER MOT DECOUPÉ: ",rimes)	
	return rimes

def corrigPonct(strophe):	
	#Supprime les signes :,; si ils se trouvent a la fin d'une strophe
	ponct = ";,:»"

	for char in strophe[-3:]:
		if char in ponct:
			strophe = strophe.strip().strip().strip(char)
	return strophe 


def main(corpus, o, v, s, p, m, vb):
	t0 = time.clock()  #heure de debut de la generation
	liste_tokens = load_file(corpus, p, m)
	liste_triplets = listetriplets(liste_tokens)
	occ_abc, occ_abx, ab2abc = build_dicts(liste_triplets)
	poeme = ""
	print()

	for i in range(s):
		strophe = generate_strophe(occ_abc, occ_abx, ab2abc, v, vb)
		strophe = corrigPonct(strophe)
		poeme += strophe + "\n"	
		print(strophe)	
		print()

	t1 = time.clock() #heure de fin de la generation
	duree = t1 - t0 #calcul de la duree de generation du poeme

	output = open(str(o)+".txt", 'a', encoding='utf-8') #'a' est comme 'w' mais ecrit a la suite du contenu du fichier sans ecraser
	output.write(str(datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S  "))+str(int(duree))+"s\n\n")
	output.write(poeme)
	output.write("\n--------------------------------------------------\n")
	output.close()



# ----- MAIN ----------------------- 

if __name__ == '__main__':

	usage = """
		   Script qui charge un fichier texte, et estime un modele de langue."
		   """
		
	parser=argparse.ArgumentParser(usage=usage)

	# DEFINITION DES OPTIONS
	parser.add_argument('texte', help = "Fichier texte prealablement traité où chaque ligne est entourée de 'BEGIN NOW' et 'END' ", default='.')
	parser.add_argument('--output', help = "Nom du fichier où enregistrer le texte généré", default='.')
	parser.add_argument('--v', type=int, help = "Nombre de phrase par strophe. Type : int", default=3)
	parser.add_argument('--s', type=int, help = "Nombre de strophes. Type : int", default=3)
	parser.add_argument('--p', action="store_false", help = "Ponctuation off. Type : boolean. Default : on.", default=True)
	parser.add_argument('--m', action="store_false", help = "Majuscules off. Type : boolean. Default : on.", default=True)
	parser.add_argument('--vb', action="store_true", help = "Verbiose on. Type : boolean. Default : off.", default=False)

	args = parser.parse_args()
	corpus = args.texte
	o = args.output
	v = args.v
	s = args.s
	p = args.p 
	m = args.m
	vb = args.vb


	main(corpus, o, v, s, p, m, vb)

