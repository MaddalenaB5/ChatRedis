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

'''
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
'''
def registrazione2(username, password):
    if r.hexists(f"utenti:{username}", "nome"):
        print("Nome Utente già utilizzato. Sceglierne un'altro...")
        return False
    
    password_hash = hash_password(password)
    
    r.hset(f"utenti:{username}","nome",username)
    r.hset(f"utenti:{username}","password",password_hash) 
    r.lpush(f"utenti:{username}:contatti", "trovati:")
    r.setbit(f"utenti:{username}:dnd", 0,0)

    return True

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


#ricerca utenti anche parziale
def ricerca_utenti(nome):
    cursor = 0
    risultati = []
    while cursor == 0:
        cursor, keys = r.scan(cursor=cursor, match = f'utenti:{nome}*')
        for key in keys:
            if r.type(key) == b'hash':
                value = r.hget(key, nome)
                if value is not None:
                    value_decoded = value.decode('utf-8')
                    if nome in value_decoded:
                        risultati.append(value_decoded)
    return risultati


# Funzione per aggiungere nuovi contatti
def aggiuntacont(risultati, username):
    utentedaagg = print(str("quale scegli?: "))
    contatti = r.lrange("contatti", 0, -1)
    for el in risultati:
        if utentedaagg not in contatti and el == utentedaagg:
            r.rpush(f"utenti:{username}:contatti", utentedaagg)
            print("i tuoi contatti sono: \n", contatti)
        else:
            print("errore")
            break

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

            valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0)
            if valdnd == 1:
                print("Do Not Disturb attivo")
            else:
                print("Do Not Disturb disattivo")

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
                nome_ricerca = input(str("Inserire l'username da trovare: "))
                risultati = ricerca_utenti(nome_ricerca)
                print("risultati", risultati)
            
            case "v":
                pass

            case "d":
                valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0)
                if valdnd == 0:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 1)
                    print("Do Not Disturb attivato")
                else:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 0)
                    print("Do Not Disturb disattivato")

            

#per entrare nel primo     
if __name__ == "__main__":
    main()