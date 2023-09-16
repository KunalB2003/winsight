SUITES = ["Sp","Ht","Dd", "Cb"]
RANKS = ["2", "3", "4", "5", "6", "7", "8" , "9", "10", "J", "Q", "K", "A"]
PLAYER_HAND = []
TABLE_CARDS = []
HAND_STRENGTH = 0
SUITED_CONNECTOR = False
PAIR = False
AVERAGE_HAND = 1.7
FAVOR = 0

class testCard (object):
    
    def __init__(self, s, r):
        self.rank = r
        self.suite = s
        
    def getRank(self):
        return self.rank

    def getSuite(self):
        return self.suite


def hand (card1, card2):
    card1rank = -1
    card2rank = -1
    card1suite = ""
    card2suite = ""
    suited = False
    global HAND_STRENGTH
    for rank in range(len(RANKS)):
        if card1.getRank() == RANKS[rank]:
            card1rank = rank
        if card2.getRank() == RANKS[rank]:
            card2rank = rank 
        
    for suite in range(len(SUITES)):
        if card1.getSuite() == SUITES[suite]:
            card1suite = suite
        if card2.getSuite() == SUITES[suite]:
            card2suite = suite 
            
    if card1suite == card2suite:
        HAND_STRENGTH += .5
        suited = True

    if card1rank == card2rank:
        PAIR = True
        if card1rank >= 9:
            ##premium hand 
            HAND_STRENGTH += card1rank * .1 + .3
        else:
            #pair
            HAND_STRENGTH += card1rank * .1 + .1

    if card1rank + 1 == card2rank or card2rank + 1 == card1rank or (card1rank == 0 or card2rank == 0 and card2rank == 12 or card1rank == 12):
        SUITED_CONNECTOR = True
        HAND_STRENGTH += .3

    HAND_STRENGTH += card1rank * .1
    HAND_STRENGTH += card2rank * .1


def favor():
    

def table (tablelist):
    global FAVOR
    for card in tablelist:
        if card.getRank() == PLAYER_HAND[0].getRank() and PAIR == True:
            ##trips
            FAVOR += 4
        elif card.getRank() == PLAYER_HAND[0].getRank():
            FAVOR += 1
        elif card.getRank() == PLAYER_HAND[1].getRank():
            FAVOR += 1

    
        




    
        

def main():
    testHand()
    pass


def testHand():
    global HAND_STRENGTH
    card1 = testCard("Ht", "9")
    card2 = testCard("Sp", "10")
    hand(card1, card2)
    print(HAND_STRENGTH)
    
if __name__ == "__main__":
    main()    
            