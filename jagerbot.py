import discord
from discord.ext import commands
import request_mot
import os
import time
import shutil
import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


TOKEN = "YOUR TOKEN"#TO CHANGE
PATH = "PATH OF THE MAIN DIRECTORY OF THE PROJECT" #TO CHANGE


COMMAND_PREFIX = ''
DESCRIPTION = "Shinzou wo sasageyo"



MESSAGE = ""

POURQUOI = False

NEGATION = False

EN_REPONSE = False

RAFFINEMENT = False

tableauExplication = []
moyennePoidNodes = 10
moyennePoidRelEntrante = 10
moyennePoidRelSortante = 10

userIDS = []


profondeurMax = 3


intents = discord.Intents.default()  # Créer un objet Intents avec les intentions par défaut
intents.typing = True  # Désactiver l'intention de "typing"
intents.presences = False  # Désactiver l'intention de "presences"

intents.members = True # Activation de l'intention de contenu de message privilégié
intents.message_content = True  # Ajouter l'intention du contenu du message

def launch():

    bot = commands.Bot(command_prefix=COMMAND_PREFIX,description=DESCRIPTION,intents=intents)



    @bot.event
    async def on_ready():
        print("ready")
        activity = discord.Activity(type=discord.ActivityType.listening, name="!help")
        await bot.change_presence(activity=activity)
        bot.description = DESCRIPTION


    @bot.event
    async def on_message(message):

        global userIDS
        global profondeurMax
        global MESSAGE
        global POURQUOI
        global tableauExplication
        global NEGATION
        global EN_REPONSE
        global RAFFINEMENT
      
        
        


        if message.author == bot.user:
            return ""
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        if(user_message == "!start"):
            async with message.channel.typing():
                userIDS.append(message.author.id)
                await message.channel.send("Bot démarré, vous pouvez commencer à discuter !")

        elif(user_message == "!stop"):
            async with message.channel.typing():
                userIDS.remove(message.author.id)
                await message.channel.send("À la prochaine !")

        elif(user_message == "!raffinement_on"):
            RAFFINEMENT = True
        elif(user_message == "!raffinement_off"):
            RAFFINEMENT = False
        elif(user_message == "!help"):
            embed = discord.Embed(title="Menu d'Aide", description="Voici les commandes disponibles :", color=discord.Color.blue())
            embed.add_field(name="!help", value="Afficher le menu d'aide", inline=False)
            embed.add_field(name="!start", value="Lancement du bot, vous pourrez ensuite parler avec lui depuis n'importe quel channel", inline=False)
            embed.add_field(name="!stop", value="Stopper le bot pour qu'il ne vous réponde plus", inline=False)
            embed.add_field(name="!raffinement_on", value="Activer le mode 'raffinement sémantique', ce mode permet de lever l'ambiguité sur des mots. \n il vous demandera de spécifier parmis une selection de sens celui de votre mot (exemple: voler -> voler>déplacement aérien ou voler>malhonnêteté.\n si spécifier le sens d'un mot ne vous semble pas OBLIGATOIRE à la compréhension alors choisissez l'option: sens générique.)", inline=False)
            embed.add_field(name="!raffinement_off", value="Stopper mode 'raffinement sémantique'", inline=False)
            embed.set_footer(text="développé par @Xenender")
            await message.channel.send(embed=embed) 








        else:#tous les autres messages
            if(message.author.id in userIDS):#l'utilisateur a lancé le bot
                async with message.channel.typing():

                    if(EN_REPONSE == False):
                        EN_REPONSE = True

                        profondeurActu = 0
                        MESSAGE = message

                        premierMSGLIST = None

                        PREMIER_USER_MESSAGE = user_message.lower()

                        user_message = user_message.lower()

                        


                        #tester si c'est une negation
                        if(("n'" in user_message or " ne " in user_message) or " pas " in user_message):
                            user_message = user_message.replace("n'","")
                            user_message = user_message.replace("d'","")
                            NEGATION = True
                        else:
                            NEGATION = False
                            
                            


                        #tester si c'est une demande d'explications:
                        if("pourquoi" in user_message):
                            user_message = user_message.replace("pourquoi","")
                            POURQUOI = True
                            profondeurMax = 4
                        else:
                            POURQUOI = False
                            profondeurMax = 4



                        #mots clés de la phrase
                        #tester plusieurs sens aux mots:
                        
                        keywordsKw = extract_keywords(user_message)




                        


                        if("r_" in user_message):#relation donnée
                            TabmessageRelationCherche = replaceRelation(user_message)
                            phrase = supprimer_mots_dollars(TabmessageRelationCherche)[0]

                            print(phrase)

                            print("cheche")
                            print(TabmessageRelationCherche)
                        
                    
                        else:

                        #trouver la relation qu'on cherche  SUR PHRASE ENTIERE
                            tabRelationCherche,phrase,TabmessageRelationCherche = findRelationCherche(user_message)

                            
                        

                        print("phrase d'entrée:")
                        print(TabmessageRelationCherche)
                    

                        newTabRel = []
                        for mes in TabmessageRelationCherche:#key world des phrases relations
                    
                            keywordsKw = extract_keywords(mes)
                        
                            phraseKw = " ".join(keywordsKw)
                        
                            newTabRel.append(phraseKw)

                
                        TabmessageRelationCherche = newTabRel
                        

                        keywords = extract_keywords(phrase)
                
                        phrase = " ".join(keywords)
                    

                        print(phrase)

                        #on fait l'appel seulement avec les mots clés
                
                        nombreMotsPhrase = len(splitAcolades(phrase))
                        msgList = traitementMessage(phrase)


                        #######################################RAFFinement semantique
                        if(RAFFINEMENT):
                        
                            def check(mes):
                                return mes.author == message.author and mes.channel == message.channel

                            newDicoRAf = {}
                            dicoRaf = findRaffinementSemantique(phrase)
                            for mot,raf in dicoRaf.items():
                                newDicoRAf[mot] = None
                                if(raf != []):
                                    await message.channel.send("Plusieurs sens ont été détectés pour le mot: "+mot)
                                    await message.channel.send("veuillez en choisir en tapant son numéro")
                                    for i in range(len(raf)):
                                        await message.channel.send("("+str(i)+") "+raf[i][0])
                                    
                                    await message.channel.send("("+str(len(raf))+") sens générique")
                                    try:
                                        mes = await bot.wait_for('message', check=check, timeout=60)  # Attendre 60 secondes maximum
                                        await message.channel.send(f"vous avez choisi: {mes.content}")


                                        #TODO VERIFICATION DE LA REPONSE: int compris entre les propositions
                                        try:
                                            newDicoRAf[mot] = raf[int(mes.content)][1]
                                        except IndexError:#ON NE CHANGE RIEN
                                            newDicoRAf[mot] = mot
                                    except:
                                        await message.channel.send("Temps écoulé. Aucun message reçu.")

                            print("dico raffinemnt")
                            print(newDicoRAf)

                            #ON REMPLACE LES MOTS PAR LES NOUVEAUX ET ON REFAIT LA PREMIERE ETAPE AVANT ça 
                            #ON REMPLACE LES MOTS PAR LES NOUVEAUX ET ON REFAIT LA PREMIERE ETAPE AVANT ça
                            user_message = PREMIER_USER_MESSAGE
                            for mot,value in newDicoRAf.items():
                                if(value == None):
                                    value = mot
                                user_message = user_message.replace(mot,value)


                            #ON RECMMENCE LE TOUT DEBUT AVEC LA NOUVELLE PHRASE


                                                #tester si c'est une negation
                            if(("n'" in user_message or " ne " in user_message) or " pas " in user_message):
                                user_message = user_message.replace("n'","")
                                user_message = user_message.replace("d'","")
                                NEGATION = True
                            else:
                                NEGATION = False
                                


                            #tester si c'est une demande d'explications:
                            if("pourquoi" in user_message):
                                user_message = user_message.replace("pourquoi","")
                                POURQUOI = True
                                profondeurMax = 4
                            else:
                                POURQUOI = False
                                profondeurMax = 4



                            #mots clés de la phrase
                            #tester plusieurs sens aux mots:
                            
                            keywordsKw = extract_keywords(user_message)




                            


                            if("r_" in user_message):#relation donnée
                                TabmessageRelationCherche = replaceRelation(user_message)
                                phrase = supprimer_mots_dollars(TabmessageRelationCherche)[0]

                                print(phrase)

                                print("cheche")
                                print(TabmessageRelationCherche)
                            
                        
                            else:

                            #trouver la relation qu'on cherche  SUR PHRASE ENTIERE
                                tabRelationCherche,phrase,TabmessageRelationCherche = findRelationCherche(user_message)

                                
                            

                            print("phrase d'entrée:")
                            print(TabmessageRelationCherche)
                            print("la phrase!")
                            print(phrase)
                        

                            newTabRel = []
                            for mes in TabmessageRelationCherche:#key world des phrases relations
                        
                                keywordsKw = extract_keywords(mes)
                            
                                phraseKw = " ".join(keywordsKw)
                            
                                newTabRel.append(phraseKw)

                    
                            TabmessageRelationCherche = newTabRel
                            

                            keywords = extract_keywords(phrase)
                    
                            phrase = " ".join(keywords)
                        
                            print("la phrase 222")
                            print(phrase)

                            #on fait l'appel seulement avec les mots clés
                    
                            nombreMotsPhrase = len(splitAcolades(phrase))
                            msgList = traitementMessage(phrase)                   




                        #FIN DU RECMMENCEMENT DU DEBUT




                    
                    
                        premierMSGLIST = msgList
                    
                    
                        tabChainePoid = []

                        tabRelEntrante,tabRelSortante,tabchaine,tabChainePoid = findRelation(msgList)#trouve toutes les relations possibles entre les mots
                        if(tabchaine == None):
                            await on_message(MESSAGE)
                            return ""

                        #on prend les mots clés des chaines calculés

                        newTabRelTrouve = []
                        for mes in tabchaine:#key world des phrases relations
                    
                            keywordsKw = extract_keywords(mes)
                        
                            phraseKw = " ".join(keywordsKw)
                        
                            newTabRelTrouve.append(phraseKw)

                
                        tabchaine = newTabRelTrouve


                        #les relations cherche devrons obligatoirement contenir les mêmes mots que dans celle trouvé, on stocke les mots qui ne sont pas liés aux autres

                        motsNonliés = []
                        # tousLesMots = mots_uniques(tabchaine)
                        # for e in TabmessageRelationCherche:
                        #     sp1 = e.split()
                        #     for e1 in sp1:#chaque mots de relation cherche
                                
                        #         if(not(e1.startswith("$")) and (not(e1 in tousLesMots))):#si le mot commence pas par $ et n'est pas dans les rel trouvés
                        #             #alors on le stocke
                        #             motsNonliés.append(e1)


                        #PEUT ETRE ????? on supprime les mots non liés ???????
                
                        motsNonliés = supprimer_doublons(motsNonliés)
                

                        nt=[]
                        for mes in TabmessageRelationCherche:
                            mes = supprimer_mots_phrase(mes,motsNonliés)
                            nt.append(mes)
                        TabmessageRelationCherche = nt



                        tabChaineNoChange = [x for x in tabchaine]
                
                        tab2 = [x for x in tabchaine]

            
                        for i in range(nombreMotsPhrase-2-len(motsNonliés)):

                            tab2 = ajoute_mot_phrase_algebre(tab2,tabChaineNoChange)
                            tab2 = supprimer_doublons(tab2)
                        
                        tabchaine = tab2

            



                        print("cherche")
                        print(TabmessageRelationCherche)

            
                        reponse = False
                        reltrouve = ""
                        reponsePoidNegBool = False
                        reponsePoidNeg = ""
        
                        #await message.channel.send(username + " a dit: "+user_message+" ("+channel+")")
                        for c in tabchaine:
                            for cherche in TabmessageRelationCherche:
                            
                                if(c == cherche):
                                    reponse = True
                                    reltrouve = c
                                    #on stocke pour l'explication :
                                    
                                    #TEST POID NEGATIF
                                    poidR = int(tabChainePoid[c])
                                    if(poidR < 0):
                                        reponsePoidNegBool = True
                                        reponsePoidNeg = c

                                    #si c contient un raffinement, on le supprime

                                    newC = ""
                                    
                                    sp = splitAcolades(c)
                                    for mot in sp:
                                        if(">" in mot):
                                            mot = mot.split(">")[0]

                                        newC = newC + mot +" "
                                    newC =newC.strip()

                                

                            

                                    if not(contain_first_element_liste_tuple(tableauExplication,newC)):

                                        tableauExplication.append((newC,profondeurActu,tabChainePoid[c]))

                        
                        precedenteRelationCherche = [x for x in TabmessageRelationCherche]

                        if(reponse and not POURQUOI):
                            
                            if(reponsePoidNegBool):
                                if(NEGATION):
                                    await message.channel.send("C'est JUSTE parce que:")
                                else:
                                    await message.channel.send("C'est FAUX parce que:")
                                
                                await message.channel.send(replace_dollars_par_sa_relation(reponsePoidNeg+" est une relation FAUSSE"))
                                    
                            else:
                                
                                if(NEGATION):
                                    await message.channel.send("C'est FAUX parce que:")
                                else:

                                    await message.channel.send("C'est JUSTE parce que:")

                                await message.channel.send(replace_dollars_par_sa_relation(reltrouve))



                            tableauExplication = []
                            POURQUOI = False
                            NEGATION=False
                            EN_REPONSE = False
                            return ""
                            


                        else:#profondeur 1

                            msgListAvecIndice = None

                            while(profondeurActu < profondeurMax):
                                
                            
                                newIsACherche,newHypoCherche,msgListAvecIndice = trouverLesNouvellesRelations(msgList,TabmessageRelationCherche,msgListAvecIndice)

                            
                                newIsACherche = list(set(newIsACherche))
                                newHypoCherche = list(set(newHypoCherche))#SUPPRIMER DOUBLONS
                                
                    
                        
                                newIsAKeyword = supprimer_mots_dollars(newIsACherche)
                                newHypoKeyword = supprimer_mots_dollars(newHypoCherche)

                            
                            
                                #appel comme dans le if

                                phrase = " ".join(newIsAKeyword)

                                
                            
                                msgList = traitementMessage(phrase)
                                msgList = list(set(msgList))

            

                            
                            
                                tabRelEntrante,tabRelSortante,tabchaine,tabChainePoid = findRelation(msgList)
                        
                                if(tabchaine == None):
                                    await on_message(message)
                                    return ""

                                tabchaine = list(set(tabchaine))

                                reponse = False
                                reltrouve =""

                                #transformation tabchaine

                                tabChaineNoChange = [x for x in tabchaine]
                
                                tab2 = [x for x in tabchaine]

                        
                                for i in range(nombreMotsPhrase-2-len(motsNonliés)):

                                    tab2 = ajoute_mot_phrase_algebre(tab2,tabChaineNoChange)
                                    tab2 = supprimer_doublons(tab2)
                                
                                tabchaine = tab2


                                ###
                                reponsePoidNegBool=False
                                reponsePoidNeg = ""

                                print("cherche2")
                                print(newIsACherche)
                            
                                for c in tabchaine:
                                    for cherche in newIsACherche:

                                        
                                        

                                    
                                        if(c == cherche):
                                            reponse = True
                                            reltrouve = c
                                            newC = ""


                                            #TEST POID NEGATIF
                                            poidR = int(tabChainePoid[c])
                                            if(poidR < 0):
                                                reponsePoidNegBool = True
                                                reponsePoidNeg = c

                                    
                                            sp = splitAcolades(c)
                                            for mot in sp:
                                                if(">" in mot):
                                                    mot = mot.split(">")[0]

                                                newC = newC + mot +" "
                                            newC =newC.strip()

                                    
                                    

                                            if not(contain_first_element_liste_tuple(tableauExplication,newC)):

                                                tableauExplication.append((newC,profondeurActu+1,tabChainePoid[c]))

                                if(reponse and not POURQUOI):

                                    if(reponsePoidNegBool):
                                        if(NEGATION):
                                            await message.channel.send("C'est JUSTE parce que:")
                                        else:
                                            await message.channel.send("C'est FAUX parce que:")
                                        
                                        await message.channel.send(replace_dollars_par_sa_relation(reponsePoidNeg+" est une relation FAUSSE"))
                                            
                                    else:
                                        
                                        if(NEGATION):
                                            await message.channel.send("C'est FAUX parce que:")
                                        else:

                                            await message.channel.send("C'est JUSTE parce que:")

                                        await message.channel.send(replace_dollars_par_sa_relation(reltrouve))
                                    
                                    tableauExplication = []
                                    POURQUOI = False
                                    NEGATION = False
                                    EN_REPONSE = False
                                    return ""

                                else:#cas hypo

                                    phrase = " ".join(newHypoKeyword)
                                    msgList = traitementMessage(phrase)
                                    tabRelEntrante,tabRelSortante,tabchaine,tabChainePoid = findRelation(msgList)
                                    if(tabchaine == None):
                                        await on_message(message)
                                        return ""
                                    #transformation tabchaine

                                    tabChaineNoChange = [x for x in tabchaine]
                    
                                    tab2 = [x for x in tabchaine]

                    
                                    for i in range(nombreMotsPhrase-2-len(motsNonliés)):

                                        tab2 = ajoute_mot_phrase_algebre(tab2,tabChaineNoChange)
                                        tab2 = supprimer_doublons(tab2)
                                    
                                    tabchaine = tab2


                                    ###


                                    


                                    reponse = False
                                    reltrouve =""
                                
                                    for c in tabchaine:
                                        for cherche in newHypoCherche:
                                        
                                            if(c == cherche):
                                                reponse = True
                                                reltrouve = c
                                                newC = ""


                                                #TEST POID NEGATIF
                                                poidR = int(tabChainePoid[c])
                                                if(poidR < 0):
                                                    reponsePoidNegBool = True
                                                    reponsePoidNeg = c

                                    
                                                sp = splitAcolades(c)
                                                for mot in sp:
                                                    if(">" in mot):
                                                        mot = mot.split(">")[0]

                                                    newC = newC + mot +" "
                                                newC =newC.strip()

                                        
                                        
                                                if not(contain_first_element_liste_tuple(tableauExplication,newC)):

                                                    tableauExplication.append((newC,profondeurActu+1,tabChainePoid[c]))

                                    if(reponse and not POURQUOI):

                                        if(reponsePoidNegBool):
                                            if(NEGATION):
                                                await message.channel.send("C'est JUSTE parce que:")
                                            else:
                                                await message.channel.send("C'est FAUX parce que:")
                                            
                                            await message.channel.send(replace_dollars_par_sa_relation(reponsePoidNeg+" est une relation FAUSSE"))
                                                
                                        else:
                                            
                                            if(NEGATION):
                                                await message.channel.send("C'est FAUX parce que:")
                                            else:

                                                await message.channel.send("C'est JUSTE parce que:")

                                            await message.channel.send(replace_dollars_par_sa_relation(reltrouve))



                                        tableauExplication = []
                                        POURQUOI = False
                                        NEGATION = False
                                        EN_REPONSE = False
                                        return ""
                                    else:
                                    
                                    

                                        newIsACherche = [x for x in newIsACherche] #if not x in precedenteRelationCherche]
                                        newHypoCherche = [x for x in newHypoCherche] #if not x in precedenteRelationCherche]
                                        precedenteRelationCherche = newIsACherche + newHypoCherche

                                        newMsgList = []
                                        for e in supprimer_mots_dollars(newIsACherche):
                                            sp = splitAcolades(e)
                                            for el in sp:
                                                if not el in newMsgList:
                                                    newMsgList.append(el)

                                        msgList = newMsgList
                                        TabmessageRelationCherche = precedenteRelationCherche
                                        print("ça repart pour un tour")
                                        print("pronf actu "+str(profondeurActu))
                                    
                                        print("___________________________________________________________________________________________________")


                                        #ON VA REPARTIR POUR UN TOUR 
                                
                                profondeurActu +=1



                            if(tableauExplication != [] and not NEGATION):
                                tableauMotLiaison=["Je suis convaincu que la phrase est vraie grâce à mes connaissances: ","En réfléchissant un peu j'ai trouvé que ","Si je pousse la réflexion très loin ","Pour finir ","En fait j'ai encore un truc: ","Et au cas ou: ","Pour etre sur: "]
                                indiceTableauLiaison=-1
                                tabDejaPrint = []
                                # await message.channel.send("La relation parait vraie car:")
                                tableauExplication = list(set(tableauExplication))
                                tableauExplication = trier_tableauExplication(tableauExplication)#tabexplication : ["rel",profondeur,poid]
                                for e in tableauExplication:

                                    if(e[1] != indiceTableauLiaison):
                                            
                                        indiceTableauLiaison = e[1]
                                        await message.channel.send(tableauMotLiaison[indiceTableauLiaison])

                                    
                                    newE=e[0]
                                    if(">" in e[0]):
                                        newE = ""
                                        
                                        sp = splitAcolades(e[0])
                                        for mot in sp:
                                            if(">" in mot):
                                                mot = mot.split(">")[0]

                                            newE = newE + mot +" "
                                        
                                    newE = newE.strip()
                                    if not newE in tabDejaPrint:
                                        tabDejaPrint.append(newE)

                                        #RRRRRRRRRRRRRRRRRRRR
                                        if(e[1] != 0):#il y a eu un isa/autre
                                            lanewphrase=""
                                            laphrase= newE
                                            phrasesplit=splitAcolades(laphrase)
                                            nbDollars = 0

                                            for ee in range(len(phrasesplit)):
                                                if not(phrasesplit[ee].startswith("$")) and (phrasesplit[ee] != premierMSGLIST[ee-nbDollars]):
                                                    lanewphrase = lanewphrase + phrasesplit[ee]+"(provient de "+premierMSGLIST[ee-nbDollars]+") "
                                                else:
                                                    if((phrasesplit[ee].startswith("$"))):
                                                        nbDollars+=1

                                                    lanewphrase = lanewphrase + phrasesplit[ee]+" "
                                            lanewphrase.strip()

                                            if(e[2]<0):
                                                lanewphrase = lanewphrase + " -> EST UNE RELATION FAUSSE"
                                            await message.channel.send("-"+(replace_dollars_par_sa_relation(lanewphrase)))
                                        else:
                                            if(e[2]<0):
                                                newE = newE + " -> EST UNE RELATION FAUSSE"
                                            await message.channel.send("-"+(replace_dollars_par_sa_relation(newE)))
                                
                                
                                tableauExplication = []
                                POURQUOI = False
                                NEGATION = False 
                                EN_REPONSE = False
                                return ""
                            else:
                                if(NEGATION):
                                    await message.channel.send("C'est JUSTE !")
                                else:

                                    await message.channel.send("C'est FAUX !")
                            
                                tableauExplication = []
                                POURQUOI = False
                                NEGATION = False
                                EN_REPONSE = False
                                return ""


                    


    def trier_tableauExplication(tableau):
        tableau_trie = sorted(tableau, key=lambda x: (x[1], -x[2]))
        return tableau_trie



    def traitementMessage(message): #prend en param: une phrase constituée de mots clés et pour chaque mot de la phrase va creer un directory et le remplir avec la bdd jeu de mots
                                    #out: renvoie les mots de la phrase d'entrée sous forme de liste
        os.chdir(PATH+"DONNEES")

        dossiersDonnees = os.listdir()

        msg = message.strip()
        msgList = splitAcolades(msg)

    
        

        for mot in msgList:
            dossiersDonnees = os.listdir()
            print("LE MOT")
            print(mot)
            if(not(mot in dossiersDonnees) and(mot != "")):
                #creation d'un dossier avec ce nom et remplissage avec une requette à jeuxdemots
                
           
                os.mkdir(mot)#creer un dossier
                os.chdir(mot)#se deplacer dedans

                print("CREATIION DIR:")
                print(mot)

                request_mot.doRequest(mot)# les { et } sont supprimés lors de la requete du mot
                
                time.sleep(2)
                os.chdir("..")#revenir

        os.chdir("..")
    

        return msgList


    def findRelation(lstMot):#prend en entrée une liste de mot d'une phrase (mots clés)
        tabListeRelations = [-1,-1]
        tabLstMots = [lstMot,inverser_tableau(lstMot)]

        for p in range(2):

            lstMot = tabLstMots[p]


            os.chdir(PATH+"DONNEES")
            listeRelation = {}
            if(len(lstMot)>1):
                for i in range(len(lstMot)):
                    listeRelation[lstMot[i]]= [[],[]] #mot:[[relEntrantes],[relSortantes]]
                    lstNodesID = []
                
                    os.chdir(lstMot[i])

                    for j in range(i+1,len(lstMot)):
                        
                        try:
                        
                            with open("nodes.txt",'r') as file:
                                for line in file:
                                    try:
                                        if(line):
                                            #traiter la ligne:
                                            ligne = str(line)
                                            ligne = ligne.replace("'","")
                                            ligne = ligne.strip()
                                            ligne = ligne.split(";")
                                        
                                        
                                            if((lstMot[j] == (ligne[2]).lower()) and (int(ligne[4]) >= moyennePoidNodes)):#on a peut etre une relation: on stocke l'id : ligne[1]
                                                
                                                lstNodesID.append((ligne[1],ligne[2].lower())) #id et nom
                                                
                                    except:
                                        continue
                        except FileNotFoundError:
                            os.chdir("..")
                            #delete repertory
                            shutil.rmtree(lstMot[i])
                            #tout recommencer
                            return None,None,None

                        
                
                    #à partir de là on a toutes les nodes en fonction des mots de la phrase
                    #on cherche une relation avec la liste des nodes
        
                    try:
                        remplirListeRelation(lstNodesID,listeRelation,lstMot,i)
                    except FileNotFoundError:
                            os.chdir("..")
                            #delete repertory
                            shutil.rmtree(lstMot[i])
                            #tout recommencer
                         
                            return None,None,None

                    os.chdir("..")




            os.chdir("..")
        
        

            tabListeRelations[p] = listeRelation
        
        #concatener les deux listeRelations

        resListeRelation = regrouper_dictionnaires(tabListeRelations[0],tabListeRelations[1])
    

        return findTypeRelation(resListeRelation)


    def remplirListeRelation(lstNodesID,listeRelation,lstMot,i):
        

        with open("relation_entrantes.txt",'r') as file:
            
            for line in file:
                try:
                    ligne = str(line)
                    ligne = ligne.replace("'","")
                    ligne = ligne.strip()
                    ligne = ligne.split(";")
                    
                
                    for x in lstNodesID:
                    
                        if((ligne[2] == x[0]) and ((int(ligne[5])>=moyennePoidRelEntrante) or (int(ligne[5])<0))):#il y a une relation: si le poid est superieur à la borne ou que le poid est negatif
                            listeRelation[lstMot[i]][0].append((ligne[2].lower(),ligne[4],ligne[5],x[1]))#on stocke le type de relation, le poid et le nom

                        

                except:
                    continue


        with open("relation_sortantes.txt",'r') as file:
            for line in file:
                try:
                    ligne = str(line)
                    ligne = ligne.replace("'","")
                    ligne = ligne.strip()
                    ligne = ligne.split(";")
                    
                    for x in lstNodesID:
                        
                        if((ligne[3] == x[0]) and ((int(ligne[5])>=moyennePoidRelSortante) or (int(ligne[5])<0))):#il y a une relation: si le poid est superieur à la borne ou que le poid est negatif
                        
                            listeRelation[lstMot[i]][1].append((ligne[3],ligne[4],ligne[5],x[1]))#on stocke le type de relation et le poid


                except:
                    continue
        




    def findTypeRelation(listeRelation):#liste relation est le tableau contenant toute les relations entre les mots, cette fonction va creer les phrases représentant les relations: ('114486', '5', '130', 'ragoût')  -> ragout $5 cassoulet
        
        tabChaine = []
        tabRelationEntrante = []
        tabRelationSortante = []
        tabChainePoid = {}
        os.chdir(PATH+"DONNEES")
    
        for key in listeRelation.keys():

            os.chdir(key)

            with open("relations_types.txt",'r') as file:#3
                for line in file:
                    try:
                        ligne = str(line)
                        ligne = ligne.replace("'","")
                        ligne = ligne.strip()
                        ligne = ligne.split(";")



                        passage = 0
                        for value in listeRelation[key]:
                        
                            for rel in value:
                            
                                if(rel[1]== ligne[1]):
                                    if(passage == 0):
                                        chaine = rel[3] +" $"+ str(ligne[1]) +" "+ key
                                        tabRelationEntrante.append(ligne[1])
                                    else:
                                        
                                        chaine = key +" $"+str(ligne[1]) +" "+ rel[3]
                                        tabRelationSortante.append(ligne[1])

                                    tabChaine.append(chaine)
                                    tabChainePoid[chaine]=int(rel[2])#on ajoute le chaine:poid
            
                            passage = passage + 1



                    except:
                        continue
            os.chdir("..")
        os.chdir("..")
        return tabRelationEntrante,tabRelationSortante,tabChaine,tabChainePoid







    def findRelationCherche(phrase):

        newPhrase = phrase+"*****"#delimitateur fin phrase
        tabRelationsCherche = []
        tabDeleteMots = []
    
        TabmessageRelationCherche = [phrase]

        os.chdir(PATH+"GENERAL")
        with open("mots.txt") as file:
            for line in file:
                ligne = str(line)
                ligne = ligne.strip()
                ligne = ligne.split(";")

                allmots = ligne[2].split("|")

                for mot in allmots:
                
                    if((mot+" " in newPhrase)):#+" " pour que ça soit un mot fini et pas inclus dans un autre mot
                        tabRelationsCherche.append(ligne[1])
                        #supprimer le mot de la phrase à la fin
                    
                        tabDeleteMots.append([mot,ligne[1]])
                        #messageRelationCherche = messageRelationCherche.replace(mot,'$'+str(ligne[1]))
        


        tabDeleteMots = trieTabStrDecroissant(tabDeleteMots)

    
        newPhrase = newPhrase.replace("*****","")
        newPhrase = newPhrase.strip()
        
    
        traite = []
        for mot in tabDeleteMots:

            if not mot in traite:

             
                #tester si il y a plusieurs appartion du mot dans tab delete, donc plusieurs relations possibles
                tabDeleteMotSeulementMot = [x[0] for x in tabDeleteMots]


                indicesOccurence = trouver_indices_valeur(tabDeleteMotSeulementMot,mot[0])
                if(len(indicesOccurence) > 1):
                    addTab=[]
                    for phrase in TabmessageRelationCherche:
                        #TabmessageRelationCherche.remove(phrase)
                        for indice in indicesOccurence:
                            
                            newPhrase = newPhrase.replace(mot[0],"") 
                            
                            messageRefait = phrase.replace(mot[0],'$'+tabDeleteMots[indice][1])
                            
                            addTab.append(messageRefait)
                    
                    nbDel=0
                    for indice in indicesOccurence:
                        
                        traite.append(tabDeleteMots[indice])
                        # tabDeleteMots.pop(indice-nbDel)
                        # nbDel+=1
                        
                



                    TabmessageRelationCherche = addTab
                
                else:
                    addTab=[]
                    for phrase in TabmessageRelationCherche:
                        # TabmessageRelationCherche.remove(phrase)

                        newPhrase = newPhrase.replace(mot[0],"")

                     
                        phrase2 = phrase.replace(mot[0],'$'+mot[1])
                    
                        addTab.append(phrase2)

                    TabmessageRelationCherche = addTab
        newPhrase = newPhrase.replace("*****","")
        newPhrase = newPhrase.replace("  "," ")
    
        os.chdir("..")
    
        return tabRelationsCherche,newPhrase,TabmessageRelationCherche


    def trouver_indices_valeur(tableau, valeur):
        indices = []
        for index, element in enumerate(tableau):
            if element == valeur:
                indices.append(index)
        return indices


    def splitAcolades(sentence):#va séparer les mots de la phrase selon les espaces mais AUSSI si il y a dans la phrase un groupe de mots entourés par { } alors il faudra qu'il soit considéré comme un seul mot dans le tableau que renvoie la fonction
        words = []
        current_word = ""
        within_braces = False

        for char in sentence:
            if char == '{':
                within_braces = True
            elif char == '}':
                within_braces = False
            elif char == ' ' and not within_braces:
                if current_word:
                    words.append(current_word)
                    current_word = ""
                continue

          
            current_word += char

        if current_word:
            words.append(current_word)

        return words


    def regrouper_elements_raffinement(tableau):
        resultat = []
        i = 0
        while i < len(tableau):
            if tableau[i] == '>':
                if i > 0 and i < len(tableau) - 1:
                    element_precedent = resultat.pop()
                    element_suivant = tableau[i + 1]
                    mot_cle = f"{element_precedent}>{element_suivant}"
                    resultat.append(mot_cle)
                    i += 2
                else:
                    resultat.append(tableau[i])
                    i += 1
            else:
                resultat.append(tableau[i])
                i += 1
        return resultat



    def extract_keywords(sentence):
   
        sen = sentence
       
        motsRaffinement = re.findall(r'\b\w+>\d+\b', sen)
        
     

        #suppression ponctuation
        char_nremov = "1,2,3,4,5,6,7,8,9,0,$"

        char_remove = []
        # for char in char_remov:
            
        #     sentence = sentence.replace(char, "")


        # Tokenization de la phrase en mots
        tokens = word_tokenize(sen, language='french')


        i = 0

        while i < len(tokens): #regrouper $ avec $22/$1/$212 ...
            if tokens[i] == "$":
                tokens[i] += tokens[i + 1]
                del tokens[i + 1]
            else:
                i += 1

        #regrouper sabre > 12 avec sabre>123/>22332 ...
        tokens = regrouper_elements_raffinement(tokens)  



        # Chargement des mots vides (stopwords) en français
        stop_words = set(stopwords.words('french'))

        # Extraction des mots non vides (non-stopwords) et non de ponctuation
        keywords = [word.lower() for word in tokens if (word.lower() not in stop_words) and (word.lower().isalpha()) or (word.lower().startswith("$")) and (word.lower() not in char_remove) or (word.lower().startswith("{")) or (word.lower().endswith("}")) or (">" in word.lower())]#and (word.isalpha() or "$" in word)

        return keywords


    def moyenneIndiceFile(file,indice):
        somme = 0
        i = 1
        with open(file,'r') as f:
            for line in f:
                ligne = str(line)
                ligne = ligne.strip()
                ligne = ligne.split(";")
                try:
                    somme = somme + int(ligne[indice])
                    i+=1
                except:
                    continue
        return somme / i


    def trieTabStrDecroissant(tableau):
        for i in range(len(tableau)):
            for j in range(len(tableau) - 1 - i):
                if len(tableau[j][0]) < len(tableau[j+1][0]):
                    tableau[j], tableau[j+1] = tableau[j+1], tableau[j]
        return tableau


    def inverser_tableau(tableau):
        return tableau[::-1]


    def regrouper_dictionnaires(dict1, dict2):
        resultat = {}

        # Parcourir les clés du premier dictionnaire
        for cle in dict1.keys():
            
            # Fusionner les valeurs correspondantes des deux dictionnaires
            valeurs = [dict1[cle][0] + dict2[cle][0] ,dict1[cle][1] + dict2[cle][1]]

            resultat[cle] = valeurs

        return resultat



    def maxTableauTupleDeuxieme(tab):
        max=tab[0][1]
        indice=0
        for j in range(1,len(tab)):
            if(tab[j][1] > max):
                max = tab[j][1]
                indice = j

        return indice


    def find_r_RELATION(mot,relation,n):#n est le nombre de mots is_a voulu relation : numero de la relation en char : '6'
        lst_is_a_id = []
        lst_is_a_id_n = []

        os.chdir(PATH+"DONNEES")
        os.chdir(mot)

        #le dossier existe déjà
        with open("relation_sortantes.txt",'r') as f:
            for line in f:
                ligne = str(line)
                ligne = ligne.strip()
                ligne = ligne.split(";")
                try:
                    if(ligne[4] == relation):#is_a
                        lst_is_a_id.append((ligne[3],int(ligne[5])))#id et poid
                except:
                    continue

        if(relation == '8'):#seulement pour hypo
            with open("relation_entrantes.txt",'r') as f:
                for line in f:
                    ligne = str(line)
                    ligne = ligne.strip()
                    ligne = ligne.split(";")
                    try:
                        if(ligne[4] == relation):#is_a
                            lst_is_a_id.append((ligne[2],int(ligne[5])))#id et poid
                    except:
                        continue
        
        #faire le tri avec les n premier is_a mots en fct de poid

        #trier la liste sans les mots qui commences par _
     
        newLst=[]
        with open("nodes.txt",'r') as f:
            for line in f:
                ligne = str(line)
                ligne = ligne.strip()
                ligne = ligne.split(";")
                for elem in lst_is_a_id:
                    try:
                        if(ligne[1]==elem[0]):
                            if not('_' in ligne[2]):
                             
                                newLst.append(elem)

                    except IndexError:
                        continue

        lst_is_a_id =  newLst
    

        for i in range(n):
            try:
               indice = maxTableauTupleDeuxieme(lst_is_a_id)
            except IndexError:
                continue

            lst_is_a_id_n.append(lst_is_a_id[indice])
            lst_is_a_id.pop(indice)
        

            

        #trouver les mots associés aux ids

        lst_is_a_nom = []

        with open("nodes.txt",'r') as f:
            for line in f:
                ligne = str(line)
                ligne = ligne.strip()
                ligne = ligne.split(";")

                for e in lst_is_a_id_n:
                    try:
                        if(ligne[1] == e[0]):
                          
                            if(len(str(ligne[2]).split()) > 1):#c'est un mot double ou multiple: on met des accolades pour l'entourer
                               
                                ph = "{"
                                ph = ph+str(ligne[2]).replace("'","").lower()+"}"
                                lst_is_a_nom.append(ph)
                            else:
                                lst_is_a_nom.append(str(ligne[2]).replace("'","").lower())#le nom
                    except:
                        continue

        os.chdir("..")
        os.chdir("..")
     
        return lst_is_a_nom


    def generer_phrases(listes):#genere toute combinaison de phrase avec les mots
        #[["Je", "Tu"], ["mange", "dors"], ["une pomme", "un gâteau"]] -> 
        # Je mange une pomme
        # Je mange un gâteau
        # Je dors une pomme
        if len(listes) == 0:
            return []
        
        phrases = []
        mots_actuels = listes[0]
        autres_mots = generer_phrases(listes[1:])
        
        if len(autres_mots) == 0:
            return [mot for mot in mots_actuels]
        
        for mot in mots_actuels:
            for autre_mot in autres_mots:
                phrase = mot + " " + autre_mot
                phrases.append(phrase)
        
        return phrases

    def parcourir_mots_accolade(phrase):
        mots = []
        mot_actuel = ""
        entre_accolades = False

        for caractere in phrase:
            if caractere == "{":
                entre_accolades = True
            elif caractere == "}":
                entre_accolades = False
                mots.append(mot_actuel)
                mot_actuel = ""
            elif caractere == " " and not entre_accolades:
                if mot_actuel:
                    mots.append(mot_actuel)
                    mot_actuel = ""
            else:
                mot_actuel += caractere

        if mot_actuel:
            mots.append(mot_actuel)

        return mots


    def supprimer_mots_dollars(tableau):#dans un tableau de phrase contenant des $ : pour chaque phrase supprime les $
        newT = [x for x in tableau]
        for i in range(len(newT)):
            mots = splitAcolades(newT[i])
            mots_sans_dollar = [mot for mot in mots if not mot.startswith('$')]
            newT[i] = ' '.join(mots_sans_dollar)
        return newT


    def supprimer_mots_phrase(phrase, tableau):#supprime les mots d'une phrase qui sont contenu dans le tableau

        mots = splitAcolades(phrase)  # Sépare la phrase en mots
        mots_filtres = [mot for mot in mots if mot not in tableau]  # Filtre les mots qui ne se trouvent pas dans le tableau
        phrase_filtree = ' '.join(mots_filtres)  # Rejoindre les mots filtrés pour former une nouvelle phrase
        
        return phrase_filtree

    def replace_dollars_par_sa_relation(phrase):#dans une phrase si il y a '$6' il sera remplacé par 'est un'
        os.chdir(PATH+"GENERAL")

        newPhrase = ""

        sp = splitAcolades(phrase)
        for mot in sp:
            if(mot.startswith('$')):
                rel = mot.replace('$','')
                with open("mots.txt",'r') as file:
                    for line in file:
                        ligne = str(line)
                        ligne = ligne.strip()
                        ligne = ligne.split(";")

                
                        if(str(ligne[1]) == rel):
                            allmots = ligne[2].split("|")
                            newPhrase = newPhrase + allmots[0]+" "
            else:
                newPhrase = newPhrase + mot+" "


        os.chdir("..")
        return newPhrase


    def mots_uniques(tableau):
        mots = set()  # Créer un ensemble vide pour stocker les mots uniques

        for phrase in tableau:
            mots_phrase = splitAcolades(phrase)  # Diviser chaque phrase en mots
            mots.update(mots_phrase)  # Ajouter les mots de la phrase à l'ensemble

        return list(mots)  # Convertir l'ensemble en liste et la renvoyer



    def ajoute_mot_phrase_algebre(tab,tab2,tabCONDITION=None):#[a,b] [b,a] -> [a,b] [b,a] [a,b,a]
      
        newTableau = [x for x in tab]
        phraseSeulementNew = []
        for phraseI in range(len(tab)):
            lastWord = splitAcolades(tab[phraseI])[-1]

            for phraseI2 in range(len(tab2)):
                if(tab[phraseI] != tab2[phraseI2]):#pas le meme indice
                    first_word = splitAcolades(tab2[phraseI2])[0]
                    if(first_word == lastWord):#on peut concatener
                        phraseSansPremierMot = ""
                        phraseSplit= splitAcolades(tab2[phraseI2])
                        for i in range(len(phraseSplit)):
                            if(i != 0):
                                phraseSansPremierMot = phraseSansPremierMot + phraseSplit[i] + " "
                    

                        newphrase = tab[phraseI] + " " + phraseSansPremierMot
                        newphrase = newphrase.strip()
                        newTableau.append(newphrase)
                        phraseSeulementNew.append(newphrase)

        return phraseSeulementNew

    def supprimer_doublons(tableau):
        tableau_sans_doublons = list(set(tableau))
        return tableau_sans_doublons


    def replaceRelation(message):#prend un message de la forme: x 'r_isa/autre' y et renvoie x $6 y
        os.chdir(PATH+"GENERAL")
        newMsg = message
        with open("relations_types.txt",'r') as f:

            for line in f:
                try:
                    ligne = str(line)
                    ligne = ligne.replace("'","")
                    ligne = ligne.strip()
                    ligne = ligne.split(";")

                    if(ligne[2] in newMsg):
                        newMsg = newMsg.replace(ligne[2],'$'+str(ligne[1]))

                except:
                    continue

        os.chdir("..")
        return [newMsg]
            

            # for mot in msgsplit:
            #     if("r_" in mot):
            #         for line in f:
            #             try:
            #                 ligne = str(line)
            #                 ligne = ligne.replace("'","")
            #                 ligne = ligne.strip()
            #                 ligne = ligne.split(";")

            #                 if(ligne[2]==mot):

            #             except:
            #                 continue



    def trouverLesNouvellesRelations(msgList,TabmessageRelationCherche,msgListIndice = None):

        msgListAvecIndiceNew = []

        nbMots = 2

    #SI PREMIER PASSAGE, LISTE VIDE ALORS ON MET L'INDICE DANS MSGLIST AUX ELEMENTS, ET ON METTRA AUX SUIVANT SI IL Y A ENCORE UN APPEL
        if(msgListIndice == None):
            
            msgListIndice = [(msgList[x],x) for x in range(len(msgList))] #contient les mots de msgList + leurs indices dans un tuple : {(chat,0),(chien,1)]


        msgListAvecIndiceNew = [x for x in msgListIndice]



        listeNewMotsIsa = [[] for x in range(count_different_elements(msgListIndice))]

        
        #isa
        for m in msgListIndice:
           

            listeNewMotsIsa[m[1]] = listeNewMotsIsa[m[1]] + [m[0]]

            NEWREL = find_r_RELATION(m[0],'6',nbMots)

            listeNewMotsIsa[m[1]] = listeNewMotsIsa[m[1]] + NEWREL

            #creer la nouvelle liste pour le prochain appel
            for j in NEWREL:

                msgListAvecIndiceNew.append((j,m[1]))
            

        
        listeNewMotsHypo = [[] for x in range(count_different_elements(msgListIndice))]
        #hypo
        for m in msgListIndice:
            listeNewMotsHypo[m[1]] = [m[0]]

            NEWREL = find_r_RELATION(m[0],'8',nbMots)

            listeNewMotsHypo[m[1]] = listeNewMotsHypo[m[1]] + NEWREL
        
        
            #creer la nouvelle liste pour le prochain appel
            for j in NEWREL:

                msgListAvecIndiceNew.append((j,m[1]))
    

        msgListAvecIndiceNew = list(set(msgListAvecIndiceNew))
       

      


        
        listePhrasesIsa = generer_phrases(listeNewMotsIsa)
        listePhrasesHypo = generer_phrases(listeNewMotsHypo)
   
    

        newIsACherche=[]
        newHypoCherche=[]

        #ISAAAA

        
        listePhrasesIsa = list(set(listePhrasesIsa))

   
    
        for phrase in listePhrasesIsa:
            phraseSplit = splitAcolades(phrase)
        
            for cherche in TabmessageRelationCherche:
                newPhrase = ""
                chercheSplit = splitAcolades(cherche)
                nombreSpe = 0
                for Imot in range(len(chercheSplit)):

                    if(chercheSplit[Imot].startswith("$")):
                        newPhrase = newPhrase + chercheSplit[Imot] +" "
                        nombreSpe+=1

                    else:
                        #tester si il y a des accolades et si il y en a c'est le meme mot jusqu'à l'autre accolade
                        
                        newPhrase = newPhrase + phraseSplit[Imot-nombreSpe] + " "

                newPhrase = newPhrase.strip()
                newIsACherche.append(newPhrase)

        

        #HYPOOOOOO

        for phrase in listePhrasesHypo:
            phraseSplit = splitAcolades(phrase)
        
            for cherche in TabmessageRelationCherche:
                newPhrase = ""
                chercheSplit = splitAcolades(cherche)
                nombreSpe = 0
                for Imot in range(len(chercheSplit)):

                    if(chercheSplit[Imot].startswith("$")):
                        newPhrase = newPhrase + chercheSplit[Imot] +" "
                        nombreSpe+=1

                    else:
                        #tester si il y a des accolades et si il y en a c'est le meme mot jusqu'à l'autre accolade
                        
                        newPhrase = newPhrase + phraseSplit[Imot-nombreSpe] + " "

                newPhrase = newPhrase.strip()
                newHypoCherche.append(newPhrase)


        return newIsACherche,newHypoCherche,msgListAvecIndiceNew

    
    def findRaffinementSemantique(phrase):#prend en entrée une phrase contenant les mots clés et renvoie un dictionnaire contenant pour chaque mot une liste de ses raffinements
        os.chdir(PATH+"DONNEES")
        spitPhrase = splitAcolades(phrase)
        dicoRaf = {}
        for mot in spitPhrase:
            os.chdir(mot)
            relationRaf = []
            dicoRaf[mot] = []


            with open("relation_sortantes.txt",'r') as file:
                
                for line in file:
                    try:
                        ligne = str(line)
                        ligne = ligne.replace("'","")
                        ligne = ligne.strip()
                        ligne = ligne.split(";")

                        if(int(ligne[4]) == 1 and int(ligne[5]) >= moyennePoidRelSortante):#relation raffinement
                            relationRaf.append(ligne[3])#ajout id 

                    except:
                        continue

            #on a les id des raffinements, on va ajouter leurs noms et leurs nom pour la recherche : {sabre:[(sabre>poisson,sabre>14543),(),()]}

            with open("nodes.txt",'r') as file:
                
                for line in file:
                    try:
                        ligne = str(line)
                        ligne = ligne.replace("'","")
                        ligne = ligne.strip()
                        ligne = ligne.split(";")

                        for raf in relationRaf:

                            if(ligne[1] == raf):#relation raffinement
                                dicoRaf[mot].append((ligne[5],ligne[2]))

                    except:
                        continue

            os.chdir("..")
    
        os.chdir("..")
        return dicoRaf


    
    bot.run(TOKEN)


