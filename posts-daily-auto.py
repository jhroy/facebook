# ©2018 Jean-Hugues Roy. GNU GPL v3.
# coding: utf-8

# Ce script est déclenché à tous les jours à 23h59

import csv, facebook, requests, datetime, os, glob
from datetime import datetime, timedelta
from pytz import timezone
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pymysql.cursors

# Pour trouver la date à moissonner, il faut d'abord savoir quelle date on est

now = datetime.now()
heureEst = timezone("US/Eastern")

# Fonction qui écrit les données relatives aux commentaires

def ecritureCommentaires():
	lepost.append(commentairesTotaux)
	lepost.append(commentairesSurCommentaires)
	lepost.append(likesSurCommentaires)

# Comme on a besoin de selenium, il faut initialiser un chromedriver

chrome_options = Options()
chromedriver = "/usr/local/bin/chromedriver"
prefs = {"profile.password_manager_enabled": False, "credentials_enable_service": False}
chrome_options.add_experimental_option("prefs", prefs)
yo = webdriver.Chrome(executable_path = chromedriver,chrome_options=chrome_options)

# Selenium se connecte à Facebook en entrant mon courriel et mon mot de passe, confinés ailleurs

yo.get("https://www.facebook.com/jhroy/")
yo.find_element_by_id('email').send_keys("XXX")
yo.find_element_by_id('pass').send_keys("YYY")
yo.find_element_by_xpath("//input[@type='submit']").click()

# Selenium ouvre ensuite une page de la section «developers» me permettant d'obtenir un jeton d'accès

yo.get("https://developers.facebook.com/tools/accesstoken/")

source = yo.page_source
page = BeautifulSoup(source,"html.parser")

# J'obtiens un jeton d'accès qui diffère en fonction du jour du mois

codes = page.find_all("code")

if now.day in [0,5,10,15,20,25,30]:
	jeton = codes[0].text
elif now.day in [2,7,12,17,22,27]:
	jeton = codes[2].text
elif now.day in [4,9,14,19,24,29]:
	jeton = codes[4].text
elif now.day in [1,6,11,16,21,26,31]:
	jeton = codes[6].text
elif now.day in [3,8,13,18,23,28]:
	jeton = codes[8].text

# Selenium ferme la page

yo.close()

print("\n","&"*80)
print("Comme on est le {}, on a le jeton suivant:\n{}".format(now.day,jeton))
print("&"*80,"\n")

annee = now.year
mois = now.month
jour = now.day

# Les variables début et fin servent à déterminer le début (minuit) et la fin (23h59 et 59 secondes) du moissonnage

debut = "{}-{}-{} 00:00:00.000000".format(annee,mois,jour)
fin = "{}-{}-{} 23:59:59.999999".format(annee,mois,jour)

# Ici, on retranche 15 jours à nos variables debut et fin.

heureDebut = datetime.strptime(debut, "%Y-%m-%d %H:%M:%S.%f") - timedelta(days=15)
heureFin = datetime.strptime(fin, "%Y-%m-%d %H:%M:%S.%f") - timedelta(days=15)

print(heureDebut,heureFin)

annee2 = heureDebut.year
mois2 = heureDebut.month
jour2 = heureDebut.day

# Ici, on obtient les valeurs temps UNIX du début et de la fin du moissonnage
# On a besoin de ces valeurs car c'est ce dont se servira l'API Graph pour savoir où commencer et finir le moissonnage

since = int(heureDebut.strftime("%s"))
until = int(heureFin.strftime("%s"))

print(since)
print(until)

# Création d'un objet pour se connecter à l'API Graph

graph = facebook.GraphAPI(access_token=jeton,version="2.7")

# Connection à ma base de données SQL

connection = pymysql.connect(host='localhost',
	user='ZZZ',
	password="",
	db='facebook',
	charset='utf8mb4', # Jeu de caractères UTF-8 augmenté pour tenir comptes des emojis, qu'on retrouve en quantité industrielle dans les publications Facebook
	cursorclass=pymysql.cursors.DictCursor)

