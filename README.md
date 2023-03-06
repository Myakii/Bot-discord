<h1 align="center">Discord Bot</h1>

<p>Projet scolaire réalisé en groupe en 1ère année de Développement Web à Hetic.</p>
<p>Délai du projet : 23/11/2022 jusqu'au 11/12/2022</p>
<p>Note du projet : 20/20</p>

<h2>
Contributeurs :
</h2>

<ul>
  <li><a href="https://github.com/OrBital1650">Lorys L.</a></li>
  <li><a href="https://github.com/LinelinLove">Chrisline L.</a></li>
  <li><a href="https://github.com/Myakii">Rosine Y.</a></li>
</ul>

## Sommaire

- [Consigne](#consigne)
  - [Fonctionnalités](#fonctionnalités-du-projet)
  - [Notation](#notation)
- [Technologies utilisées](#technologies-utilisées)
- [Fonctionnement du bot](#fonctionnement-du-bot)
  - [Dépendances](#dépendances)
  - [Modification à faire](#modification-à-faire)
  - [Commandes disponibles](#commandes-disponibles)


## Consigne

Le but de ce projet est de créer un bot discord pouvant être déployé sur un serveur et permettant de jouer une chasse au trésor sur le net. Le joueur voulant essayer la chasse pourra lancer le jeu via une commande. Une série d’énigmes lui sera ensuite posée. Chaque énigme lui demandera de chercher sur le web la réponse (soyez créatif). Il pourra à tout moment demander un indice pour l’aider dans sa recherche. Chaque question rapportera des points. S’il demande un indice, il marquera cependant moins de points. A la fin du quizz, un message lui donnant son nombre de points total sera affiché.


### Fonctionnalités du projet

Le bot doit pouvoir :
- Être lancé via une commande à tout moment
- Pouvoir poser une série de questions à l’utilisateur (au moins 5)
- Récupérer ses réponses et lui donner des points si la réponse est bonne
- Afficher un indice sur l’énigme courante si l’utilisateur le demande
- Afficher son score total lorsque toutes les énigmes ont été réalisées
- Faire une commande pour afficher son score actuel
- Faire une commande pour relancer le quizz depuis le début


### Notation

Le projet est à faire par équipe de 4 maximum et 2 minimum. Il sera noté sur 20 points, 14 points sur les commandes demandés ( si il en manque une ou deux vous n’aurez pas 0) et 6 points sur des fonctionnalités supplémentaires non spécifiées. Vous avez carte blanche pour trouver des idées qui permettraient d’améliorer ce jeu (dans les limites du respectable), vous pouvez par exemple essayer de rajouter un timer, des images, du son, des réponses à choix multiples, etc … Les points seront attribués en fonction de la complexité et du nombres de fonctionnalités rajoutées.


## Technologies utilisées

- [Python 3.10](https://docs.python.org/3.10/)
- [API Discord Py](https://discordpy.readthedocs.io/en/stable/)
- [API Discord Pycord](https://docs.pycord.dev/en/stable/)
- [API Open Weather Map](https://openweathermap.org/)


## Fonctionnement du bot


### Dépendances

Pour faire fonctionner le bot, installer au préalable sur votre machine ces dépendances :

```
!pip install discord.py
!pip install nest_asyncio 
!pip install discord_buttons_plugin
!pip install -U py-cord
!pip install youtube_dl
!pip install ffmpeg
!pip install pynacl
!pip install pycountry
```


### Modification à faire

- ligne 160, remplacer `id_channel` par l'ID du channel que vous souhaitez où le bot apparait.
- ligne 975, remplacer `'token_api` par votre token Open Weather Map
- la dernière ligne, remplacer `TOKEN` par le token de votre bot !


### Commandes disponibles

- `!avatar` : pour afficher votre avatar en grand
- `!cat` `!chat` : J'ai une belle galerie de chat à vous montrer, voulez-vous les voir ?
- `!dog` `!chien` : J'ai pu me documenter sur les chiens récemment, voulez-vous les voir ?
- `!greet` : pour me dire bonjour !
- `!gtn` `!guessthenumber` : pour deviner le chiffre !
- `!indice` : pour avoir des indices durant le jeu !
- `!invite` : n'hésitez pas à me proposer à vos amis avec la commande
- `!magicball votre question` `!8ball votre question` `!mb votre question`: si vous avez des questions sur votre avenir
- `!morpion` `!tictactoe` `!ttt` `!mp` : pour jouer au tic tac toe contre moi !
- `!poll "votre question"` : Vous avez besoin de l'avis d'autre utilisateur
- `!qcm `: si vous avez envie de jouer !
- `!slap <mention d'une personne>` `!s <mention d'une personne>` : si vous avez une envie de frapper quelqu'un
- `!tag` `!spam` `!t` `!sp` : pour spammer les gens !
- `!shifumi` `!sfm` `!pfc` `!pierrefeuilleciseaux` : pour jouer au pierre-feuille-ciseaux contre moi !
- `!vf` : si vous voulez jouer au vrai ou faux !
- `!weather "nom de ville"` `!w "nom de ville"` `!meteo "nom de ville"` `!m "nom de ville"` : pour avoir la météo en temps réel !

Les commandes pour la musique :

- `!join` : pour m'appeler, j'ai besoin d'un peu de préparation !
- `!play URLyoutube` : pour jouer le lien
- `!pause` : pour mettre en pause la vidéo actuelle
- `!resume` : pour reprendre la musique
- `!skip` : pour changer de lien youtube
- `!stop` : pour m'arrêter
- `!leave` : pour me déconnecter