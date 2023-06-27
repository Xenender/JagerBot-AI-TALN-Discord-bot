# JagerBot-IA-TALN-Discord-bot

JägerBot est un chat-bot discord. Il a été développé en collaboration avec le LIRMM (Laboratoire d'informatique, de robotique et de microélectronique de Montpellier)
Il s'agit d'un bot dont le but est de répondre à des questions simple posées en **FRANCAIS**

"un manchot peut il voler ?"
"un chien peut il manger de la viande ?"

vous pouvez également demander des explications sur la réponse qui a été donnée:
"pourquoi un manchot peut il voler ?"

## Comment fonctionne t-il ?

JägerBot fonctionne grâce à la base de connaissance <a href="https://www.jeuxdemots.org/jdm-accueil.php">JeuxDeMots</a>.
Pour résumer très simplement, JägerBot va essayer de comprendre la relation qui lie les mots de la question.
Après avoir trouvé la ou les relations cherchés, JägerBot va trouver les mots clés de la phrase et effectuer une requete express à jeuxDeMots pour chaque mot clés,
un traitement sera alors effectué pour rassembler toutes les relations existentes entre les mots clés, si la relation recherchée existe alors la question est considérée comme vraie.
JägerBot va travailler avec une profondeur de 4, c'est à dire que pour chaque mots clés il va chercher les relations "générique" et "hypo" (et ainsi dessuite sur les nouveaux mots 4 fois) et effectuer à nouveau le travail pour trouver ou non la relation recherchée.

## Comment l'utiliser ?

    -Créer un bot discord.
    
    -L'inviter sur votre serveur.
    
    -Télécharger le fichier zip du projet.
    
    -Ouvrir le fichier jagerbot.py et modifier la variable "TOKEN" en mettant le token de votre bot.
    
    -Modifier également la variable "PATH" en mettant le chemin absolu jusqu'au dossier contenant le programme jagerbot.py.
    
    -Télécharger si besoin les bibliothèques python necessaires au fonctionnement du programme.

    -Exécuter le fichier python "jagerbot.py".
    
    -Le bot va se connecter sur le serveur, vous pouvez commencer à discuter, faites !help pour connaitre les commandes de base.

