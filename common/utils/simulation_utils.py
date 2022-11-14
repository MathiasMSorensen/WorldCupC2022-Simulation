import scipy as scipy
import scipy.stats
import numpy as np

class WorldCupMatch(object):
    def __init__(self,team1,team2):
        self.played = False
        self.penalties = False
        self.team1 = team1
        self.team2 = team2
        self.eloK = 60 # for world cup (see http://www.eloratings.net/about)
        self.run_hot = True
        
    def __repr__(self):
        return "Match %s vs %s." % (self.team1.name, self.team2.name)
        
    
class WorldCupGroup(object):
    def __init__(self,name,teams):
        self.group_name = name # group name
        self.group_teams = teams # list of group teams
        self.build_group_matches()        
        
    def __repr__(self):
        teams = ""
        for t in self.group_teams:
            teams = teams + t.name + ", "
        return f"""group %s contains %s" % (self.group_name,teams)"""     
    
    def build_group_matches(self):
        self.matches = []
        # assume group matches in every group  are in the same order.
        self.matches.append(WorldCupMatch(self.group_teams[0],self.group_teams[1]))
        self.matches.append(WorldCupMatch(self.group_teams[2],self.group_teams[3]))
        self.matches.append(WorldCupMatch(self.group_teams[0],self.group_teams[2]))
        self.matches.append(WorldCupMatch(self.group_teams[1],self.group_teams[3]))
        self.matches.append(WorldCupMatch(self.group_teams[3],self.group_teams[0]))
        self.matches.append(WorldCupMatch(self.group_teams[1],self.group_teams[2]))
    

class WorldCupSim(object):
    def __init__(self,group_names,teams,df_group_stage, df_winner, verbose):
        self.group_names = group_names
        self.teams = teams
        self.groups = []
        self.df_group_stage = df_group_stage
        self.df_winner = df_winner
        self.verbose = verbose
                
    def get_probs_group_stage(self, team1, team2):
        if len(self.df_group_stage.loc[((self.df_group_stage["home_team"]==team1) & ((self.df_group_stage["away_team"]==team2))), ['prob1', 'probx', 'prob2']])>0:
            return self.df_group_stage.loc[((self.df_group_stage["home_team"]==team1) & ((self.df_group_stage["away_team"]==team2))), ['prob2', 'probx', 'prob1']].values[0]
        else:
            return self.df_group_stage.loc[((self.df_group_stage["home_team"]==team2) & ((self.df_group_stage["away_team"]==team1))), ['prob1', 'probx', 'prob2']].values[0]

    def play_game_group_stage(self, probs, m):
        bernoulli = np.random.uniform(low=0.0, high=1.0, size=None)
        res = (probs.cumsum()>bernoulli).sum()
        if res == 1:
            m.team1.points += 3
            m.team2.points += 0
        elif res==2:
            m.team1.points += 1
            m.team2.points += 1
        else: 
            m.team1.points += 0
            m.team2.points += 3
            
    def get_probs_finals(self, team1, team2):
        temp_odds1 = self.df_winner.loc[self.df_winner["name"]==team1,"prob_to_win"].values[0]
        temp_odds2 = self.df_winner.loc[self.df_winner["name"]==team2,"prob_to_win"].values[0]
        
        max_odds = max(temp_odds1, temp_odds2)
        # see estimate_draw_probabilities.ipynb
        draw_prob = 0.48757177-0.29805232*max_odds
        team1_prob = (1-draw_prob)*temp_odds1/(temp_odds1+temp_odds2)
        team2_prob = (1-draw_prob)*temp_odds2/(temp_odds1+temp_odds2)
        
        return np.array([team1_prob, draw_prob, team2_prob]).cumsum()

    def play_game_finals(self, prob,m):
        bernoulli = np.random.uniform(low=0.0, high=1.0, size=None)
        if (prob<bernoulli).sum()==0:
            m.winner = m.team1 
        elif (prob<bernoulli).sum()==1:
            # if draw, game becomes 50/50
            bernoulli = np.random.uniform(low=0.0, high=1.0, size=None)
            m.winner = m.team1 if bernoulli < 0.5 else m.team2
        else:
            m.winner = m.team2
        
    def runsim(self):
        for g in self.group_names:
            group_teams = [t for t in self.teams if t.group==g]
            self.groups.append(WorldCupGroup(g,group_teams))
            
        for g in self.groups:
            for m in g.matches:
                g.probs = self.get_probs_group_stage(m.team1.name, m.team2.name)
                self.play_game_group_stage(g.probs, m)
            
            g.table = sorted(g.group_teams,key = lambda team: (team.points), reverse=True)        
            g.winner = g.table[0]        
            g.runner = g.table[1]    
            
        self.KnockOut = WorldCupKnockOut(self.groups)
        
        self.KnockOut.Round16()        
        for m in self.KnockOut.R16matches:
            prob = self.get_probs_finals(m.team1.name,m.team2.name)
            self.play_game_finals(prob, m)
            
        self.KnockOut.QuarterFinal()
        for m in self.KnockOut.QFmatches:
            prob = self.get_probs_finals(m.team1.name,m.team2.name)
            self.play_game_finals(prob, m)
            
        self.KnockOut.SemiFinal()
        for m in self.KnockOut.SFmatches:
            prob = self.get_probs_finals(m.team1.name,m.team2.name)
            self.play_game_finals(prob, m)
            
        self.KnockOut.Final()
        for m in self.KnockOut.Final:
            prob = self.get_probs_finals(m.team1.name,m.team2.name)
            self.play_game_finals(prob, m)
            
            
