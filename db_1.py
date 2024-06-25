import redis as red
import getpass
import hashlib

# Connetti al server Redis cloud del tuo collega con autenticazione
r = red.Redis(host='redis-18934.c328.europe-west3-1.gce.redns.redis-cloud.com',
                port=18934,
                db=0,
                charset="utf-8",
                decode_responses=True,
                password='4GVWbKjMnaiMtHaX56tTNKODmzblmYtq')
print('Connesso')

#Converte la password in un hash per motivi di sicurezza
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#prova da controllare (mi piace di più)
# Funzione di registrazione
def registrazione(username, password):
    if r.hexists(f"utenti:{username}", "nome"):
        print("Nome Utente già utilizzato. Sceglierne un'altro...")
        return False
    password_hash = hash_password(password)
    dati_utente = {
        "nome": username,
        "password": password_hash,
        "contatti": [],
        "dnd" : 0
        }
    
    r.hset(f"utenti:{username}", dati_utente)
    return True

# Funzione di login
def login(username, password):
    if not r.hexists(f"utenti:{username}", "nome"):
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False
    
    password_salvata = r.hget(f"utenti:{username}", "password")
    if password_salvata == hash_password(password):
        print("Benvenuto!")
        return True
    else:
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False

'''
#ricerca utenti anche parziale
def ricerca_utenti(user):
    nomi_presenti = r.hkeys("utenti")
    risultati = []
    for nome_utente in nomi_presenti:
        if user.lower() in nome_utente[0:len(user)+1].lower():
            risultati.append(nome_utente)
        
        return risultati


# Funzione per aggiungere nuovi contatti
def aggconta(user):
    contparz = input(str("utente che vuoi cercare: "))
    ricerca_utenti(contparz)
    contscelto = input(str("quale scegli? "))
    if red.hget(f"user:{contscelto}") is None: # Si controlla l'estistenza del contatto nel db
        print('Utente non esistente')
    else: #controlla che non sia già presente nella lista contatti
        lista_contatti = red.lrange(f"contatti:{user}", 0, -1)  #restituisce la lista dei contatti
        if contscelto.encode('utf-8') in lista_contatti:
            print('Contatto già presente')
        else:
            red.rpush(f"contatti:{user}", contscelto) #qui aggiungo a contatti (una lista) dell'utente il contatto che vuole aggiungere
            print(f"Aggiunto {contscelto} alla lista contatti di {user}")


#Funzione per visalizzare i contatti
def contatti_utente(user):
    lista_contatti = red.lrange(f"contatti:{user}", 0, -1) #stesso metodo presente nell'aggiungi contatti
    if not lista_contatti:  # In caso la lista sia vuota
        print(f"Non hai contatti da visualizzare")
    else:
        print(f"I tuoi contatti sono:")
        for contatto in lista_contatti:
            print(contatto.decode('utf-8'))

'''

# Funzione primo menù
def main():
    while True:
        scelta = input("Vuoi (r)egistrati oppure effettuare il (l)ogin? (q) per uscire ").lower()
        
        match scelta:
            case "q":
                break
            case "r":
                username = input("Inserire l'username: ")
                password = getpass.getpass("Inserire la password: ")
                registrazione(username, password)
            case "l":
                username = input("Inserire l'username: ")
                password = getpass.getpass("Inserire la password: ")
                loggato = login(username, password)
            case _:
                print("Scelta non valida! Riprovare...")
            

        '''
        if loggato == True:
            usernameloggato = username
            main2(usernameloggato, loggato)
            valdnd = r.hget("utenti", usernameloggato, "dnd")
            if valdnd == 1:
                print("Do Not Disturb attivo")
            else:
                print("Do Not Disturb disattivo")
            '''


'''
# Funzione per modificare la modalità Do Not Disturb

def DND(user): # User è il nome dell'utente in sessione.
    scelta1 = input("Vuoi modificare la modalità Do Not Disturb: si / no ").lower()
    if scelta1 == "si":
        val = red.hget(f"user:{user}", "DnD")
        if val == "0":
            red.hset(f"user:{user}", "DnD", 1)
            print("Modalità Do Not Disturb attivata.")
        else:
            red.hset(f"user:{user}", "DnD", 0)
            print("Modalità Do Not Disturb disattivata.")

# Esecuzione delle funzioni
while True:
    azione = input("Vuoi registrarti o fare il login? (registrazione/login): ").lower()
    if azione == "registrazione":
        registrazione()
    elif azione == "login":
        nome = login()
        if nome:
            while True:
                scelta = input("Cosa vuoi fare? (DND/aggiungi contatto/logout): ").lower()
                if scelta == "dnd":
                    DND(nome)
                elif scelta == "aggiungi contatto":
                    contatto = input("Inserisci il nome del contatto da aggiungere: ")
                    #aggiungi_contatto(nome, contatto)
                elif scelta == "logout":
                    print("Logout effettuato.")
                    break
                else:
                    print("Scelta non valida. Riprova.")
    else:
        print("Scelta non valida. Riprova.")

'''

#per entrare nel primo     
if __name__ == "__main__":
    main()