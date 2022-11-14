import pandas as pd
import requests

def get_tournament_winner_odds(API_KEY):
    url = f"""https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup_winner/odds/?apiKey={API_KEY}&regions=eu&oddsFormat=decimal"""
    data = requests.get(url)
    df = pd.read_json(data.text)
    df = pd.DataFrame(df["bookmakers"][0][0]["markets"][0]["outcomes"])
    payback = 1/(1/df["price"]).sum()
    df["prob_to_win"] = payback/df["price"]
    return df

def get_group_stage_odds(API_KEY):
    url = f"""https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal"""
    data = requests.get(url)
    df = pd.read_json(data.text)

    df["1"]=0
    df["X"]=0
    df["2"]=0
    for i in range(len(df)):
        # for j in range(len(df.loc[i,"bookmakers"])):
        if len(df.loc[i,"bookmakers"])>0:
            if df.loc[i,"home_team"]==df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][0]["name"]:
                df.loc[i,"1"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][0]["price"]
            elif df.loc[i,"away_team"]==df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][0]["name"]:
                df.loc[i,"2"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][0]["price"]
            else:
                df.loc[i,"X"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][0]["price"]
            
            if df.loc[i,"home_team"]==df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][1]["name"]:
                df.loc[i,"1"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][1]["price"]
            elif df.loc[i,"away_team"]==df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][1]["name"]:
                df.loc[i,"2"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][1]["price"]
            else:
                df.loc[i,"X"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][1]["price"]
                
            if df.loc[i,"home_team"]==df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][2]["name"]:
                df.loc[i,"1"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][2]["price"]
            elif df.loc[i,"away_team"]==df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][2]["name"]:
                df.loc[i,"2"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][2]["price"]
            else:
                df.loc[i,"X"] = df.loc[i,"bookmakers"][1]["markets"][0]["outcomes"][2]["price"]
                    
                    
    df["payback_percent"] = 1/(1/df["1"]+1/df["X"]+1/df["2"])
    df["prob1"] = df["payback_percent"]/df["1"]
    df["probx"] = df["payback_percent"]/df["X"]
    df["prob2"] = df["payback_percent"]/df["2"]
    
    return df

def get_group_stage_OU(API_KEY):
    url = f"""https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={API_KEY}&regions=eu&markets=totals&oddsFormat=decimal"""
    data = requests.get(url)
    df_OU = pd.read_json(data.text)

    df_OU["OVER"] = 0
    df_OU["UNDER"] = 0
    df_OU["GOALS"] = 0

    for i in range(len(df_OU)):
        # for j in range(len(df_OU.loc[i,"bookmakers"])):
            # if ((df_OU.loc[i,"bookmakers"][j]["key"]=="mybookieag") | (df_OU.loc[i,"bookmakers"][j]["key"]=="Unibet")):
        if len(df_OU.loc[i,"bookmakers"])>0:
            if df_OU.loc[i,"bookmakers"][0]["markets"][0]["outcomes"][0]["name"]=="over":
                df_OU.loc[i,"OVER"] = df_OU.loc[i,"bookmakers"][0]["markets"][0]["outcomes"][0]["price"]
                df_OU.loc[i,"UNDER"] = df_OU.loc[i,"bookmakers"][0]["markets"][0]["outcomes"][1]["price"]
            else:
                df_OU.loc[i,"OVER"] = df_OU.loc[i,"bookmakers"][0]["markets"][0]["outcomes"][1]["price"]
                df_OU.loc[i,"UNDER"] = df_OU.loc[i,"bookmakers"][0]["markets"][0]["outcomes"][0]["price"]
            
            df_OU.loc[i,"GOALS"] = df_OU.loc[i,"bookmakers"][0]["markets"][0]["outcomes"][1]["point"]
                
    df_OU["payback_percent"] = 1/(1/df_OU["OVER"]+1/df_OU["UNDER"])
    df_OU["prob_over"] = df_OU["payback_percent"]/df_OU["OVER"]
    df_OU["prob_under"] = df_OU["payback_percent"]/df_OU["UNDER"]
    
    return df_OU