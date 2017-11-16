TOKEN = "" #Mettre ici votre token




















REFRESHTIME = 10 #a regler
NBTOPICS = 40

if TOKEN == "" :
    print("Vous n'avez pas inscrit votre token dans le script, merci donc de rentrer vos identifiants")
    username = input("Pseudo : ")
    mdp = input("Mot de passe : ")
idTopic = 0
















import json
import urllib3
import sys
import time
import threading
import queue
urllib3.disable_warnings()
http = urllib3.PoolManager()

class Client() :
    def __init__(self) :
        self.pseudo = ""
        self.mdp = ""
        self.token = ""
        self.id = ""

    def connection(self, pseudo, mdp) : #ok
        self.pseudo = pseudo
        self.mdp = mdp
        r = http.request('POST', 'https://avenoel.org/api/v1/auth', fields = {'username' : pseudo, 'password' : mdp})
        liste = json.loads(r.data)
        self.token = liste["api_token"]
        if liste["error"] == None :
            print("Authentification faite :)")
        else :
            print(liste["error"])

    def pseudoFromId(self, id) :
        r = http.request('GET', 'https://avenoel.org/api/v1/user/'+str(id))
        liste = json.loads(r.data)
        return(liste["data"]["username"])

    def getAllTopics(self) : #ok
        """Retourne une liste des topics, faire liste[k]["api_url"] pour l'url, "title" pour le titre"""
        r = http.request('GET', 'https://avenoel.org/api/v1/topics', fields = {'size' : NBTOPICS})
        liste = json.loads(r.data)
        return liste["data"]

    def getTopic(self, id) : #ok
        """Retourne les infos d'un topic et de son auteur, il faut passer l'id du topic"""
        r = http.request('GET', 'https://avenoel.org/api/v1/topics/'+str(id), fields = {'with_user' : True})
        liste = json.loads(r.data)
        return liste

    def getAllMessages(self, id) : #ok
        """Retourne les infos d'un topic et de son auteur, il faut passer l'id (un int) du topic
        "content" pour le contenu d'un message"""
        r = http.request('GET', 'https://avenoel.org/api/v1/messages/', fields = {'topic_id' : id})
        liste = json.loads(r.data)
        return liste

    def getLastMessages(self, nb) : #ok
        """Retourne les infos d'un topic et de son auteur, il faut passer l'id (un int) du topic
        "content" pour le contenu d'un message"""
        r = http.request('GET', 'https://avenoel.org/api/v1/messages/', fields = {'topic_id' : self.id, 'reverse' : True, 'size' : nb})
        liste = json.loads(r.data)
        return liste

    def postMessage(self, id, message) : #ok
        if self.token == "" :
            print("Pas de token d'api")
        r = http.request('POST', 'https://avenoel.org/api/v1/messages', headers = {'X-Authorization' : self.token}, fields = {'topic_id' : id, 'content' : message})
        liste = json.loads(r.data)
        return liste

    def send(self, msg) :
        if self.id == "" :
            print("Pas de blabla")
        else :
            l = self.postMessage(self.id, msg)

def affichage(li, lasti) :
    """Affiche une liste de getLastMessages par exemple"""
    dernierMessage = ""
    if li :
        dernierMessage = li["messages"][0]["content"]
    tmp = 0
    if li["messages"] :
        for k in li["messages"] :
            if k["content"] == lasti :
                break
            tmp+=1
    for indice in range(tmp) :
        k = li["messages"][tmp-indice-1]
        tmpPseudo = c.pseudoFromId(k["user_id"])
        if lasti == k["content"] :
            break
        liste = k["content"].split("\n")
        for i in liste :
            if i and not i[0] == ">" and not i == "\r" :
                print("<"+tmpPseudo+">", end = " ")
                for k in i.split() :
                    if not "https://image.noelshack.com/" in k :
                        print(k, end = " ")
                    else :
                        print(k[:k.index("https://image.noelshack.com/")], end = " ")
                print("")
    return dernierMessage

