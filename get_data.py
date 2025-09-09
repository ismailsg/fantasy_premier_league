import requests
import pandas as pd

# 1. Récupération des données depuis l'API FPL
url = "https://fantasy.premierleague.com/api/bootstrap-static/"
response = requests.get(url)
data = response.json()

# 2. Extraire les données des joueurs
players = data['elements']

# 3. Sélection des champs utiles
player_list = []

positions = {1: "Gardien", 2: "Défenseur", 3: "Milieu", 4: "Attaquant"}
for player in players:
    player_info = {
        "id": player["id"],
        "first_name": player["first_name"],
        "second_name": player["second_name"],
        "team": player["team"],
        "position": positions[player["element_type"]],
        "now_cost": player["now_cost"] / 10,  # en millions
        "total_points": player["total_points"],
        "minutes": player["minutes"],
        "goals_scored": player["goals_scored"],
        "assists": player["assists"],
        "clean_sheets": player["clean_sheets"],
        "selected_by_percent": player["selected_by_percent"]
    }
    player_list.append(player_info)

# 4. Convertir en DataFrame
df = pd.DataFrame(player_list)

# 5. Enregistrer en CSV (facultatif)
df.to_csv("fpl_players.csv", index=False)

# 6. Afficher les 5 premiers joueurs
print(df.head())
