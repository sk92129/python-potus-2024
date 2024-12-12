import requests
import pandas as pd
import matplotlib.pyplot as plt
import json

def get_state_data(state_url):
    try:
        response = requests.get(state_url)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching data for {state_url}: {e}")
        return None

def get_leader(candidates):
    try:
        for candidate in candidates:
            if candidate.get("leader"):
                total = candidate.get("votes").get("total")
                name = candidate.get("nyt_id")
                return name, total
        return None, None
    except Exception as e:
        print(f"Error fetching data for {candidates}: {e}")
        return None


def get_candidate_votes(state_data):
    reports = {}
    outcomeArr= {}
    for race in state_data.get("races", []):
        type = race.get("type")
        office = race.get("office")
        if (type == "General") and (office == "President"):
            #print("found potus")
            reportingUnits = race.get("reporting_units", [])
            outcome = race.get("outcome")
            who_won = outcome.get("won", [])
            outcomeArr["who"] = who_won[0]
            outcomeArr["electoral_votes"] = outcome.get("electoral_votes", [])
            for unit in reportingUnits:
                #print("processing unit")
                candidates = unit.get("candidates", [])
                leader_name, leader_votes = get_leader(candidates)
                # the leader data can be None
                data = {"name": unit.get("name"),"level": unit.get("level"), "total_votes": unit.get("total_votes"), "expected": unit.get("total_expected_vote"), "leader": leader_name, "leader_votes": leader_votes}
                reports[unit.get("nyt_id")] = data
            #print("got all the potus from this state")
            break

    outcomeArr["reports"] = reports
    return outcomeArr

def main():
    base_url = "https://static01.nyt.com/elections-assets/pages/data/2024-11-05/results-"
    states = [
        "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida", "georgia",
        "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland",
        "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new-hampshire", "new-jersey",
        "new-mexico", "new-york", "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode-island", "south-carolina",
        "south-dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west-virginia", "wisconsin", "wyoming"
    ]

    candidate_votes = {"trump-d": {}, "harris-k": {}}
    for state in states:
        state_url = f"{base_url}{state}.json"
        state_data = get_state_data(state_url)
        if state_data:
            outcome = get_candidate_votes(state_data)
            who = outcome.get("who")
            candidate_votes[who][state] = outcome.get("electoral_votes")


    # Save to CSV
    trump_df = pd.DataFrame(list(candidate_votes["trump-d"].items()), columns=["State", "Trump Votes"])
    harris_df = pd.DataFrame(list(candidate_votes["harris-k"].items()), columns=["State", "Harris Votes"])
    combined_df = pd.merge(trump_df, harris_df, on="State", how="outer")
    combined_df.to_csv("election_results_2024_candidates.csv", index=False)
    print("Data saved to election_results_2024_candidates.csv")

    # Print top 20 rows
    print(combined_df.head(20))

    # Plot histogram
    plt.figure(figsize=(12, 6))
    states = list(candidate_votes["trump-d"].keys())
    trump_values = list(candidate_votes["trump-d"].values())
    harris_values = list(candidate_votes["harris-k"].values())

    bar_width = 0.4
    index = range(len(states))

    plt.bar(index, trump_values, bar_width, label="Trump", color='red')
    plt.bar([i + bar_width for i in index], harris_values, bar_width, label="Harris", color='blue')

    plt.xticks([i + bar_width / 2 for i in index], states, rotation=90)
    plt.title("Total Votes for Trump and Harris by State in 2024 POTUS Election")
    plt.xlabel("States")
    plt.ylabel("Total Votes")
    plt.legend()
    plt.tight_layout()
    plt.savefig("election_results_histogram_candidates.png")
    plt.show()

if __name__ == "__main__":
    main()
