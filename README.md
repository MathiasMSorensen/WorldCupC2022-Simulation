# WC2022-Simulation

Go to tournament_simulation.ipynb to simulate. 

Method:
 - Odds has been extracted across various betting sites using oddsapi (need an API keyu here)
 - for each game in group stage, a value has been assigned through the odds, to run simulation in group stage
 - for each playoff game, initial change of winning the tournament has been used, together with an esimtated approximation for the probabiliy of draw (depending on the level of winner certainty). If game ended draw, penalty shootout is assumed to be 50/50.

 Have fun simulating the world cup! 
