from collections import Counter, namedtuple
from itertools import combinations, product
from random import sample, shuffle, random, randint, choice,uniform
import csv

with open('/Users/aaronfoote/Documents/GitHub/Collabria-Fellowship/handProbsRevisedRanked.csv', mode='r') as infile:
     # keys are strings of card tuples, values are floats of win probabilities
    reader = csv.reader(infile)
    with open('new.csv', mode='w') as outfile:
        writer = csv.writer(outfile)
        lookup_table = {rows[0]:float(rows[1]) for rows in list(reader)[1:]}

with open('/Users/aaronfoote/Documents/GitHub/Collabria-Fellowship/handProbsRevisedRanked.csv', mode='r') as infile:
    # keys are strings of card tuples, values are integers of hand rankings
    reader = csv.reader(infile)
    with open('new.csv', mode='w') as outfile:
        writer = csv.writer(outfile)
        rank_lookup = {rows[0]:int(rows[2]) for rows in list(reader)[1:]}

with open('/Users/aaronfoote/Documents/GitHub/Collabria-Fellowship/handProbsRevisedRanked.csv', mode='r') as infile:
    # keys are integer hand rankings, values are the associated string card tuple
    reader = csv.reader(infile)
    with open('new.csv', mode='w') as outfile:
        writer = csv.writer(outfile)
        hand_from_rank = {int(rows[2]) : rows[0] for rows in list(reader)[1:]}

SUITS = ['d', 'h', 's', 'c']
RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
Card = namedtuple('Card', ['suit', 'rank'])