# On commence par aller chercher la liste des médias dont on va extraires les publications

try:
	with connection.cursor() as cursor:
		sql = "SELECT * FROM medias"
		cursor.execute(sql)
		medias = cursor.fetchall()

	n = 0
  
  # Boucle grâce à laquelle on examine un média à la fois

	for media in medias:
		print("\n","#"*80,"#"*80,"   >>> On extrait {}".format(media["titre"]))
    
    # On extrait toutes les publications («posts») de ce média ce jour-là
    
		posts = graph.get_object("{}?fields=posts.since({}).until({}).limit(100)".format(media["fbID"],since,until))
    
    # S'il y en a, on les examine une à la fois

		try:
			lesposts = posts["posts"]["data"]
			print("\n","@"*80)
			print("{} posts publiés par le média {} le {}-{}-{}".format(len(lesposts),media["titre"],annee2,mois2,jour2))

			for post in lesposts:
				n += 1
				# print(post["id"])
        
        # On met dans la variable infos toutes les informations relatives à cette publication
        
				infos = graph.get_object("{}?fields=message,description,caption,link,name,status_type,source,story,type,shares".format(post["id"]))
				
        # La variable message contient le message principal de la publication
        
				try:
					message = infos["message"]
				except:
					message = "?"
          
        # La variable description contient une description de la publication

				try:
					description = infos["description"]
				except:
					description = "?"

	# La variable nom contient le titre de la publication
        
        			try:
					nom = infos["name"]
				except:
					nom = "?"

	# La variable vignette contient un bas de vignette, s'il y a lieu
        
        			try:
					vignette = infos["caption"]
				except:
					vignette = "?"

	# La variable source contient la source de la publication (souvent, c'est le média lui-même)
        
        			try:
					source = infos["source"]
				except:
					source = "?"

	# La variable histoire contient parfois des infos de base, en anglais, du genre «TVA Nouvelles shared a link»
        
        			try:
					histoire = infos["story"]
				except:
					histoire = "?"

	# La variable lien contient l'URL lorsque le type de publication est un hyperlien
        
        			try:
					lien = infos["link"]
				except:
					lien = "?"

	# La variable statut est une description du type de publication
        
        			try:
					statut = infos["status_type"]
				except:
					statut = "?"

	# La variable letype contient le type de publication dont il s'agit (video, photo, lien, etc.)
        
        			try:
					letype = infos["type"]
				except:
					letype = "?"

	# La variable partage contient le nombre de partages pour cette publication
        
        			try:
					partages = infos["shares"]["count"]
				except:
					partages = 0

	# On crée une liste appelée «lepost» pour confiner toutes les informations relatives à la publication qu'on est en train de moissonner
        
        			lepost = []

				lepost.append(media["titre"])
				lepost.append(media["fbID"])
				lepost.append(n)

	# On enregistre deux dates pour chaque publication
        # la première est l'heure en temps universel (c'est ce qu'enregistre Facebook)
        # la seconde est cette même heure traduite en heure de l'Est
        
        			lepost.append(post["created_time"])
				dateUTC = datetime.strptime(post["created_time"], "%Y-%m-%dT%H:%M:%S%z")
				dateQC = dateUTC.astimezone(heureEst)
				lepost.append(datetime.strftime(dateQC, "%Y-%m-%dT%H:%M:%S%z"))

				lepost.append(post["id"])
				lepost.append(message)
				lepost.append(nom)
				lepost.append(description)
				lepost.append(vignette)
				lepost.append(histoire)
				lepost.append(source)
				lepost.append(lien)
				lepost.append(statut)
				lepost.append(letype)

				lepost.append(partages)
        
        # Ici, on va chercher l'ensemble des réactions possibles

				like = graph.get_object("{}?fields=reactions.type(LIKE).summary(1)".format(post["id"]))["reactions"]["summary"]["total_count"]
				love = graph.get_object("{}?fields=reactions.type(LOVE).summary(1)".format(post["id"]))["reactions"]["summary"]["total_count"]
				wow = graph.get_object("{}?fields=reactions.type(WOW).summary(1)".format(post["id"]))["reactions"]["summary"]["total_count"]
				haha = graph.get_object("{}?fields=reactions.type(HAHA).summary(1)".format(post["id"]))["reactions"]["summary"]["total_count"]
				angry = graph.get_object("{}?fields=reactions.type(ANGRY).summary(1)".format(post["id"]))["reactions"]["summary"]["total_count"]
				sad = graph.get_object("{}?fields=reactions.type(SAD).summary(1)".format(post["id"]))["reactions"]["summary"]["total_count"]
        
        # On en fait aussi la somme
        
				reactionsTotales = like + love + wow + haha + angry + sad
        
        # On confine ces nombres dans notre liste «lepost»
        
				lepost.append(reactionsTotales)
				lepost.append(like)
				lepost.append(love)
				lepost.append(wow)
				lepost.append(haha)
				lepost.append(angry)
				lepost.append(sad)
        
        # On va maintenant chercher les commentaires, ce qui est légèrement plus complexe

				commentairesTotaux = 0
				commentairesSurCommentaires = 0
				likesSurCommentaires = 0

				try:
					commentaires = graph.get_object("{}?fields=comments.limit(100){{comment_count,like_count}}".format(post["id"]))["comments"]["data"]
					for commentaire in commentaires:
						commentairesTotaux += 1
						commentairesSurCommentaires = commentairesSurCommentaires + commentaire["comment_count"]
						likesSurCommentaires = likesSurCommentaires + commentaire["like_count"]

	# S'il y a plus de 100 commentaires (nombre maximal qu'on peut obtenir par requête), il faut utiliser le code suivant pour aller chercher la suite 
          
          				if len(commentaires) > 99:
						# try:
						next = graph.get_object("{}?fields=comments.limit(100){{comment_count,like_count}}".format(post["id"]))["comments"]["paging"]["next"]
						print("               ------> Il y a plus de 100 commentaires!")
						commentaires = requests.get(next).json()

	# Tant qu'on obtient plus de 100 commentaires, on recommence
            
            					while(True):
							try:
								for commentaire in commentaires["data"]:
									commentairesTotaux += 1
									commentairesSurCommentaires = commentairesSurCommentaires + commentaire["comment_count"]
									likesSurCommentaires = likesSurCommentaires + commentaire["like_count"]

								commentaires = requests.get(commentaires["paging"]["next"]).json()

							except KeyError:
								ecritureCommentaires()
								break

					else:
						ecritureCommentaires()
				except:
					ecritureCommentaires()

	# Impression de nos résultats dans le terminal
        
        			print("~~"*40)
				print(lepost)

				# On enregistre nos données dans la base de données
        
        			with connection.cursor() as cursor:
				sql = """INSERT into posts (titre,fbID,num,dateUTC,dateQC,postID,message,nom,description,vignette,histoire,source,lien,statut,type,partages,reactions,likes,love,wow,haha,colere,tristesse,commentaires,likes_commentaires,commentaires_commentaires) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
				cursor.execute(sql,(lepost[0],lepost[1],lepost[2],lepost[3],lepost[4],lepost[5],lepost[6],lepost[7],lepost[8],lepost[9],lepost[10],lepost[11],lepost[12],lepost[13],lepost[14],lepost[15],lepost[16],lepost[17],lepost[18],lepost[19],lepost[20],lepost[21],lepost[22],lepost[23],lepost[24],lepost[25]))
				connection.commit()

	# Impression dans le terminal dans les cas où le média n'a rien publié ce jour-là
    
    		except KeyError:
			print("@"*80)
			print("AUCUN post publié par le média {} en ce jour d'aujourd'hui".format(media["titre"]))

# On termine en se déconnectant de la base de données

finally:
	connection.close()
