POINT_COUNT = 0

## .getValue should be the method that gives back the card 
def cardfound(card):
    if card.getValue() >= 2 and  card.getValue() <= 6:
        POINT_COUNT += 1
    elif card.getValue() >= 10:
        POINT_COUNT -= 1
    
        
