#!/usr/bin/env ruby
# ©2015 Jean-Hugues Roy. GNU GPL v3.

require "json"
require "koala"
require "nokogiri"
require "open-uri"
require "open_uri_redirections"
require "csv"
require "google/api_client"
require "google_drive"

id = "xxx.apps.googleusercontent.com"
codeSecret = "xxx-xxx"
refreshToken = "1/xxx-xxx"

client = Google::APIClient.new(
  :application_name => 'FB',
  :application_version => '1.0.0'
)

auth = client.authorization
auth.client_id = id
auth.client_secret = codeSecret
auth.scope =
    "https://docs.google.com/feeds/ " +
    "https://docs.googleusercontent.com/ " +
    "https://spreadsheets.google.com/feeds/"

auth.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
auth.refresh_token = refreshToken
auth.refresh!
access_token = auth.access_token
session = GoogleDrive.login_with_oauth(access_token)

xl = session.spreadsheet_by_key("xxx").worksheets[0]

# puts "Il y a #{xl.num_rows-1} noms."

utilisateur = xl[xl.num_rows,2]

puts "Le dernier utilisateur s'appelle #{utilisateur}"

cle = xl[xl.num_rows,3]

# for row in 2..xl.num_rows
#     listeEnvoi.push xl[row,3]
# end

# cles = [
# "aksesstaukin"
# ]

fb = Koala::Facebook::API.new(cle)

r = fb.get_connections("me","?fields=home.limit(100)&locale=fr_CA")
# puts fb.get_connection('search', type: :place)
# fb.put_wall_post("Test avec Koala")

r=r.to_json

puts r

File.open("#{utilisateur}.json","w") do |f|
	f.write(r)
end

# fichier1 = "#{utilisateur}.json"
# source1 = "#{utilisateur}.txt"

# n = 0
# ligne1 = 0
# ligne2 = 0

# File.readlines(source1).each do |ligne|
# 	n += 1
# 	if ligne[1] == "\n"
# 		puts n.to_s + " : " + ligne.size.to_s + " : " + ligne
# 		if ligne1 == 0
# 			ligne1 = n
# 		else
# 			ligne2 = n
# 		end 
# 	end
# end
# puts "On extrait de la ligne #{ligne1} à la ligne #{ligne2}"

# File.readlines(source)[ligne1-1..ligne2-1].each do |linea|
# 	# puts linea
# 	l = linea.to_s.gsub(/\u00A0\u00A0/, "\t")
# 	# puts l
# 	File.open(fichier,"a") do |f|
# 		f.write(l)
# 	end
# end

# puts "Nom de fichier?"

# source = gets.chomp

fichier = "#{utilisateur}.csv"
source = "#{utilisateur}.json"

f = File.read(source)

p = JSON.parse(f)

p = p["home"]
data = p["data"]
# u = p["paging"].to_h
# u = u["previous"]
# u = u[32..-1]
# numFB = u[0..u.index("/")-1]

# puts numFB

medias = {
	"radio-canada.ca" => "Radio-Canada",
	"icimusique.ca" => "Radio-Canada",
	"cbc.ca" => "CBC",
	"lapresse.ca" => "La Presse",
	"ledevoir.com" => "Le Devoir",
	"huffingtonpost.com" => "Huffington Post",
	"huffingtonpost.ca" => "Huffington Post",
	"journaldequebec.com" => "Journal de Québec",
	"journaldemontreal.com" => "Journal de Montréal",
	"tvanouvelles.com" => "TVA",
	"tvanouvelles.ca" => "TVA",
	"lemonde.fr" => "Le Monde",
	"lefigaro.fr" => "Le Figaro",
	"lepoint.fr" => "Le Point",
	"rds.ca" => "RDS",
	"nytimes.com" => "New York Times",
	"theglobeandmail.com" => "The Globe and mail",
	"thestar.com" => "Toronto Star",
	"urbania.ca" => "Urbania",
	"journalmetro.com" => "Métro",
	"courrierinternational.com" => "Courrier International",
	"rfi.my" => "Radio-France Internationale",
	"globalnews.ca" => "Global News",
	"voir.ca" => "Voir",
	"chatelaine.com" => "Châtelaine",
	"businessinsider.com" => "Business Insider",
	"rue89.nouvelobs.com" => "Nouvel Observateur",
	"independent.co.uk" => "The Independent",
	"bbc.co.uk" => "BBC",
	"nationalpost.com" => "National Post",
	"wired.com" => "Wired",
	"pagina12.com.ar" => "Pagina 12"
}

