<img src="img/LogoFacebook.png" width="100">

# facebook
### Étude sur les publications des médias du Québec et du Canada francophone dans Facebook (2013-2017)
-----

Cette étude comporte quatre volets:

- [Les faits saillants de 2013-2017](https://wp.me/p53tzW-Bi) (sur mon blogue)
- [La méthodologie détaillée de l'étude](https://wp.me/p53tzW-AF) (sur mon blogue)
- [Une analyse plus détaillée de 2017, incluant 4 palmarès](https://medium.com/@jeanhuguesroy/linformation-sur-facebook-en-2017-fd1c5aa79e8b) (sur Medium)
- [Les données brutes en format SQL](https://datahub.io/jhroy/facebook_2013-2017.sql) (sur Datahub)

Dans ce répertoire, vous trouverez également différents fichiers qui en ont permis la réalisation ou qui en sont issus.

Il y a un script python&nbsp;:

- **posts-daily-auto.py** : Le script déclenché chaque jour à minuit et qui récolte ce que les 101 médias ont publié sur Facebook 15 jours auparavant.

Et quelques fichiers CSV&nbsp;:

- **listemedias-301.csv** : La liste des pages Facebook des 301 médias qui ont été identifiés initialement
- **listemedias-top-101.csv** : La liste des pages Facebook des 101 médias qui font partie de l'étude
- **engagementParMedia.csv** :  Un résumé de l'engagement moyen par année et par média
- **engagementParType.csv** : Un résumé de l'engagement moyen par type de publication (sur les cinq ans)
- **engagementParJour.csv** : Un résumé de l'engagement moyen par jour de la semaine (sur les cinq ans)
- **engagementParHeure.csv** : Un résumé de l'engagement moyen par heure du jour (sur les cinq ans)

:+1: :+1: :+1:

=====

J'ai également ajouté un répertoire appelé **2015** pour mettre des documents relatifs à un projet de recherche élaboré en 2015-2015 et décrit dans [cette opinion publiée dans *La Presse+*](http://plus.lapresse.ca/screens/45d2ac30-8704-4dd7-91c9-f3bdf27469a0%7C_0.html). On y trouve essentiellement un [script ruby](https://github.com/jhroy/facebook/blob/master/2015/fb.rb) et [un exemple des données qu'il permettait d'extraire](https://github.com/jhroy/facebook/blob/master/2015/MattDugal.csv).
