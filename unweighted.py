from importAgentsEV import Agent, Texas_Hold_Em, playHand, initializeRothErev
from time import strftime
from random import choice
from itertools import zip_longest
import csv
from tqdm import tqdm


total_agents = 300
strategies = ['one choice random', 'rational','AAo bluffer']
magnitude = 1
epochs = 10000


directory = f'August/Investigating Rational/Results/With AAo/Unweighted'

iterations = 100
startStack = 10000 #10 thousand
smallBlind = 100 # 50BB stacks

with open(f'{directory}/Parameters for Most Recent Simulation.txt','w') as f:
    f.write(f"When ran: {strftime('%m-%d-%Y %H:%M:%S')}\n")
    f.write(f"Iterations: {iterations}\n")
    f.write(f"Total Agents: {total_agents} (split evenly amongst strategies)\n")
    f.write(f"Strategies Used: {strategies}\n")
    f.write(f"Stack Size (in BBs): {int(startStack/(2*smallBlind))}\n")
    f.write(f"Marbles Added per Win: {magnitude}\n")
    f.write(f"Epochs: {epochs}\n")
f.close()

th = Texas_Hold_Em(player_count = 2)

aggMarblesIn = {s : [] for s in strategies}

epochL = []
winningStrategy = []
p1Strategy = []
p2Strategy = []
chipsWon = []

for it in tqdm(range(iterations)):
    marblesIn = {s : [] for s in strategies}

    agent_pool = []
    for i in range(total_agents):
        agent_pool.append(Agent(ID = f'{i}', stack = startStack, strategy = initializeRothErev(strategies)))
    
    for e in range(epochs):
        for g in range(int(len(agent_pool)/2)):
            p1 = choice(agent_pool)
            agent_pool.remove(p1)
            if min(p1.Strategy.values()) < 0:
                print(p1.Strategy)
            p2 = choice(agent_pool)
            p1.Stack = startStack
            p2.Stack = startStack

            th.deal_cards()
            p1.PreviousStack = p1.Stack
            p2.PreviousStack = p2.Stack

            p1.Stack,p2.Stack,p1Folded,p2Folded,whoWon,_,_ = playHand(p1,p2,smallBlind,th,g % 2)

            epochL.append(e)
            p1Strategy.append(p1.StrategyUsed)
            p2Strategy.append(p2.StrategyUsed)
            winningStrategy.append(p1.StrategyUsed if whoWon == 0 else p2.StrategyUsed)
            chipsWon.append(p1.Stack - p1.PreviousStack if whoWon == 0 else p2.Stack - p2.PreviousStack)

            agent_pool.append(p1)
            if whoWon == 0:
                p1.RothErevLearn(magnitude)
            else:
                p2.RothErevLearn(magnitude)
                
        for s in strategies:
            marblesIn[s].append(sum([a.Strategy[s] for a in agent_pool]))
            
    for s in strategies:
        aggMarblesIn[s].append(marblesIn[s])

for s in strategies:
    dataToExport = zip_longest(*aggMarblesIn[s],fillvalue='NaN')
    with open(f'{directory}/Marbles In {s}.csv','w') as f:
        toWrite = csv.writer(f)
        header = ["Iteration" + str(i) for i in range(iterations)]
        toWrite.writerow(header)
        toWrite.writerows(dataToExport)
    f.close()

with open(f'{directory}/Hand Data.csv', 'w') as f:
    f.write('P1Strategy,P2Strategy,WinnerStrategy,ChipsWon,Epoch\n')
    for i in range(len(epochL)):
        f.write(f"{p1Strategy[i]},{p2Strategy[i]},{winningStrategy[i]},{chipsWon[i]},{epochL[i]}\n")