def count_different_elements(lst):#my_list = [("chat", 0), ("chien", 2), ("tortue", 2)]
    #renvoie 2
    #compte le nombre de deuxieme terme des éléments de la liste différents
    distinct_elements = set()
    for _, num in lst:
        distinct_elements.add(num)
    return len(distinct_elements)

def contain_first_element_liste_tuple(lst, string):
    for item in lst:
        if string == item[0]:
            return True
    return False





if(__name__ == "__main__"):
    # while 1:
    #     try:
    #         launch()
    #     except:
    #         continue
    launch()



    """
    TODO:   '_' dans nom


    with open("nodes.txt",'r') as f:
            if(lst_is_a_id != []):
                for i in range(n):
                  

                    
                    valide = False
                    while valide == False:
                        try:
                            indice = maxTableauTupleDeuxieme(lst_is_a_id) 
                        except:
                            indice = None
                            break 

                        for line in f:
                            ligne = str(line)
                            ligne = ligne.strip()
                            ligne = ligne.split(";")
                            
                            try:
                                if(ligne[1] == lst_is_a_id[indice][0]):
                              
                                    if(ligne[2].startswith('_')):
                                      
                                        valide = False
                                        lst_is_a_id.pop(indice)
                                    else:
                                    
                                        valide = True
                                        
                            except IndexError:
                               
                                continue

                    
                    if(indice != None):
                        lst_is_a_id_n.append(lst_is_a_id[indice])
                        lst_is_a_id.pop(indice)
                
            else:
                lst_is_a_id_n = []
            #trouver les mots associés aux ids

    """

