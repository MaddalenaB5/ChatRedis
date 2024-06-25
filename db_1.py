import redis as red
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
        "dnd" : 0
        }

    r.hmset(f"utenti:{username}", dati_utente)
    return True
"""
def registrazione2(username, password):
    if r.hexists(f"utenti:{username}", "nome"):
        print("Nome Utente già utilizzato. Sceglierne un'altro...")
        return False
    
    password_hash = hash_password(password)
    
    r.hset(f"utenti:{username}","nome",username)
    r.hset(f"utenti:{username}","password",password_hash)
    r.rpush(f"utenti:{username}:contatti","")
    r.setbit(f"utenti:{username}:dnd",0,0)
    
    return True
"""
# FARE CASTING DA LISTA IN STRINGA E VICEVERSA
# Funzione di login
def login(username, password):
    if not r.hexists(f"utenti:{username}", "nome"):
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False
    
    password_salvata = r.hget(f"utenti:{username}", "password")
    if password_salvata == hash_password(password):
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
def main(loggato = False):
    while True:
        scelta = input("Vuoi (r)egistrati oppure effettuare il (l)ogin? (q) per uscire ").lower()
        
        match scelta:
            case "q":
                break
            case "r":
                username = input("Inserire l'username: ")
                password = input("Inserire la password: ")
                registrazione2(username, password)
            case "l":
                username = input("Inserire l'username: ")
                password = input("Inserire la password: ")
                loggato = login(username, password)
            case _:
                print("Scelta non valida! Riprovare...")
            
        if loggato == True:
            usernameloggato = username
            main2(usernameloggato, loggato)
            """
            valdnd = r.hget("utenti", usernameloggato, "dnd")
            if valdnd == 1:
                print("Do Not Disturb attivo")
            else:
                print("Do Not Disturb disattivo")
"""

#secondo menù
def main2(usernameloggato, loggato):
    while True:
        scelta = input("""Benvenuto! Vuoi:
                       - (a)ggiungere un nuovo contatto?
                       - (v)isualizzare lista contatti?
                       - (c)hattare con un contatto?
                       - cambiare lo stato del (d)o not disturb?
                       - (t) per tornare. """).lower()
        
        match scelta:
            
            case "t":
                loggato = False
                break
              
            case "a":
                nome_ricerca = input("Inserire l'username da trovare: ")
                #risultati = ricerca_utenti(nome_ricerca)
            
            case "v":
                pass

            case "d":
                valdnd = r.hget(f"utenti:{usernameloggato}", "dnd")
                print("valdnd", valdnd)
                if int(valdnd) == 0:
                    #r.setbit("dnd", 0, 1)
                    r.hset(f"utenti:{usernameloggato}", "dnd", 1)
                    print("Do Not Disturb attivato")
                else:
                    #r.setbit("dnd", 0, 0)
                    r.hset(f"utenti:{usernameloggato}", "dnd", 0)
                    print("Do Not Disturb disattivato")

            

#per entrare nel primo     
if __name__ == "__main__":
    main()