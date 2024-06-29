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


# Funzione che gestisce la registrazione dell'utente
def registrazione(username, password):
    if r.hexists(f"utenti:{username}", "nome"):
        print("Nome Utente già utilizzato. Sceglierne un altro...")
        return False
    
    password_hash = hash_password(password)
    
    # Creazione hash con nome utente e password, lista dei contatti inizializzata con un solo elemento, bitmap per il DnD
    r.hset(f"utenti:{username}","nome",username)
    r.hset(f"utenti:{username}","password",password_hash) 
    r.lpush(f"utenti:{username}:contatti", "trovati:")
    r.setbit(f"utenti:{username}:dnd", 0,0)

    return True


# Funzione per il login dell'utente
def login(username, password):
    if not r.hexists(f"utenti:{username}", "nome"): #controlla l'esistenza dell'hash associato all'utente
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False
    
    password_salvata = r.hget(f"utenti:{username}", "password") #get della password contenuta nell'hash associato all'utente
    if password_salvata == hash_password(password):
        return True
    else:
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False

'''
# Ricerca utenti anche parziale
def ricerca_utenti(nome):
    cursor = 0
    risultati = []
    while cursor == 0:
        cursor, keys = r.scan(cursor=cursor, match = f'utenti:{nome}*')  #scan di tutte le chiavi del db
        for key in keys:
            if r.type(key) == b'hash':
                value = r.hget(key, nome)
                if value is not None:
                    value_decoded = value.decode('utf-8')
                    if nome in value_decoded:
                        risultati.append(value_decoded)
    return risultati
'''

'''
# Ricerca utenti 2
def ricerca_utenti(username):
    cursor = '0'
    ris = []
    while True:  # Il ciclo dovrebbe continuare finché la scansione non è completata
        cursor, keys = r.scan(cursor=cursor, match=f'utenti:{username}*')  # Scansiona tutte le chiavi del dbl
        for key in keys:
            value = r.hget(key, "nome")  # Ottiene il valore del campo "nome" dell'hash
            if value is not None:
                value_decoded = value.decode('utf-8')
                if username in value_decoded:
                    ris.append(value_decoded)
        if cursor == 0:  # Se il cursore è '0', la scansione è completata
            break

    return ris
 
 '''   

# funzione ricerca utenti
def ricerca_utenti(username_loggato, nome_ricerca):

  risultati = []

  # Scansione di tutti gli hash utente
  for key in r.scan(match="utenti:*", type="hash"):
    pattern = "utenti:" + nome_ricerca
    if key == f"utenti:{username_loggato}" | pattern not in key:  # Ignora la chiave dell'utente loggato
        continue
    else:
        risultati.append(r.hget(key, "nome"))

  return risultati

# Funzione per aggiungere nuovi contatti
def aggiungi_contatti(username, ris):

    for i, contatto in enumerate(ris, start = 1):
            print(f"{i}. {contatto}")

    utentedaagg = print(int("Inserisci il numero corrispondente al contatto che vuoi aggiungere: "))
    contatti = r.lrange(f"utenti:{username}:contatti", 0, -1)  #restituisce una lista di redis associata alla chiave contatti
    for el in ris:
        r.rpush(f"utenti:{username}:contatti", utentedaagg) #comando che aggiunge l'elemento nella lista
        print("i tuoi contatti sono: \n", contatti)
       #sistemare senza inserimento parziale già fatto sopra
       # mettere la condizione per il quale il contatto non sia già presente nella lista contatti 

# Funzione per la visualizzazione della lista dei contatti
def vis_contatti(username):
    contatti = r.lrange(f"utenti:{username}:contatti", 0, -1)  #recupera i contatti dell'utente
    if contatti:
        for i, contatto in enumerate(contatti[1:], start = 1):
            print(f"{i + 1}. {contatto}")

# Prima parte del menù, gestisce registrazione, login e DnD
def main(loggato = False):
    while True:
        scelta = input("Vuoi (r)egistrati oppure effettuare il (l)ogin? (q) per uscire ").lower()
        
        match scelta:
            case "q":
                break
            case "r":
                username = input("Inserire l'username: ")
                password = input("Inserire la password: ")
                registrazione(username, password)
            case "l":
                username = input("Inserire l'username: ")
                password = input("Inserire la password: ")
                loggato = login(username, password)
            case _:
                print("Scelta non valida! Riprovare...")
            
        if loggato == True:
            usernameloggato = username

            valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0)  # comando che estrae il bitmap DnD associato all'utente loggato
            if valdnd == 1:
                print("Do Not Disturb attivo")
            else:
                print("Do Not Disturb disattivo")

            main2(usernameloggato, loggato)

# Seconda parte del menù, gestisce tutte le altre azioni
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
                nome_ricerca = input(str("Inserire l'username da trovare: "))
                risultati = ricerca_utenti(usernameloggato, nome_ricerca)
                aggiungi_contatti(usernameloggato, risultati)
            
            case "v":
                valori = vis_contatti(usernameloggato)
                print(valori)
                
            case "d":
                valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0) # estrazione del bitmap DnD associato all'utente loggato
                if valdnd == 0:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 1) # modifica del valore in "attivo"
                    print("Do Not Disturb attivato")
                else:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 0) # modifica del valore in "disattivato"
                    print("Do Not Disturb disattivato")

            

#per entrare nel primo     
if __name__ == "__main__":
    main()