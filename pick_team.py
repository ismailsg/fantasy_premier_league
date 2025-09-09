import sqlite3
import pandas as pd

# 1. Connexion à la base SQLite
conn = sqlite3.connect("fpl.db")
cursor = conn.cursor()

# 2. Ajouter une colonne 'score' si elle n'existe pas
cursor.execute("PRAGMA table_info(players)")
columns = [col[1] for col in cursor.fetchall()]
if 'score' not in columns:
    cursor.execute("ALTER TABLE players ADD COLUMN score REAL")

# 3. Calculer le score : total_points + minutes/90 + selected_by_percent
cursor.execute("""
UPDATE players
SET score = total_points + selected_by_percent - now_cost 
""")
conn.commit()

# 4. Sélectionner les joueurs par position en respectant max 3 par équipe
def select_players(position):
    query = f"""
-- Sélection des meilleurs joueurs par position (score sur toute la position)
SELECT *
FROM players
WHERE position = '{position}'
ORDER BY score DESC, now_cost ASC


    """
    return pd.read_sql_query(query, conn)

# 5. Sélection finale
goalkeepers = select_players('Gardien')
defenders = select_players('Défenseur')
midfielders = select_players('Milieu')
forwards = select_players('Attaquant')

# 6. Combiner tous les joueurs
final_team = pd.concat([goalkeepers, defenders, midfielders, forwards], ignore_index=True)

print(f"Total players selected: {len(final_team)}")

# 7. Vérifier budget
budget = 100  # millions
total_cost = final_team['now_cost'].sum()
print(f"Total cost: {total_cost}M")
if total_cost > budget:
    print("Warning: budget exceeded")

# 8. Afficher l'équipe finale
print(final_team[['first_name','second_name','team','position','now_cost','total_points','score']])

# 9. Fermer la connexion
conn.close()

def build_team(all_players, total_budget=100):
    required = {
        'Gardien': (2, 0.9, 0),     # pas de contrainte
        'Défenseur':   (5, 0.25, 3.9),
        'Milieu': (5, 0.40, 4.4),
        'Attaquant':    (3, 0.26, 4.4)
    }

    final_team = []
    team_count = {}

    for position, (needed, pct_budget, reserve_last) in required.items():
        budget_limit = total_budget * pct_budget
        position_players = []
        position_cost = 0

        candidates = all_players[all_players['position'] == position]

        for _, player in candidates.iterrows():
            team = player['team']
            cost = player['now_cost']
            players_selected = len(position_players)

            if players_selected >= needed:
                break
            if team_count.get(team, 0) >= 3:
                continue
            reserve = 4.4
            
            # réserve de budget si on n'a pas encore ajouté le dernier joueur
            
            # required_reserve = reserve_last if remaining_spots == 1 else 0

            if players_selected < needed - 1:
                if position_cost + cost   > (budget_limit - reserve_last):
                    continue
            if position_cost + cost > (budget_limit ):
                continue

            position_players.append(player)
            position_cost += cost
            team_count[team] = team_count.get(team, 0) + 1
            print("position",position,position_cost)
        if len(position_players) < needed:
            print(f"Pas assez de joueurs pour {position} avec budget {budget_limit:.1f}M, restants {budget_limit - position_cost:.1f}M")

        final_team.extend(position_players)

    return pd.DataFrame(final_team)

all_players_df = pd.DataFrame(final_team)

final_team_df = build_team(all_players_df, total_budget=100)
# Afficher l'équipe finale
print(final_team_df)  