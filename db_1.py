import redis as red

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
def registrazione(contatti = []):
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

# Funzione per aggiungere contatti
def aggiungi_contatto(nome, contatto):
    if red.hget(f"user:{contatto}") is None: # Si controlla l'estistenza del contatto nel db
        print('Utente non esistente')
    else:    # Dovremo controllare se il contatto è già presente nella lista
        red.rpush(f"contatti:{nome}", contatto)
        print(f"Aggiunto {contatto} alla lista contatti di {nome}") # Altrimenti lo si aggiunge.


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
