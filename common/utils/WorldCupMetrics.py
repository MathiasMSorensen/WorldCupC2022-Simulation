# -*- coding: utf-8 -*-
"""
A collection of (poorly-commented) plotting and output routines

@author: @eightyfivepoint
"""

import numpy as np
from scipy.stats import mode
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

import pandas as pd
import plotly
import plotly.graph_objs as go


def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#4B8BBE','#306998','#FFE873','#4F9119','#646464']
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp =  list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp
        
    # remove duplicates from labelList
    labelList = list(dict.fromkeys(labelList))
    
    # define colors based on number of levels
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]]*colorNum
        
    # transform df into a source-target pair
    for i in range(len(cat_cols)-1):
        if i==0:
            sourceTargetDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            sourceTargetDf.columns = ['source','target','count']
        else:
            tempDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            tempDf.columns = ['source','target','count']
            sourceTargetDf = pd.concat([sourceTargetDf,tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source','target']).agg({'count':'sum'}).reset_index()
        
    # add index for source-target pair
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))
    
    # creating the sankey diagram
    data = dict(
        type='sankey',
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(
            color = "black",
            width = 0.5
          ),
          label = labelList,
          color = colorList
        ),
        link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count']
        )
      )
    
    layout =  dict(
        title = title,
        font = dict(
          size = 10
        )
    )
       
    fig = dict(data=[data], layout=layout)
    return fig

def make_sankey(teamname, sims):
# trace probability of a team progressing through the tournament
    Nsims = float(len(sims))
    stages = ['GRP','R16','QF','SF','Final','Winner']
    group_stages = list(np.full(int(Nsims),"Group D"))
    R16_opponents = list(np.full(int(Nsims),"null"))
    QF_opponents = list(np.full(int(Nsims),"null"))
    SF_opponents = list(np.full(int(Nsims),"null"))
    Final_opponents = list(np.full(int(Nsims),"null"))
    count = 0
    for count, s in enumerate(sims):
        for i in range(len(s.KnockOut.R16matches)):
            if teamname==s.KnockOut.R16matches[i].team1.name: 
                R16_opponents[count] = s.KnockOut.R16matches[i].team2.name + " - R16"
            elif teamname==s.KnockOut.R16matches[i].team2.name: 
                R16_opponents[count] = s.KnockOut.R16matches[i].team1.name + " - R16"
        
        for i in range(len(s.KnockOut.QFmatches)):
            if teamname==s.KnockOut.QFmatches[i].team1.name: 
                QF_opponents[count] = s.KnockOut.QFmatches[i].team2.name + " - QF"
            elif teamname==s.KnockOut.QFmatches[i].team2.name: 
                QF_opponents[count] = s.KnockOut.QFmatches[i].team1.name + " - QF"
                
        for i in range(len(s.KnockOut.SFmatches)):
            if teamname==s.KnockOut.SFmatches[i].team1.name: 
                SF_opponents[count] = s.KnockOut.SFmatches[i].team2.name + " - SF"
            elif teamname==s.KnockOut.SFmatches[i].team2.name: 
                SF_opponents[count] = s.KnockOut.SFmatches[i].team1.name + " - SF"
        
        for i in range(len(s.KnockOut.Final)):
            if teamname==s.KnockOut.Final[i].team1.name: 
                Final_opponents[count] = s.KnockOut.Final[i].team2.name + " - Final"
            elif teamname==s.KnockOut.Final[i].team2.name: 
                Final_opponents[count] = s.KnockOut.Final[i].team1.name + " - Final"
                
        count += 1 

    df_finals = pd.concat([pd.Series(group_stages),
                        pd.Series(R16_opponents),
                        pd.Series(QF_opponents),
                        pd.Series(SF_opponents),
                        pd.Series(Final_opponents)], axis = 1)

    df_finals.columns = ["Group","R16", "QF", "SF", "Final"]
    df_finals["count"] = 0
    df_finals = df_finals.groupby(["Group","R16", "QF", "SF", "Final"], sort=False).size().reset_index(name='count')
    df_finals[["QF", "SF", "Final"]] = df_finals[["QF", "SF", "Final"]].replace('null', np.nan)
    df_finals["R16"] = df_finals["R16"].replace('null', "Not in playoffs")
    
    fig = genSankey(df_finals, cat_cols = ["Group","R16", "QF", "SF", "Final"], value_cols = "count", title = "Denmarks road to the final")
    plotly.offline.plot(fig, validate=False)
    