# f = Nokogiri::HTML(open("http://www.facebook.com/" + numFB, :allow_redirections => :safe))

# utilisateur = f.css("title").text.strip

# puts utilisateur

tout = []

# fb["Utilisateur"] = utilisateur

data.each do |item|
	fb = {}
	# fb["Numero d'utilisateur"] = numFB
	item = item.to_h
	# puts item.size

	if item.has_key?("from")
		qui = item["from"].to_h
		fb["Contact"] = qui["name"]
		if qui.has_key?("category")
			fb["Categorie"] = qui["category"]
		else
			fb["Categorie"] = ""
		end
	else
		fb["Contact"] = ""
	end

	if item.has_key?("story")
		fb["Story"] = item["story"]
	else
		fb["Story"] = ""
	end

	if item.has_key?("message")
		fb["Message"] = item["message"]
	else
		fb["Message"] = ""
	end

	if item.has_key?("link")
		fb["Lien"] = item["link"]
		# puts item["link"][0..6]
		if item["link"][0..6] == "http://"
			site = item["link"][7..-1]
			site = site[0..site.index("/")-1]
			# puts site
			fb["Site"] = site
		elsif item["link"][0..7] == "https://"
			site = item["link"][8..-1]
			site = site[0..site.index("/")-1]
			# puts site
			fb["Site"] = site
		else
			fb["Site"] = ""
		end
	else
		fb["Lien"] = ""
		fb["Site"] = ""
	end

	if fb["Site"] != ""
		s = fb["Site"]

		if s[-4..-1] == "t.co" || s[-11..-1] == "youtube.com" || s[-12..-1] == "facebook.com" || s[-9..-1] == "vimeo.com" || s[-14..-1] == "soundcloud.com" || s[-6..-1] == "bit.ly"
			social = Nokogiri::HTML(open(item["link"], :allow_redirections => :safe))
			titre = social.css("title")
			t = titre.text
			if t.include?("adio-Canada") || t.include?("ICI ")
				fb["Media"] = "Radio-Canada"
			elsif t.include?("CBC")
				fb["Media"] = "CBC"
			elsif t.include?("Protégez")
				fb["Media"] = "Protégez-Vous"
			elsif t.include?("Huffington")
				fb["Media"] = "Huffington Post"
			else
				fb["Media"] = ""
			end
		else
			fb["Media"] = ""
		end
		medias.each do |urlMedia, nomMedia|
			if s[-(urlMedia.size)..-1] == urlMedia
				fb["Media"] = nomMedia
			end
		end
	else
		fb["Media"] = ""
	end

	if fb["Categorie"].include?("ews")
		fb["Media"] = fb["Contact"]
		if fb["Media"].include?("adio-Canada")
			fb["Media"] = "Radio-Canada"
		elsif fb["Media"].include?("Huffington")
			fb["Media"] = "Huffington Post"
		end
	end

	puts fb["Media"]

	if item.has_key?("name")
		fb["Titre"] = item["name"]
	else
		fb["Titre"] = ""
	end	

	if item.has_key?("caption")
		fb["Legende"] = item["caption"]
	else
		fb["Legende"] = ""
	end	

	if item.has_key?("description")
		fb["Description"] = item["description"]
	else
		fb["Description"] = ""
	end

	if item.has_key?("type")
		fb["Type"] = item["type"]
	else
		fb["type"] = ""
	end

	if item.has_key?("likes")
		jaime = item["likes"].to_h
		fb["Jaime"] = jaime["data"].size
	else
		fb["Jaime"] = 0
	end

	if item.has_key?("comments")
		commentaires = item["comments"].to_h
		fb["Commentaires"] = commentaires["data"].size
	else
		fb["Commentaires"] = 0
	end

	if item.has_key?("shares")
		partages = item["shares"].to_h
		fb["Partages"] = partages["count"]
	else
		fb["Partages"] = 0
	end

	tout.push fb
end

CSV.open(fichier, "wb") do |csv|
	csv << tout.first.keys
	tout.each do |hash|
		csv << hash.values
	end
end
