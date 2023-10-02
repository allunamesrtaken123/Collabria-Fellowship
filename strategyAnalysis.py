from importAgentsEV import Agent, Texas_Hold_Em, playHand
from tqdm import tqdm

startStack = 10000 #10 thousand
smallBlind = 100 # 50BB stacks
hands = 100000000

rat = Agent(ID = 'rational', stack = startStack, strategy = {'rational' : 1, 'one choice random' : 0})
AAo = Agent(ID = 'bluffer', stack = startStack, strategy = {'rational' : 0, 'AAo bluffer' : 1})

ratEquity = [] #ratEquity and ratEquityRep are the same
AAoEquity = []
winner = []
ratFold = []
AAoFold = []
ratBet = []
AAoBet = []
betsL = []

th = Texas_Hold_Em(player_count = 2)
for h in tqdm(range(hands)):
    rat.Stack = startStack
    AAo.Stack = startStack

    th.deal_cards()
    rat.PreviousStack = rat.Stack
    AAo.PreviousStack = AAo.Stack

    rat.Stack,AAo.Stack,ratFolded,AAoFolded,whoWon,equities,bets  = playHand(rat,AAo,smallBlind,th,h % 2)

    ratEquity.append(equities['p1Equity'])
    AAoEquity.append(equities['p2Equity'])

    winner.append(whoWon)

    ratBet.append(rat.Stack - rat.PreviousStack)
    AAoBet.append(AAo.Stack - AAo.PreviousStack)

    ratFold.append(ratFolded)
    AAoFold.append(AAoFolded)
    
    betsL.append(bets)
with open(f'August/Investigating Rational/Results/With AAo/ratAndAAo.csv','w') as f:
    f.write("ratEquity,ratFold,ratWinnings,AAoEquity,AAoFold,AAoWinnings,winner,bets,bigBlind\n")
    for i in range(hands):
        f.write(f"{ratEquity[i]},{ratFold[i]},{ratBet[i]},{AAoEquity[i]},{AAoFold[i]},{AAoBet[i]},{winner[i]},{betsL[i]},{i % 2}\n")
f.close()