def SetShortNames():
    # For plot axis labels
    ShortNames = {
        'Netherlands': 'NLD',
        'Ecuador':'ECU',
        'Qatar':'QAT',
        'USA':'USA',
        'Wales':'WAL',
        'Canada': 'CAN',
        'Cameroon':'CAM',
        'Ghana': 'GHA',
        'Russia':'RUS',
        'Uruguay':'URU',
        'Egypt':'EGP',
        'Saudi Arabia':'SAU',
        'Portugal':'POR',
        'Spain':'SPA',
        'Iran':'IRA',
        'Morocco':'MOR',
        'France':'FRA',
        'Peru':'PER',
        'Denmark':'DEN',
        'Australia':'AUS',
        'Argentina':'ARG',
        'Croatia':'CRO',
        'Iceland':'ICE',
        'Nigeria':'NIG',
        'Brazil':'BRA',
        'Switzerland':'SWI',
        'Costa Rica':'COS',
        'Serbia':'SER',
        'Germany':'GER',
        'Mexico':'MEX',
        'Sweden':'SWE',
        'Korea Republic':'KOR',
        'South Korea':'KOR',
        'Belgium':'BEL',
        'England':'ENG',
        'Tunisia':'TUN',
        'Panama':'PAN',
        'Poland':'POL',
        'Colombia':'COL',
        'Senegal':'SEN',
        'Japan':'JAP'
    }
    return ShortNames

def SimWinners(sims,teamnames,includeOdds=False, randsims=None, save=True):
    # Probability of top-16 favourites each winning tournament
    ShortNames = SetShortNames()
    nTeamsPlot = 16 # number of teams to plot
    Nsims = len(sims)
    Winners = [x.KnockOut.Final[0].winner.name for x in sims]
    WinnerFreq = [(name,Winners.count(name)) for name in teamnames]
    WinnerFreq = sorted( WinnerFreq, key = lambda x : x[1], reverse=True)
    WinnerFreq = [(n,c) for (n,c) in WinnerFreq if c > 0]
    WinnerFreq = WinnerFreq[0:nTeamsPlot]
    WinnerNames = [x[0] for x in WinnerFreq]
    fig, ax = plt.subplots(figsize=(10, 5))   
    ind = np.arange(len(WinnerFreq))
    width = 0.6
    WinnerProp = np.array([x[1] for x in WinnerFreq],'float')/float(Nsims)
    ax.bar(ind+(1-width)/2., 100.*WinnerProp, width=width, color='r', linewidth=0, alpha = 0.3,label='Simulations') 
    ax.set_ylabel('Prob of Winning Tournament (%)',fontsize=12)
    ax.set_xticks(ind + 0.5)
    ax.set_xticklabels([ShortNames[name] for name in WinnerNames],fontsize=12)
    ax.set_xlim(0,nTeamsPlot)
    ax.yaxis.grid()
    #ax.legend(loc='best',framealpha=0.2,frameon=False,fontsize=12, numpoints=1)
    #ax.get_xticklabels().set_fontsize(20)
    fig.suptitle("WC2022 Favourites",fontsize=14)
    if save:
        figname = 'SimWinners.png'
        plt.savefig(figname,dpi=400,bbox_inches='tight',pad_inches=0.1) 
    
    
def SimFinalists(sims,teamnames,ShortNames):
   # Find most frequent finalists
   Finalists = [(x.KnockOut.Final[0].team1.name,x.KnockOut.Final[0].team2.name) for x in sims]
   F = [(x[0],x[1],Finalists.count(x)) for x in Finalists]
   F = sorted( F, key = lambda x : x[2], reverse=True)
   # get uniques
   FinalistFreq = []
   for f in F:
       if f not in FinalistFreq:
           FinalistFreq.append(f)
   print( FinalistFreq)

def TraceTeam(sims,teamname, verbose=False):
    # trace probability of a team progressing through the tournament
    Progress = []
    Nsims = float(len(sims))
    stages = ['GRP','R16','QF','SF','Final','Winner']
    for s in sims:
        p = 0
        if teamname in s.KnockOut.R16teamnames: p += 1
        if teamname in s.KnockOut.QFteamnames: p += 1
        if teamname in s.KnockOut.SFteamnames: p += 1
        if teamname in s.KnockOut.Finalteamnames: p += 1
        if teamname == s.KnockOut.Final[0].winner.name: p += 1
        Progress.append(stages[p])    
    ProgressFreq = [Progress.count(s)/Nsims for s in stages]
    assert np.isclose( np.sum(ProgressFreq),1.,atol=0.001,rtol=0.0)
    ProgressFreq = 1-np.cumsum(ProgressFreq)
    Progress = (teamname,ProgressFreq[0],ProgressFreq[1],ProgressFreq[2],ProgressFreq[3],ProgressFreq[4]) 
    if verbose:
        print ("%s: %1.2f,%1.2f,%1.2f,%1.2f,%1.2f" % Progress)
    return Progress