def init() :
    li = c.getAllTopics()
    for i in range(5) :
        print('--')
    print("Rappel du pseudo utilisé :", c.pseudo)
    print("Liste des premiers topics :")
    for k in range(len(li)) :
        print("(" + str(k) + ")", li[k]["title"], "[" + str(li[k]["messages_count"][0]["aggregate"]) + " messages]")
    print("")
    numTopic = int(input("Quel numéro de topic ? (-1 pour recharger une liste de topics) "))
    if numTopic == -1 :
        print("Chargement de la liste des sujets en cours")
        init()
    else :
        print("Chargement du topic numéro", numTopic, "en cours")
        c.id = li[numTopic]["id"]
        for i in range(10) :
            print('--')
        print("Nombre de post du topic :", li[numTopic]["messages_count"][0]["aggregate"])
        print("Titre du topic :", li[numTopic]["title"])
        try :
            global last_work_time
            last_work_time = 0
            idle_work()
        except :
            None

timeout = 0.2 # seconds
last_work_time = 0
lastmsg = ""

c = Client()
if TOKEN != "" :
    c.token = TOKEN
else :
    c.connection(username, mdp)
init()


def treat_input(linein):
    if linein[0:2] == "//" :
        if linein[0:6] == "//help" :
            print("Commande disponible :")
            print("//exit :d) sert à quitter le topic")
            print("//refresh :d) sert à regarder si des nouveaux messages sont la")
            print("//set refreshtime = X :d) sert à mettre le temps de raffraichissement à X")
            print("//set nbtopics = X :d) sert à regler le nombre de topics affichés dans ")
        elif linein[0:6] == "//exit" :
            print("Retour à la liste des sujets en cours")
            init()
        elif linein[0:9] == "//refresh" :
            idle_work()
            print("Refresh effectué")
        elif linein[0:20] == "//set refreshtime = " :
            global REFRESHTIME
            REFRESHTIME = int(linein[20:])
            print("Temps de raffraichissement changé à", REFRESHTIME, "secondes")
        elif linein[0:17] == "//set nbtopics = " :
            global NBTOPICS
            NBTOPICS = int(linein[17:])
            print("Nombre de topics chargés changé à", NBTOPICS)
        else :
            print("Commande non comprise")
    else :
        if len(linein) > 2 :
            c.send(linein)
            idle_work()

def idle_work():
  global last_work_time
  now = time.time()
  # do some other stuff every REFRESHTIME seconds of idleness
  if now - last_work_time > REFRESHTIME :
    last_work_time = now
    li = c.getLastMessages(10)
    global lastmsg
    lastmsg = affichage(li, lastmsg)

# will hold all input read, until the work thread has chance
# to deal with it
input_queue = queue.Queue()

# will signal to the work thread that it should exit when
# it finishes working on the currently available input
no_more_input = threading.Lock()
no_more_input.acquire()

# will signal to the work thread that it should exit even if
# there's still input available
interrupted = threading.Lock()
interrupted.acquire()



# work thread' loop: work on available input until main
# thread exits
def treat_input_loop():
  while not interrupted.acquire(blocking=False):
    try:
      treat_input(input_queue.get(timeout=timeout))
    except queue.Empty:
      # if no more input, exit
      if no_more_input.acquire(blocking=False):
        break
      else:
        idle_work()

work_thread = threading.Thread(target=treat_input_loop)
work_thread.start()

# main loop: stuff input in the queue until there's either
# no more input, or the program gets interrupted
try:
  for line in sys.stdin:
    if line: # optional: skipping empty lines
      input_queue.put(line)

  # inform work loop that there will be no new input and it
  # can exit when done
  no_more_input.release()

  # wait for work thread to finish
  work_thread.join()

except KeyboardInterrupt:
    interrupted.release()
