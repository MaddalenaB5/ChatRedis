import redis

# Connetti al server Redis cloud del tuo collega con autenticazione
r = redis.Redis(host='redis-18934.c328.europe-west3-1.gce.redns.redis-cloud.com',
                port=18934,
                db=0,
                charset="utf-8",
                decode_responses=True,
                password='4GVWbKjMnaiMtHaX56tTNKODmzblmYtq')
print('Connesso')

# Funzione di registrazione
def registrazione():
    nome = input("Inserisci il nome utente che vuoi usare: ")

    # Controllo se il nome utente esiste già
    if r.hget(f"user:{nome}", "passw") is None:
        password = input("Inserisci la password che vuoi usare: ")
        r.hset(f"user:{nome}", mapping={"passw": password, "DnD": 0})
        print("Registrazione completata con successo.")
    else:
        print("Nome utente già presente. Riprova.")

# Funzione di login
def login():
    nome = input('Inserisci il tuo nome utente: ')
    password = input('Inserisci la password: ')

    pass_salvate = r.hget(f"user:{nome}", "passw")

    if pass_salvate is None:
        print("Nome utente non trovato. Registrazione necessaria.")
        return None
    else:
        if pass_salvate == password:
            print("Login riuscito!")
            return nome
        else:
            print("Password errata.")
            return None

# Funzione per aggiungere contatti
def aggiungi_contatto(nome, contatto):
    if r.hget(f"user:{contatto}", "passw") is None:
        print('Utente non esistente')
    else:    
        r.rpush(f"contatti:{nome}", contatto)
        print(f"Aggiunto {contatto} alla lista contatti di {nome}")

# Funzione per modificare la modalità Do Not Disturb
def DND(nome):
    scelta1 = input("Vuoi modificare la modalità Do Not Disturb: si / no ").lower()
    if scelta1 == "si":
        val = r.hget(f"user:{nome}", "DnD")
        if val == "0":
            r.hset(f"user:{nome}", "DnD", 1)
            print("Modalità Do Not Disturb attivata.")
        else:
            r.hset(f"user:{nome}", "DnD", 0)
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
