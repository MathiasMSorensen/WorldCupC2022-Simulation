import urllib.request, json
import pandas as pd

def get_holdet_data():
    cols = ["name1", "name2" ,"name3","name4","name5","name6", "name7"]
    df_final = pd.DataFrame(columns = cols)
    for j in range(40):
        try:
            url = f"""https://www.holdet.dk/handlers/tradedata.ashx?language=da&game=2022-world-manager&userteam=&partial-name=&positions=&team=&formation=&minimum-value=0&maximum-value=0&lineup=&original-lineup=&sort=&addable-only=false&direction=-1&page={j}&include-headers=true&include-formations=true&include-lineup=true&include-fields=true&r=1666622443519"""
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            for i in range(len(data["Dataset"]["Items"])):
                # cols = ["name1", "name2" ,"name3","name4","name5","name6", "name7","country"]
                df_new = pd.DataFrame()
                df_new.loc[i,"name1"] = data["Dataset"]["Items"][i]["Values"][1]
                df_new.loc[i,"name2"] = data["Dataset"]["Items"][i]["Values"][2]
                df_new.loc[i,"name3"] = data["Dataset"]["Items"][i]["Values"][3]
                df_new.loc[i,"name4"] = data["Dataset"]["Items"][i]["Values"][4]
                df_new.loc[i,"name5"] = data["Dataset"]["Items"][i]["Values"][5]
                df_new.loc[i,"name6"] = data["Dataset"]["Items"][i]["Values"][6]
                df_new.loc[i,"name7"] = data["Dataset"]["Items"][i]["Values"][7]
                df_new.loc[i,"country"] = data["Dataset"]["Items"][i]["Values"][9]
                df_new.loc[i,"price"] = data["Dataset"]["Items"][i]["Values"][16]
                df_new.loc[i,"position"] = data["Dataset"]["Items"][i]["Texts"][15]
                df_final = pd.concat([df_final, df_new])
        except:
            print(f"""no such page: {j}""")
            
            
    return df_final