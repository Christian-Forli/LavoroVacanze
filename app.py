from flask import Flask, render_template, request, redirect, url_for
import random
import pandas as pd

# Inizializzazione dell'app Flask
app = Flask(__name__)

# Carica la tabella dei Pokémon da un file CSV
tabella_pokemon = pd.read_csv('pokemon.csv')

# Punti iniziali del giocatore
punti_giocatore = 100

# Dizionario che definisce la probabilità di estrazione per ogni rarità
probabilita_rarita = {
    'Comune': 0.7,
    'Non Comune': 0.2,
    'Rara': 0.09,
    'Ultra Rara': 0.01
}

# Rotta principale: mostra la pagina iniziale
@app.route('/')
def home():
    return render_template('index.html')

# Rotta per aprire un pacchetto di carte Pokémon
@app.route('/apri_pacchetto')
def apri_pacchetto():
    global punti_giocatore
    carte_estratte = []    # Lista delle carte trovate nel pacchetto
    punti_ottenuti = 0     # Punti guadagnati con il pacchetto

    # Controlla se il giocatore ha abbastanza punti per aprire un pacchetto
    if punti_giocatore >= 10:
        punti_giocatore -= 10  # Scala il costo del pacchetto

        # Estrae 5 carte in base alle probabilità di rarità
        for _ in range(5):
            rarita_estratta = random.choices(
                list(probabilita_rarita.keys()),
                weights=probabilita_rarita.values(),
                k=1
            )[0]
            # Seleziona la prima carta della rarità estratta
            carta_estratta = tabella_pokemon[tabella_pokemon['Rarità'] == rarita_estratta].iloc[0].to_dict()
            carte_estratte.append(carta_estratta)

            # Assegna punti extra in base alla rarità della carta trovata
            if rarita_estratta == 'Comune':
                punti_ottenuti += 2
            elif rarita_estratta == 'Non Comune':
                punti_ottenuti += 5
            elif rarita_estratta == 'Rara':
                punti_ottenuti += 10
            elif rarita_estratta == 'Ultra Rara':
                punti_ottenuti += 20

        punti_giocatore += punti_ottenuti  # Aggiunge i punti ottenuti
        aggiorna_collezione(carte_estratte)  # Aggiorna il file della collezione
        # Mostra il risultato all'utente
        return render_template('index.html', output=f"Hai guadagnato {punti_ottenuti} punti.", pacchetto=carte_estratte)
    else:
        # Messaggio se non ci sono abbastanza punti
        return render_template('index.html', output="Non hai abbastanza punti.")

# Rotta per mostrare tutte le carte trovate dal giocatore
@app.route('/mostra_collezione')
def mostra_intera_collezione():
    try:
        # Legge la collezione dal file CSV
        collezione_completa = pd.read_csv('carte_trovate.csv').to_dict(orient='records')
        return render_template('index.html', output="Ecco la tua collezione:", pacchetto=collezione_completa)
    except FileNotFoundError:
        # Messaggio se la collezione non esiste ancora
        return render_template('index.html', output="Nessuna collezione trovata.")

# Rotta per mostrare i punti attuali del giocatore
@app.route('/mostra_punti')
def mostra_punti():
    return render_template('index.html', output=f"Hai {punti_giocatore} punti.")

# Funzione per aggiornare il file della collezione con le nuove carte trovate
def aggiorna_collezione(carte_nuove):
    try:
        # Se il file esiste, aggiunge le nuove carte a quelle già presenti
        collezione = pd.read_csv('carte_trovate.csv')
        collezione = pd.concat([collezione, pd.DataFrame(carte_nuove)], ignore_index=True)
    except FileNotFoundError:
        # Se il file non esiste, lo crea con le nuove carte
        collezione = pd.DataFrame(carte_nuove)
    # Salva la collezione aggiornata su disco
    collezione.to_csv('carte_trovate.csv', index=False)

# Avvia l'applicazione Flask in modalità debug
if __name__ == '__main__':
    app.run(debug=True)