class Hand:
    def __init__(self, hand):
        self.hand = hand
        self.catg = None
        self.high_card_ranks = []
        self.hand.sort(key=(lambda c: c.rank), reverse=True)
        self._classify_hand()

    def __eq__(self, x_hand):
        return self._comp_hand(x_hand) == 'EQ'

    def __lt__(self, x_hand):
        return self._comp_hand(x_hand) == 'LT'

    def __gt__(self, x_hand):
        return self._comp_hand(x_hand) == 'GT'

    def __repr__(self):
        face_cards = {1: 'A', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        repr_str = ''
        for n in range(0, 5):
            repr_str += str(face_cards.get(self.hand[n].rank,
                                           self.hand[n].rank)) \
                        + self.hand[n].suit + ' '
        return repr_str

    def _classify_hand(self):
        rank_freq = list(Counter(card.rank for card in self.hand).values())
        suit_freq = list(Counter(card.suit for card in self.hand).values())
        rank_freq.sort()
        suit_freq.sort()
        if self._is_straight() and suit_freq[0] == 5:
            self.catg = 'SF'
            self.high_card_ranks = [c.rank for c in self.hand]
            self._wheel_check()
        elif rank_freq[1] == 4:
            self.catg = '4K'
            self.high_card_ranks = [self.hand[2].rank,
                                    (self.hand[0].rank
                                     if self.hand[0].rank != self.hand[2].rank
                                     else self.hand[4].rank)]
        elif rank_freq[1] == 3:
            self.catg = 'FH'
            self.high_card_ranks = [self.hand[2].rank,
                                    (self.hand[3].rank
                                     if self.hand[3].rank != self.hand[2].rank
                                     else self.hand[1].rank)]
        elif suit_freq[0] == 5:
            self.catg = 'F'
            self.high_card_ranks = [c.rank for c in self.hand]
        elif self._is_straight():
            self.catg = 'S'
            self.high_card_ranks = [c.rank for c in self.hand]
            self._wheel_check()
        elif rank_freq[2] == 3:
            self.catg = '3K'
            self.high_card_ranks = [self.hand[4].rank, self.hand[0].rank]
            self.high_card_ranks.append(self.hand[3].rank
                                        if self.hand[1].rank in self.high_card_ranks
                                        else self.hand[1].rank)
        elif rank_freq[2] == 2:
            self.catg = '2K2'
            self.high_card_ranks = [self.hand[0].rank,
                                    self.hand[2].rank,
                                    self.hand[4].rank]
        elif rank_freq[3] == 2:
            self.catg = '2K'
            self.high_card_ranks = list(set(c.rank for c in self.hand))
        else:
            self.catg = None
            self.high_card_ranks = [c.rank for c in self.hand]

    def _is_straight(self):
        return ((False not in [(self.hand[n].rank == self.hand[n+1].rank + 1)
                               for n in (0, 1, 2, 3)])
                or ([c.rank for c in self.hand] == [14, 5, 4, 3, 2]))

    def _wheel_check(self):
        # allows for the correct ordering of low ace ("wheel") straight
        if (self.catg in ['SF', 'S']
                    and self.high_card_ranks == [14, 5, 4, 3, 2]):
            self.high_card_ranks.pop(0)
            self.high_card_ranks.append(1)

    def _comp_hand(self, comp_hand):
        ret_val = 'EQ'
        catg_order = [None, '2K', '2K2', '3K', 'S', 'F', 'FH', '4K', 'SF']
        curr_hand_catg = catg_order.index(self.catg)
        comp_hand_catg = catg_order.index(comp_hand.catg)
        if curr_hand_catg > comp_hand_catg:
            ret_val = 'GT'
        elif curr_hand_catg < comp_hand_catg:
            ret_val = 'LT'
        else:
            for curr_high_card, comp_high_card in \
                        zip(self.high_card_ranks, comp_hand.high_card_ranks):
                if curr_high_card > comp_high_card:
                    ret_val = 'GT'
                    break
                elif curr_high_card < comp_high_card:
                    ret_val = 'LT'
                    break
        return ret_val


class Texas_Hold_Em(object):
    def __init__(self, player_count=2):
        self.player_count = player_count
        self.players = []
        self.comm_cards = []
        self.deck = [Card(*c) 
                     for c in product(SUITS, RANKS)]

    def __str__(self):
        face_cards = {1: 'A', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        comm_cards = ""
        for c in self.comm_cards:
            comm_cards += str(face_cards.get(c.rank, c.rank)) + c.suit + " "
        rv =  "-" * 40 + f"\n\nCommunity Cards:\n{comm_cards}\n" + "*" * 20 + "\n"
        for ct, player_hand in enumerate(self.players):
            player_cards = ""
            for c in player_hand:
                player_cards += str(face_cards.get(c.rank, c.rank)) + c.suit + " "
            rv += f"Player {str(ct)}: {player_cards}\n"
        winners = self.who_wins()
        rv += "*" * 20 + "\n"
        for winner in winners:
            rv += f"Player {str(winner[0])} wins: {str(winner[1])}\n"
        rv += "\n" + "-" * 40
        return rv

    def deal_cards(self):
        self.comm_cards.clear()
        self.players.clear()
        shuffle(self.deck)
        dealt_cards = sample(self.deck, (2 * self.player_count) + 5)
        for player in range(self.player_count):
            self.players.append([dealt_cards.pop(n) for n in range(2)])
            self.players[player].sort()
        self.comm_cards.extend(dealt_cards)
        self.comm_cards.sort()

    def who_wins(self):
        highest_hands = []
        for player, hand in enumerate(self.players):
            card_pool = self.comm_cards.copy()
            card_pool.extend(hand)
            card_combinations = [list(cards) for cards in combinations(card_pool, 5)]
            highest_hands.append(max([Hand(h) for h in card_combinations]))
        winning_hand = max(highest_hands)
        winners = []
        for player in range(highest_hands.count(winning_hand)):
            idx = highest_hands.index(winning_hand)
            winners.append((idx, highest_hands.pop(idx)))
        return winners

class Agent:
    AggressionLookup = {
        'AAo bluffer' : 1, 'T8o bluffer' : 1326,'K9o bluffer' : 531, 'K4o bluffer' : 1061,
        'T4s bluffer' : 1591, '75o bluffer' : 2121, '32o bluffer' : 2651
        }
    def __str__(self) -> str:
        return f"Player ID: {self.ID}"

    def __init__(self,ID : str, stack : int, strategy, act = None, previousBet = None, hand = []) -> None:
        self.ID = ID
        self.Stack = stack
        self.Strategy = strategy

        self.Hand = str(tuple(hand))
        self.Act = act
        self.PreviousBet = previousBet
        

        self.Rank = self.DORank()
        self.StrategyUsed,self.RepresentedHand,self.Bluffing = self.DetermineStrategy()
        self.Equity = self.UpdateEquity()
        self.PreviousStack = stack
        self.HandsSurvived = 0
        self.WonAHand = False

    def DetermineAction(self,minStake : int, pot : int):
        if self.Equity < 0.5:
            if self.EV(pot,minStake) > 0:
                return minStake
            else:
                return -1
        else:
            return self.Stack
    def UpdateEquity(self):
        '''
        Assuming the agent has a hand assigned, they will look up the equity in a table when the agent
        is rational/bluffer. Otherwise the equity is a random number from zero to one. If no hand is
        assigned yet, -1 is returned.
        '''
        if self.Hand != str(tuple([])):
            if 'random' not in self.StrategyUsed:
                return lookup_table[self.RepresentedHand]
            else:
                return uniform(0.2923,.8493)#uniform(0,1)#
        else:
            return -1
    def DetermineStrategy(self):
        strategy = max(self.Strategy,key = self.Strategy.get)
        if "bluffer" in strategy:
            rankToRep = self.AggressionLookup[strategy]
            return strategy,hand_from_rank[rankToRep],1
        else:
            return strategy,self.Hand,0
    def ConsiderBluff(self):
        '''
        Flips a weighted coin to determine if bluffing or not. If so, represent the hand as given by
        BluffAggresssion, and return 1 to indicate that the agent is bluffing. If no, just return
        the player's current hand and a zero to indicate no bluffing.
        '''
        if random() < self.BluffProbability: # we're bluffing!
            rankToRep = self.BluffAggression
            return hand_from_rank[rankToRep],1
        else:
            return self.Hand,0
    def DORank(self):
        '''
        If the agent has a hand assigned to them, the rank of that hand is returned. Otherwise -1.
        '''
        if self.Hand != str(tuple([])):
            return rank_lookup[self.Hand]
        else:
            return -1
    def UpdateCI(loser,winner):
        '''
        self -> Losing Agent
        winner -> Wining Agent

        self loses confidence in the strategy they used proportional to the amount of money they lost,
        transferring that confidence to the strategy that the winner used. This is a complete
        information update, as the loser knows the strategy used by the winner.
        '''
        if loser.PreviousStack < loser.Stack:
            print("\n\n\n\n\n Loser won money on the hand \n\n\n\n ")
            print(f'Loser Previous Stack: {loser.PreviousStack} \t Stack After Playing Hand: {loser.Stack}')
            print(f'Winner Previous Stack: {winner.PreviousStack} \t Stack After Playing Hand: {winner.Stack}\n\n')
        #print(loser.Stack)
        change = (loser.PreviousStack - loser.Stack) / loser.PreviousStack * loser.Strategy[loser.StrategyUsed]
        loser.Strategy[loser.StrategyUsed] -= change
        loser.Strategy[winner.StrategyUsed] += change

    def UpdateICI(self):
        '''
        self -> The Agent instance that is going to learn

        self loses confidence in the strategy they used an amount proportional to the amount of their stack that
        they lost. They don't know the strategy used by the winner (incomplete information), so that lost confidence
        is distributed uniformly among the rest of the strategies.
        '''
        if self.PreviousStack < self.Stack:
            print("\n\n\n\n\n Loser won money on the hand \n\n\n\n ")
            print(f'Loser Previous Stack: {self.PreviousStack} \t Stack After Playing Hand: {self.Stack}')
        change = (self.PreviousStack - self.Stack) / self.PreviousStack * self.Strategy[self.StrategyUsed]
        self.Strategy[self.StrategyUsed] -= change
        for s in self.Strategy.keys():
            if s != self.StrategyUsed:
                self.Strategy[s] += change / (len(self.Strategy) - 1)
    def urnLearnComplete(self,winner):
        self.Strategy[self.StrategyUsed] += 1 # Put the marble you used back
        self.Strategy[winner.StrategyUsed] += 1 # Put a marble in for the strategy the winner used
    def urnLearnIncomplete(self,s):
        self.Strategy[self.StrategyUsed] += 1 # Put the marble you used back
        self.Strategy[s] += 1 # Add a marble in for the randomly chosen stragey
    def RothErevLearn(self,magnitude):
        self.Strategy[self.StrategyUsed] += magnitude
    def RothErevWeightedLearn(self):
        self.Strategy[self.StrategyUsed] += self.Stack - self.PreviousStack
    def RothErevLinearWeightedLearn(self,x_min,phi):
        for s in self.Strategy:
            if self.StrategyUsed == s:
                self.Strategy[s] = (1-phi)*self.Strategy[s] + self.Stack - self.PreviousStack - x_min
            else:
                self.Strategy[s] = (1-phi)*self.Strategy[s]
    def NormalizeStrategy(self):
        dict_sum = sum(self.Strategy.values())
        props = {s : self.Strategy[s]/dict_sum for s in self.Strategy}
        self.Strategy = {s : round(self.Stack * props[s]) for s in self.Strategy}
    def determineStrategyRothErev(self):
        p = random()
        dict_sum = sum(self.Strategy.values())
        normed = {s : self.Strategy[s]/dict_sum for s in self.Strategy}
        cumulated = 0
        strategy = ''
        for s in self.Strategy:
            cumulated += normed[s]
            if p <= cumulated:
                strategy = s
                break
        if strategy == '':
            raise f'{self}'
        if "bluffer" in strategy:
            rankToRep = self.AggressionLookup[strategy]
            return strategy, hand_from_rank[rankToRep],1
        else:
            return strategy, self.Hand, 0
    def determineStrategyUrn(self):
        try:
            l = [s for s in self.Strategy for _ in range(self.Strategy[s])]
        except TypeError:
            raise Exception(f"{self.Strategy}")
        strategy = choice(l) # Pick the marble
        if "bluffer" in strategy:
            rankToRep = self.AggressionLookup[strategy]
            return strategy, hand_from_rank[rankToRep],1
        else:
            return strategy, self.Hand, 0
    def WouldPlay(self):
        return max(self.Strategy,key = self.Strategy.get)
    def EV(self,pot,bet):
        '''
        returns expected value of bet.
        Pre-condition: bet >= minimum stake in the hand
        '''
        return self.Equity*(pot + 2*bet) - bet
        
def playHand(p1 : Agent, p2 : Agent,smallBlind : int,game : Texas_Hold_Em,big : int):
    d = {}

    p1.Stack = p1.Stack - 2*smallBlind if big == 0 else p1.Stack - smallBlind
    p2.Stack = p2.Stack - smallBlind if big == 0 else p2.Stack - 2*smallBlind
    p1.PreviousBet = 2*smallBlind if big == 0 else smallBlind
    p2.PreviousBet = smallBlind if big == 0 else 2*smallBlind


    winner = game.who_wins()[0][0]

    p1.Hand = str(tuple(game.players[0]))
    p2.Hand = str(tuple(game.players[1]))

    d['p1Equity'] = lookup_table[p1.Hand]
    d['p2Equity'] = lookup_table[p2.Hand]

    p1.StrategyUsed,p1.RepresentedHand,p1.Bluffing = p1.determineStrategyRothErev()
    p2.StrategyUsed,p2.RepresentedHand,p2.Bluffing = p2.determineStrategyRothErev()

    p1.Equity = p1.UpdateEquity()
    p2.Equity = p2.UpdateEquity()

    pot = 3*smallBlind
    betsPlaced = 0
    
    if big == 0: # In this case, player 2 goes first
        p2.Act = p2.DetermineAction(p1.PreviousBet - p2.PreviousBet, pot)
        if p2.Act == -1: #p2 Folded
            return p1.Stack + pot,p2.Stack,0,1,0,d,betsPlaced
        pot += p2.Act
        p2.Stack -= p2.Act
        p2.PreviousBet += p2.Act
        betsPlaced += 1
        """
        We don't end the hand if p2 calls, since p1 still gets to act. Only 
        ends when p2 raises and then p1 acts.
        """
        if p2.Stack == 0:
            #p2 is all-in, so we give p1 a chance to act and then split up the money accordingly
            p1.Act = p1.DetermineAction(p2.PreviousBet - p1.PreviousBet, pot)
            if p1.Act == -1:
                return p1.Stack,p2.Stack + pot,1,0,1,d,betsPlaced
            else:
                pot += p1.Act
                p1.Stack -= p1.Act
                p1.PreviousBet += p1.Act
                betsPlaced += 1
                if winner == 0:
                    return p1.Stack + pot, p2.Stack, 0,0,0,d,betsPlaced
                else:
                    return p1.Stack, p2.Stack + pot, 0,0,1,d,betsPlaced
    while True:
        p1.Act = p1.DetermineAction(p2.PreviousBet - p1.PreviousBet, pot)
        if p1.Act == -1: #p1 Folded
            return p1.Stack,p2.Stack+ pot,1,0,1,d,betsPlaced
        pot += p1.Act
        p1.Stack -= p1.Act
        p1.PreviousBet += p1.Act
        betsPlaced += 1
        if p1.PreviousBet == p2.PreviousBet and betsPlaced != 1: 
            """
            player 1 calls and both players have gotten to act,
            so we determine the winner and divide winnings
            """
            if winner == 0:
                return p1.Stack + pot, p2.Stack, 0,0,0,d,betsPlaced
            else:
                return p1.Stack, p2.Stack + pot, 0,0,1,d,betsPlaced
        if p1.Stack == 0:
            #p1 is all-in, so we give p2 a chance to act and then split up the money accordingly
            p2.Act = p2.DetermineAction(p1.PreviousBet - p2.PreviousBet, pot)
            if p2.Act == -1:
                return p1.Stack + pot,p2.Stack,0,1,0,d,betsPlaced
            else:
                pot += p2.Act
                p2.Stack -= p2.Act
                p2.PreviousBet += p2.Act
                betsPlaced += 1
                if winner == 0:
                    return p1.Stack + pot, p2.Stack, 0,0,0,d,betsPlaced
                else:
                    return p1.Stack, p2.Stack + pot, 0,0,1,d,betsPlaced
        p2.Act = p2.DetermineAction(p1.PreviousBet - p2.PreviousBet, pot)
        if p2.Act == -1: #p2 Folded
            return p1.Stack + pot,p2.Stack,0,1,0,d,betsPlaced
        pot += p2.Act
        p2.Stack -= p2.Act
        p2.PreviousBet += p2.Act
        betsPlaced += 1
        if p2.PreviousBet == p1.PreviousBet: 
            #p2 calls, so we find the winner and give them the money
            if winner == 0:
                return p1.Stack + pot, p2.Stack, 0,0,0,d,betsPlaced
            else:
                return p1.Stack, p2.Stack + pot, 0,0,1,d,betsPlaced
        if p2.Stack == 0:
            #p2 is all-in, so we give p1 a chance to act and then split up the money accordingly
            p1.Act = p1.DetermineAction(p2.PreviousBet - p1.PreviousBet, pot)
            if p1.Act == -1:
                return p1.Stack,p2.Stack + pot,1,0,1,d,betsPlaced
            else:
                pot += p1.Act
                p1.Stack -= p1.Act
                p1.PreviousBet += p1.Act
                betsPlaced += 1
                if winner == 0:
                    return p1.Stack + pot, p2.Stack, 0,0,0,d,betsPlaced
                else:
                    return p1.Stack, p2.Stack + pot, 0,0,1,d,betsPlaced
        

        

def initializeStrategy(strategies : list[str], strategy : str):
    '''
    strategies -> The list of possible strategies in the population
    strategy -> The strategy that will be used

    initializeStrategy([x_0,...,x_n],x_i) = d, a dictionary such that
    d[x_j] = 1 if j = i, 0 otherwise
    '''
    return {s : (int(1) if s == strategy else int(0)) for s in strategies}
def initializeRothErev(strategies : list[str]):
    '''
    strategies -> The list of possible strategies in the population

    initializeRothErev([x_0,...,x_n]) = {x_0 : 1, x_1 : 1, ... , x_n : 1}
    '''
    return {s : 1 for s in strategies}

def initializeRothErevWeighted(strategies : list[str],startingStack : int):
    '''
    strategies -> The list of possible strategies in the population

    initializeRothErev(l = [x_0,...,x_n],s) = {x_0 : s/len(l), x_1 : s/len(l), ... , x_n : s/len(l)}
    '''
    return {s : int(startingStack/len(strategies)) for s in strategies}

def initializeRothErevLinearWeighted(strategies : list[str],startingStack : int):
    '''
    strategies -> The list of possible strategies in the population

    initializeRothErev([x_0,...,x_n],s) = {x_0 : s, x_1 : s, ... , x_n : s}
    '''
    return {s : startingStack for s in strategies}

