import pandas as pd
import numpy as np

np.random.seed(42)

players = ["Marcus Thompson", "Jordan Ellis", "Kai Okafor", "Devon Price", "Sam Nwosu"]
opponents = ["Bristol Flyers", "Leicester Riders", "Cheshire Phoenix", "Sheffield Sharks", "London Lions"]
games = []

for player in players:
    for opp in opponents:
        for game_num in [1, 2]:
            fga = np.random.randint(10, 18)
            fgm = np.random.randint(4, fga)
            tpa = np.random.randint(2, 8)
            tpm = np.random.randint(0, tpa)
            fta = np.random.randint(2, 6)
            ftm = np.random.randint(1, fta)
            games.append({
                "Player":   player,
                "Opponent": opp,
                "Game":     f"{opp} G{game_num}",
                "PTS":      fgm*2 + tpm + ftm,
                "FGM":      fgm,
                "FGA":      fga,
                "3PM":      tpm,
                "3PA":      tpa,
                "FTM":      ftm,
                "FTA":      fta,
                "AST":      np.random.randint(1, 7),
                "TOV":      np.random.randint(1, 4),
                "REB":      np.random.randint(3, 10),
                "DEF_RTG":  round(np.random.normal(105, 5), 1),
            })

df = pd.DataFrame(games)
df.to_csv("data/u19_stats.csv", index=False)
print(f"Created {len(df)} rows across {len(players)} players and {len(opponents)} opponents")