class WorldCupTeam(object):
    def __init__(self,group,name):
        self.name = name # Country
        self.group = group
        self.group_matches = 0
        self.total_matches = 0
        self.points = 0
        self.goals_for = 0
        self.goals_against = 0

    def __repr__(self):
        return "%s, %s, %s" % (self.name,self.group)
    
    
class WorldCupKnockOut(object):
    def __init__(self,groups):
        self.groups = groups
        
    def Round16(self):
        # Set up Round of 16 matches based on groups
        self.R16matches = []
        self.R16teamnames = []
        self.GroupWinners = []
        self.R16matches.append(WorldCupMatch(self.groups[0].winner,self.groups[1].runner)) #1A vs 2B
        self.R16matches.append(WorldCupMatch(self.groups[2].winner,self.groups[3].runner)) #1C vs 2D
        self.R16matches.append(WorldCupMatch(self.groups[1].winner,self.groups[0].runner)) #1B vs 2A
        self.R16matches.append(WorldCupMatch(self.groups[3].winner,self.groups[2].runner)) #1D vs 2C
        self.R16matches.append(WorldCupMatch(self.groups[4].winner,self.groups[5].runner)) #1E vs 2F
        self.R16matches.append(WorldCupMatch(self.groups[6].winner,self.groups[7].runner)) #1G vs 2H
        self.R16matches.append(WorldCupMatch(self.groups[5].winner,self.groups[4].runner)) #1F vs 2E
        self.R16matches.append(WorldCupMatch(self.groups[7].winner,self.groups[6].runner)) #1H vs 2G
        # Record group winners and round of 16 team names (for metrics)
        for group in self.groups:
            self.GroupWinners.append(group.winner.name)
        for m in self.R16matches:
            self.R16teamnames.append(m.team1.name)
            self.R16teamnames.append(m.team2.name)
    
    def ManuallySetRound16(self,R16teams):
        # Manually set Round of 16 matches
        self.R16matches = []
        self.R16teamnames = []
        for i in np.arange(0,15,step=2):
            self.R16matches.append( WorldCupMatch(R16teams[i], R16teams[i+1] ) )
        for m in self.R16matches:
            self.R16teamnames.append(m.team1.name)
            self.R16teamnames.append(m.team2.name)
    
    def QuarterFinal(self):
        # Quarter Final Matches
        self.QFmatches = []
        self.QFteamnames = []
        self.QFmatches.append(WorldCupMatch( self.R16matches[0].winner, self.R16matches[1].winner) ) # 1A/2B vs 1C/2D
        self.QFmatches.append(WorldCupMatch( self.R16matches[2].winner, self.R16matches[3].winner) ) # 1B/2A vs 1D/2C
        self.QFmatches.append(WorldCupMatch( self.R16matches[4].winner, self.R16matches[5].winner) ) # 1E/2F vs 1G/2H
        self.QFmatches.append(WorldCupMatch( self.R16matches[6].winner, self.R16matches[7].winner) ) # 1F/2E vs 1H/2G
        for m in self.QFmatches:
            self.QFteamnames.append(m.team1.name)
            self.QFteamnames.append(m.team2.name)
        
    def SemiFinal(self):
        # Semi final matches
        self.SFmatches = []
        self.SFteamnames = []
        self.SFmatches.append(WorldCupMatch( self.QFmatches[0].winner, self.QFmatches[2].winner) ) # 1A/2B/1C/2D vs 1E/2F/1G/2H
        self.SFmatches.append(WorldCupMatch( self.QFmatches[1].winner, self.QFmatches[3].winner) ) # 1B/2A/1D/2C vs 1F/2E/1H/2G
        for m in self.SFmatches:
            self.SFteamnames.append(m.team1.name)
            self.SFteamnames.append(m.team2.name)
    
    def Final(self):
        # Final
        self.Final = [WorldCupMatch( self.SFmatches[0].winner, self.SFmatches[1].winner)]
        self.Finalteamnames = [self.Final[0].team1.name, self.Final[0].team2.name]