def ExpectedGroupFinishes(sims,group_names, group_name):
    # Probability of each team in a group finishing in each position
    Nsims = len(sims)
    ind = group_names.index(group_name)
    Teams = sims[0].groups[ind].group_teams
    Table = {}
    for team in Teams:
        Table[team.name] = np.zeros(4)
    for i in range(0,Nsims):
        # sims[i].groups[ind].build_table
        for t,p in zip(sims[i].groups[ind].table,range(0,4)):
            Table[t.name][p] += 1
    n = float(Nsims)
    Table = [(t,Table[t][0]/n,Table[t][1]/n,Table[t][2]/n,Table[t][3]/n) for t in Table.keys()]
    Table = sorted(Table,key = lambda x: x[1]+x[2],reverse=True)
    return Table
    
def ExpectedGroupFinishesPlot(sims,group_names,save=True):
    # Make group table probability plot
    Tables = [ExpectedGroupFinishes(sims,group_names,group) for group in group_names]
    fig,axes = plt.subplots(nrows=4,ncols=2,figsize=(10, 9))
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=0.45, hspace=0.4)
    nGroupTeams = 4
    for Table,ax,group in zip(Tables,axes.flatten(),group_names):
        grid = np.zeros((nGroupTeams,nGroupTeams),dtype=float)
        gridmax = 0.8
        gridmin = 0
        for i in range(nGroupTeams):
            for j in range(nGroupTeams):
                grid[i,j] = np.round( Table[i][j+1] ,3)
                if grid[i,j] <0.01:
                    grid[i,j] = gridmin
        Y = np.arange(nGroupTeams+0.5, 0, -1)
        X = np.arange(0.5, nGroupTeams+1, 1)
        X, Y = np.meshgrid(X, Y)
        cmap = plt.get_cmap('Blues')#cool, Reds, Purples
        levels = MaxNLocator(nbins=gridmax/0.01).tick_values(gridmin,gridmax)# grid.max())
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
        im = ax.pcolormesh(X, Y, grid,cmap=cmap,norm=norm)
        ax.set_xlim(0.5,nGroupTeams+0.5)
        ax.set_ylim(0.5,nGroupTeams+0.5)
        teams = [t[0] for t in Table]
        for i in range(nGroupTeams): 
            if teams[i]=='Korea Republic' or teams[i]=='South Korea':
                teams[i] = 'S. Korea'
        ax.set_yticks(np.arange(1,nGroupTeams+1,1))
        ax.set_xticks(np.arange(1,nGroupTeams+1,1))
        ax.set_yticklabels(teams[::-1],color='r',fontsize=11)
        ax.set_xticklabels( ['1st', '2nd', '3rd', '4th'], color='k', fontsize=11 )
        ax.tick_params(axis=u'both', which=u'both',length=0)
        ax.set_title("Group " + group,color='r')
        pthresh=0.01
        Qual = np.array( np.round(100*np.sum( grid[:,:2], axis=1 ),0), dtype=int)
        for i in range(nGroupTeams):
            for j in range(nGroupTeams):
                if grid[i,j]>=pthresh:
                    s = "%1.0d" % (round(100*grid[i,j],0))
                    ax.text(j+0.9,nGroupTeams-i-0.15,s,fontsize=10,color='k')
        fig.set_facecolor('0.95')
        # twin axis
        ax2 = ax.twinx()
        ax2.set_ylim((0.5,0.5 + nGroupTeams ))
        ax2.set_yticks(np.arange(1,nGroupTeams+1,1))
        ax2.set_yticklabels( Qual[::-1] ,color='k')
        ax2.text(3.55+0.9,nGroupTeams+0.65,'Qual',fontsize=11,color='k')
        ax2.tick_params(axis=u'both', which=u'both',length=0)
    if save:
        figname = 'ExpectedGroupFinishes.png'
        plt.savefig(figname,dpi=400,bbox_inches='tight',pad_inches=0.1) 
        

def ExpectedGroupResults(sims,group_names, group_name):
    # Find most frequent results in group stage
    Nsims = len(sims)
    ind = group_names.index(group_name)
    resultslist = np.zeros( (Nsims,6),dtype = 'int')
    for i in range(0,Nsims):
        resultslist[i,:] = [100*m.team1_goals+m.team2_goals for m in sims[i].groups[ind].matches]
    most_freq = [ (int(x/100),int(x % 100)) for x in mode(resultslist)[0][0] ]
    # NOW PRINT RESULTS
    print (" GROUP %s RESULTS " % (group_name))
    for i in range(len(most_freq)):
        team1 = sims[0].groups[ind].matches[i].team1.name
        team2 = sims[0].groups[ind].matches[i].team2.name
        print ("%s %s v %s %s" % (team1,most_freq[i][0],most_freq[i][1],team2))

