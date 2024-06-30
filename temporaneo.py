import redis as red
import hashlib
import datetime
import time

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


# funzione ricerca utenti
def ricerca_utenti(nome):
    cursor = 0
    risultati = []
    while True:
        cursor, keys = r.scan(cursor=cursor, match=f'utenti:{nome}*')
        for key in keys:
            if r.type(key) == 'hash':
                value = r.hget(key, "nome")
                if value is not None and nome in value:
                    risultati.append(value)
        if cursor == 0:
            break
    return risultati


# Funzione per aggiungere nuovi contatti
def aggiungi_contatti(username, ris):
    
    if ris:
        
        for i, contatto in enumerate(ris, start = 1):
                print(f"{i}. {contatto}")
    
        utentedaagg = int(input("Inserisci il numero corrispondente al contatto che vuoi aggiungere: "))
        contatti = r.lrange(f"utenti:{username}:contatti", 0, -1)  #restituisce una lista di redis associata alla chiave contatti
        contatto_selezionato = ris[utentedaagg - 1]
        if contatto_selezionato in contatti:
            print('Contatto già presente')
        else:
            contatti.append(contatto_selezionato)
            r.rpush(f"utenti:{username}:contatti", contatto_selezionato) #comando che aggiunge l'elemento nella lista
            print("i tuoi contatti sono: \n", contatti)
           #sistemare senza inserimento parziale già fatto sopra
           # mettere la condizione per il quale il contatto non sia già presente nella lista contatti
    
    else:
        print("La ricerca non è andata a buon fine, impossibile aggiungere contatti.")



# Funzione per la visualizzazione della lista dei contatti
def vis_contatti(username, chattare = False):
    contatti = r.lrange(f"utenti:{username}:contatti", 0, -1)  #recupera i contatti dell'utente
    if contatti[1:]:
        for i, contatto in enumerate(contatti[1:], start = 1):
            print(f"{i + 1}. {contatto}")
    
        if chattare:
            prova = int(input("Digita il numero del contatto con cui vuoi chattare: "))
            user2 = contatti[prova - 1]
            return user2
    
    else:
        print("La lista è vuota, lol.")


# Prima parte del menù, gestisce registrazione, login e DnD
def main(loggato = False):
    while True:
        scelta = input("Vuoi (r)egistrati oppure effettuare il (l)ogin? (q) per uscire ").lower()
        
        match scelta:
            
            case "q":
                break
            
            case "r":
                username = input("Inserire l'username: ").lower()
                password = input("Inserire la password: ")
                registrazione(username, password)
                
            case "l":
                username = input("Inserire l'username: ").lower()
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
                nome_ricerca = str(input("Inserire l'username da trovare: ")).lower()
                risultati = ricerca_utenti(nome_ricerca)
                aggiungi_contatti(usernameloggato, risultati)
            
            case "v":
                vis_contatti(usernameloggato)
                
            case "d":
                valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0) # estrazione del bitmap DnD associato all'utente loggato
                if valdnd == 0:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 1) # modifica del valore in "attivo"
                    print("Do Not Disturb attivato")
                else:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 0) # modifica del valore in "disattivato"
                    print("Do Not Disturb disattivato")
            case "c":
                user2 = vis_contatti(usernameloggato, True)
                chat(usernameloggato, user2)
            case _:
                print("Scelta non valida! Riprovare...")

#   FUNZIONE MESSAGGISTICA

#funzione messaggi
import datetime

def chat(username1, username2):
    nome_chat = username1 + " - " + username2
    inv_nome_chat = username2 + " - " + username1

    mostrare_chat(nome_chat, username2)

    # scrittura messaggio e tempo
    valdnd = r.getbit(f"utenti:{username2}:dnd", 0)
    
    if valdnd == 1:
        print("L'utente non vuole essere disturbato.")
        
    else:
        print("L'utente può essere disturbato \n")
        
        messaggio = str(input("> "))
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        score = now.timestamp()
        
        # aggiungo messaggio al sorted set
        r.zadd(f"chat:{nome_chat}", {f"> {messaggio} ({timestamp})": score})
        r.zadd(f"chat:{inv_nome_chat}", {f"< {messaggio} ({timestamp})": score})
    
def mostrare_chat(nome_chat, username2):
    print(f">> Chat con {username2} <<\n")
    if r.exists(f"chat:{nome_chat}"):
        for el in r.zrange(f"chat:{nome_chat}", 0, -1, withscores=False):
            print(el)
    else:
        return print("Non fare l'asociale e manda il primo messaggio!\n")            

#per entrare nel primo     
if __name__ == "__main__":
    main()
    
"""
FUNZIONALE:
1: Dare la possibilità di vedere solo i messaggi, senza scriverne nuovi

GRAFICO:
2: Sistemare la parte grafica (uguale alla consegna) "PRIORITA'"

OPZIONALI
1: chat a tempo (eliminazione dopo 1 min)
2: notifiche 
"""