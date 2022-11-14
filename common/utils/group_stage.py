def get_groups():
    import pandas as pd

    odds = []
    team = []
    for i in range(294,294+32):
        str_temp = soup.find_all('li')[i].text
        if '+' in str_temp:
            team.append(str_temp.split('+')[0].strip())
            odds.append(float(str_temp.split('+')[1]))
        else:
            team.append(str_temp.split('-')[0].strip())
            odds.append(-float(str_temp.split('-')[1]))
            
    df_grop_stage = pd.concat([pd.Series(team),pd.Series(odds)],axis=1)
    df_grop_stage.columns = ["Team","odds_to_win"]

    import numpy as np
    df_grop_stage["odds_to_win"] = np.where(df_grop_stage["odds_to_win"]>0,(df_grop_stage["odds_to_win"] + 100)/100,(-100/df_grop_stage["odds_to_win"])+1)

    group_stage =['A','B','C','D','E','F','G','H']
    loop_list = list(range(0,33,4))
    df_grop_stage["group"] = "A"
    for i in range(8):
        df_grop_stage.loc[loop_list[i]:loop_list[i+1],"group"] = group_stage[i]
        
    df_grop_stage['pb_percent'] = 1/df_grop_stage["odds_to_win"]
    df_grop_stage['temp_column'] = 1/df_grop_stage.groupby('group')['pb_percent'].transform('sum')
    df_grop_stage["prob_to_win"]=df_grop_stage["temp_column"]/df_grop_stage["odds_to_win"]
    df_grop_stage.drop(columns = {"pb_percent","temp_column"}, inplace = True)

    df_grop_stage[["Team","group"]].to_csv("common/utils/df_groups.csv")
    
        