def ExpectedKnockOutResults(sims,stage,Nmatches):
    # Find most frequent results in each knock-out match
    Nsims = float(len(sims))
    matches = 's.KnockOut.' + stage
    print (matches     )
    for i in range(Nmatches):
        resultslist = []
        for s in sims:
            m = eval(matches)
            resultslist.append((m[i].team1.name,m[i].team1_goals,m[i].team2.name,m[i].team2_goals))
        R = [(r[0],r[1],r[2],r[3],resultslist.count(r)/Nsims) for r in resultslist]
        R = sorted(R,key = lambda x: x[4], reverse=True)
        # get uniques
        ResultsFreq = []
        for r in R:
            if r not in ResultsFreq:
                ResultsFreq.append(r)
        # NOW PRINT RESULTS
        print (" KNOCKOUT RESULTS " )
        for r in ResultsFreq[0:3]:
            print ("%s,%s,%s,%s,%s" % r)


def makeProgressPlot( sims, teamnames, save=True ):
    # Probability of each team making it to each successive stage of the tournamnet
    ProgressArray = []
    for t in teamnames:
        ProgressArray.append( TraceTeam(sims,t) )
    nRounds = 5
    nteams = len( ProgressArray )
    ProgressArray = sorted( ProgressArray, key = lambda x: np.sum(x[1:]), reverse=True )
    grid = np.zeros((nteams,nRounds),dtype=float)
    gridmax = 0.9
    gridmin = 0
    for i in range(nteams):
        for j in range(nRounds):
            grid[i,j] = np.round( ProgressArray[i][j+1] ,3)
            if grid[i,j] <0.01:
                grid[i,j] = gridmin

    fig,axes = plt.subplots(nrows=1,ncols=2,figsize=(10, 6))   
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=0.45)

    teams = [t[0] for t in ProgressArray]
    for i in range(nteams): 
        if teams[i]=='Korea Republic':
            teams[i] = 'South Korea'

    nteams = nteams/2

    for sp,ax in zip([0,1],axes):
        subgrid = grid[int(sp*nteams):int((sp+1)*nteams),:]
        subteams = teams[int(sp*nteams):int((sp+1)*nteams)]
        Y = np.arange(nteams+0.5, 0, -1)
        X = np.arange(0.5, nRounds+1, 1)
        X, Y = np.meshgrid(X, Y)
        
        cmap = plt.get_cmap('Blues')#cool, Reds, Purples
        levels = MaxNLocator(nbins=gridmax/0.01).tick_values(gridmin,gridmax)# grid.max())
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
        ax.pcolormesh(X, Y, subgrid,cmap=cmap,norm=norm)
        ax.set_xlim(0.5,nRounds+0.5)
        ax.set_ylim(0.5,nteams+0.5)

        ax.set_yticks(np.arange(1,nteams+1,1))
        ax.set_xticks(np.arange(1,nRounds+1,1))
        ax.set_yticklabels(subteams[::-1],color='r',fontsize=11)
        ax.set_xticklabels( ['R16', 'QF', 'SF', 'F', 'W'], color='k', fontsize=12 )
        pthresh=0.01
        for i in range(int(nteams)):
            for j in range(nRounds):
                if subgrid[i,j]>=pthresh:
                    s = "%1.0d" % (round(100*subgrid[i,j],0))
                    ax.text(j+0.9,nteams-i-0.1,s,fontsize=9,color='k')
                else:
                    ax.text(j+0.9,nteams-i-0.1,"<1",fontsize=9,color='k')
        fig.set_facecolor('0.95')
        ax2 = ax.twiny()
        ax2.set_xlim(0.5,nRounds+0.5)
        ax2.set_xticks(np.arange(1,nRounds+1,1))
        ax2.set_xticklabels( ['R16', 'QF', 'SF', 'F', 'W'], color='k' , fontsize=12 )
        ax.tick_params(axis='y',which='both',left='off',right='off')
        ax.tick_params(axis='x',which='both',top='off',bottom='off')
        ax2.tick_params(axis='x',which='both',top='off',bottom='off')
    fig.suptitle('WC2022: Probability of reaching round (%)',y=1.0,fontsize=14)
    if save:
        figname = 'ExpectedProgress.png'
        plt.savefig(figname,dpi=400,bbox_inches='tight',pad_inches=0.1)     
  