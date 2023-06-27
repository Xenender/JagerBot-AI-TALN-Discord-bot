import time
import requests
import os

nombreRepet = 0
def doRequest(mot):
    global nombreRepet
    nombreRepet+=1

    mot = mot.replace('{','').replace('}','')

    frr = "null"
    response = requests.get("https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel="+mot+"&rel=")
    muted = True
    while(muted):
        with open("all.txt",'w') as f:
            if(not("<CODE>MUTED_PLEASE_RESEND") in response.text):
                print("NON MUT")
                muted = False
                f.write(response.text)
            else:
                print("MUTEDDDD")
                time.sleep(3)
                response = requests.get("https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel="+mot+"&rel=")


    time.sleep(1)

    with open("all.txt",'r') as f:
        with open("nodes_types.txt",'w') as nodes_type:
            with open("nodes.txt",'w') as nodes:
                with open("relations_types.txt",'w') as relations_types:
                    with open("relation_sortantes.txt","w") as relations_sortantes:
                        with open("relation_entrantes.txt","w") as relations_entrantes:

                            for line in f:
                                l = line.rstrip()
                                #nodes_types
                                if "(Nodes Types)" in l:
                                    frr="rt"
                                #nodes
                                elif "(Entries)" in l:
                                    frr="n"
                                #relations types
                                elif "(Relation Types)" in l:
                                    frr="r"
                                #relations sortantes
                                elif "relations sortantes :" in l:
                                    frr="rs"
                                #relations entrantes
                                elif "relations entrantes :" in l:
                                    frr="re"
                                elif "</CODE>" in l:
                                    frr = "null"
                                
                                else:
                                    if(not("//" in line)):

                                        if(frr == "rt"):
                                            #1 file
                                            nodes_type.write(l+"\n")
                                        elif(frr == "n"):
                                            #2 file
                                            nodes.write(l+"\n")
                                        elif(frr == "r"):
                                            #3 file
                                            relations_types.write(l+"\n")
                                        elif(frr == "rs"):
                                            #3 file
                                            relations_sortantes.write(l+"\n")
                                        elif(frr == "re"):
                                            #3 file
                                            relations_entrantes.write(l+"\n")

    dossiersDonnees = os.listdir()
    if(dossiersDonnees == [] and nombreRepet < 5):
        print("ERREUR DOSSIER VIDE")
        doRequest(mot)
