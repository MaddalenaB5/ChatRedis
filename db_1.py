import redis as red
import getpass

# Connetti al server Redis cloud del tuo collega con autenticazione
r = red.Redis(host='redis-18934.c328.europe-west3-1.gce.redns.redis-cloud.com',
                port=18934,
                db=0,
                charset="utf-8",
                decode_responses=True,
                password='4GVWbKjMnaiMtHaX56tTNKODmzblmYtq')
print('Connesso')

# FUNZIONE DI REGISTRAZIONE
#possibile soluzione
'''
# Funzione di registrazione
def registrazione(contatti = [], stato = 0):
    nome = input("Inserisci il nome utente che vuoi usare: ")
    # Controllo se il nome utente esiste già
    if red.hget(f"user:{nome}", "passw") is None:
        user = nome
        password = input("Inserisci la password che vuoi usare: ")
        # Creare un hash Redis per l'utente
        utente_hash = {"username": user,
                       "password": password,
                       "contatti": contatti,
                       "stato": stato}
        red.hset("utenti", user, utente_hash)
        print("Registrazione completata con successo.")
    else:
        print("Nome utente già presente. Riprova.")
'''

#prova da controllare (mi piace di più)
# Funzione di registrazione
def registrazione(username, password):
    nome = input("Inserisci il nome utente che vuoi usare: ")
    # Controllo se il nome utente esiste già
    if red.hget(f"user:{nome}") is None:                                      #controlla solo l'esistenza del nome
        user = nome                                                         #inizio a distinguere nome (ricerca) da user (utente in sessione)
        password = input("Inserisci la password che vuoi usare: ")
        statoUt = f"DnD : {user}"                                           #funzione per la bitmap
        red.setbit(statoUt, 0, 0)                                             #setting del valore che deve assumere
        # Creare un hash Redis per l'utente
        utente_hash = {"username": user,
                       "password": password,
                       "contatti": contatti,
                       "DnD": statoUt}                                      #inserimento della bitmap all'interno della ash
        r.hset("utenti", nome, utente_hash)
        print("Registrazione completata con successo.")
    else:
        print("Nome utente già presente. Riprova.")

# Funzione di login
def login():
    nome = input('Inserisci il tuo nome utente: ')
    password = input('Inserisci la password: ')

    pass_salvate = red.hget(f"user:{nome}", "passw")

    if pass_salvate == password:
        print("Login riuscito!")
        return nome
    else:
        print("Qualcosa è andato storto. Non tornare più!")
        return None

# Funzione per aggiungere nuovi contatti
def aggiungi_contatto(user, contatto):
    if red.hget(f"user:{contatto}") is None: # Si controlla l'estistenza del contatto nel db
        print('Utente non esistente')
    else: #controlla che non sia già presente nella lista contatti
        lista_contatti = red.lrange(f"contatti:{user}", 0, -1)  #restituisce la lista dei contatti
        if contatto.encode('utf-8') in lista_contatti:
            print('Contatto già presente')
        else:
            red.rpush(f"contatti:{user}", contatto) #qui aggiungo a contatti (una lista) dell'utente il contatto che vuole aggiungere
            print(f"Aggiunto {contatto} alla lista contatti di {user}")

#Funzione per visalizzare i contatti
def contatti_utente(user):
    lista_contatti = red.lrange(f"contatti:{user}", 0, -1) #stesso metodo presente nell'aggiungi contatti
    if not lista_contatti:  # In caso la lista sia vuota
        print(f"Non hai contatti da visualizzare")
    else:
        print(f"I tuoi contatti sono:")
        for contatto in lista_contatti:
            print(contatto.decode('utf-8'))

#Funzione di ricerca utenti parziale
def ricerca_utente_parziale(utente_parziale):
    utenti_tutti = red.keys("user:*") #qui si trovano tutti i nomi utenti
    utenti_trovati = [] #qui si crea una lista con tutti i nomi utenti
    for i in utenti_tutti: #qui fa la ricerca parziale
        utente = i.decode('utf-8').split(':')[1] # divide user dal suo valore e restituisce quindi il nome associato
        if utente_parziale in utente:
            utenti_trovati.append(utente)
    return utenti_trovati

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
                    aggiungi_contatto(nome, contatto)
                elif scelta == "logout":
                    print("Logout effettuato.")
                    break
                else:
                    print("Scelta non valida. Riprova.")
    else:
        print("Scelta non valida. Riprova.")


#Converte la password in un hash per motivi di sicurezza
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


#per entrare nel primo     
if __name__ == "__main__":
    main()