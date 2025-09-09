import pandas as pd
import sqlite3

# 1. Charger le fichier CSV
df = pd.read_csv("fpl_players.csv")

# 2. Connexion à SQLite (crée fpl.db si elle n'existe pas)
conn = sqlite3.connect("fpl.db")

# 3. Enregistrer dans une table SQL (remplace si existe déjà)
df.to_sql("players", conn, if_exists="replace", index=False)

# 4. Vérification simple
cursor = conn.cursor()
cursor.execute("SELECT * FROM players LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(row)

# 5. Fermer la connexion
conn.close()
