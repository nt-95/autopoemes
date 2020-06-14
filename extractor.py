# coding: utf-8
import os
import csv
import requests
from bs4 import BeautifulSoup
import pprint
import datetime
import time


#WIKISOURCE
def extrWiki(link):
	soup = BeautifulSoup(requests.get("https://fr.wikisource.org/wiki/Cat%C3%A9gorie:Po%C3%A8tes").text, 'lxml')
	page_suiv = ""
	for link in soup.find_all('a'):
		if "page suivante" in str(link.string):
			page_suiv = link.get('href') #on enregsitre la page suivante dans une variable

		if "Auteur:" in str(link.string):
			try:
				print(link.string)
			except UnicodeEncodeError: 
				""
			page_auteur = link.get('href')
			#soup_auteur = BeautifulSoup(requests.get("https://fr.wikisource.org"+str(page_auteur)).text, 'lxml')			
			soup_auteur = BeautifulSoup(requests.get("https://fr.wikisource.org/wiki/Auteur:Michel_Abadie").text, 'lxml')			
			for link in soup_auteur.find_all('a'):
				pass

	print('page suivante : ', page_suiv)

	#print('a')

#POESIE-FRANCAISE.FR
def extrPF(): 
	corpus = ""
	soup = BeautifulSoup(requests.get("http://www.poesie-francaise.fr/poemes-auteurs/").text, 'lxml')
	div = soup.find('div', 'menu-centrale')
	for ul in div.find_all('ul'):
		if 'poemes_' in str(ul.attrs):   #si l'id ou la class de la ul contient 'poemes_' (suivi d'une lettre)
			for link in ul.find_all('a'):  #pour chaque lien de cette ul
				if 'poemes' in str(link) and 'charles-baudelaire' not in str(link) and 'paul-verlaine' not in str(link) and 'guillaume-apollinaire' not in str(link):   #si ce lien contient 'poemes' (suivi du nom de l'auteur)
					page_auteur = link.get('href')   #on enregistre le lien, qui mene vers la page ou sont tous les poemes de l'auteur
					print(page_auteur)
					soup_auteur = BeautifulSoup(requests.get(page_auteur).text, 'lxml')
					count_poem = 0
					for div in soup_auteur.find_all("div", "poemes-auteurs"): #pour chaque div de la page auteur contenant la liste des poemes
						for link in div.find_all('a'):   #pour chaque lien de cette div
							if 'poeme' in str(link):             #si il contient 'poeme'(suivi du titre du poeme)
								count_poem += 1
								print("Scraping poem {}".format(count_poem))
								page_poeme = link.get('href')    #on enregistre ce lien qui mène vers le poeme
								soup_poeme = BeautifulSoup(requests.get(page_poeme).text, 'lxml')  #et on transforme son contenu en BS
								try:
									div = soup_poeme.find("div", "postpoetique")  # sur la page du poeme, on prend la div qui contient le poeme
									
									for p in div.find_all('p'):   #on extrait le texte de tous ses paragraphes
										t = p.get_text("\n")
										if len(t) != 0 and t[0] != '@':
											corpus += t + "\n"
								except AttributeError:
									""
	output(corpus)
					

def pf():
	soup_auteur = BeautifulSoup(requests.get("http://www.poesie-francaise.fr/poemes-louise-ackermann/").text, 'lxml')
	for div in soup_auteur.find_all("div", "poemes-auteurs"): #pour chaque div de la page auteur contenant la liste des poemes
		for link in div.find_all('a'):   #pour chaque lien de cette div
			if 'poeme' in str(link):             #si il contient 'poeme'(suivi du titre du poeme)
				page_poeme = link.get('href')    #on enregistre ce lien qui mène vers le poeme
				soup_poeme = BeautifulSoup(requests.get(page_poeme).text, 'lxml')  #et on transforme son contenu en BS
				div = soup_poeme.find("div", "postpoetique")  # sur la page du poeme, on prend la div qui contient le poeme
				
				for p in div.find_all('p'):   #on extrait le texte de tous ses paragraphes
					print(p.find_next_sibling('p'))
					t = p.get_text("\n")
					if len(t) != 0 and t[0] != '@':
						corpus += t + "\n"
	output(corpus)

#POESIE ANGLAISE : POETRYFOUNDATION.ORG
def extrPA():
	corpus = ""
	t0 = time.clock()  #heure de debut de l'extraction

	for i in range(1,10):
		soup = BeautifulSoup(requests.get("https://www.poetryfoundation.org/poems/browse#page="+str(i)+"&sort_by=recently_added&school-period=1951-present").text, 'lxml')
		h2_list = soup.body.find_all('h2', "c-hdgSans c-hdgSans_2") # liste de toutes les balises h2, qui contiennent les liens vers les poèmes [<h2 <a href=.../a> </h2>, ... ]
		links_to_poems = [] #liste qui contiendra tous les liens directement sous forme 'http://...'
		for h2 in h2_list:  
			a = h2.find('a')  #pour chaque balise <h2> dans la liste, on cherche la balise a 
			links_to_poems.append(a["href"]) #et on extrait le lien de a
		corpus += str(links_to_poems) + "\n"  


	output(corpus)
	t1 = time.clock() #heure de fin de la generation
	duree = t1 - t0 #calcul de la duree de generation du poeme
	print(duree) 	# 10 pages = 4,31667min   1000p = 4316,67 min

	"""
		#on regarde maintenant le HTML de chaque lien vers un poeme, pour selectionner le texte du poeme
		for i in range(len(links_to_poems)-1):
			new_soup = BeautifulSoup(requests.get(links_to_poems[i]).text, 'lxml')
			div_list = new_soup.body.find_all('div') #comme les poèmes sont contenus dans des div debiles  [<div style=...> ver1 <br></div>, <div style=...> ver2<br></div>,.. ]
			
			for div in div_list:
				if div.has_attr('style'):  #trouver les div avec l'attr style 
					if isinstance(div.contents[0],str):   # div.contents = ['blablabla ver1', <br>]  // div.contents[0] = 'blablabla ver1'
						corpus += div.contents[0] + "\n"  
	output(corpus)
	t1 = time.clock() #heure de fin de la generation
	duree = t1 - t0 #calcul de la duree de generation du poeme
	print(duree) 	# 10 pages = 4,31667min   1000p = 4316,67 min
	"""
	
def output(soup):
	file = open("soup.txt", 'w', encoding='utf-8')
	file.write(str(soup))
	#file.write(str(corpus))
	file.close()


#extrWiki("")
#extrPF()
#pf()
#extrPA()

