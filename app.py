from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from roboflow import Roboflow

BURNED_CARDS = []
PLAYER_HAND = []
DEALER_HAND = []
GAME_OVER = False
PLAYER_TURN = True
MAIN_COUNT = 0
ACE_COUNT = 4
PLAYER_TOTAL = 0
DEALER_TOTAL = 0
SOFT = False

BUST_PERCENTAGE = 0


app = Flask(__name__)
camera = cv2.VideoCapture(2)

rf = Roboflow(api_key="3nUG3gBfitus0Ympj3Y2")
project = rf.workspace().project("playing-cards-ow27d")
model = project.version(4).model

def gen_color_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            color_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + color_bytes + b'\r\n')


def gen_altered_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            color_bytes = buffer.tobytes()

            predictions = model.predict(frame, confidence=60, overlap=50).json()[
                "predictions"]

            for prediction in predictions:
                if prediction["confidence"] > 0.75 and transcribeSymbol(prediction["class"]) not in BURNED_CARDS:
                    BURNED_CARDS.append(transcribeSymbol(prediction["class"]))
                    start_game(transcribeSymbol(prediction["class"]))
                    print("Burn:", BURNED_CARDS)
                    print("Player:", PLAYER_HAND)
                    print("Dealer:", DEALER_HAND)
                    print("ACE COUNT", ACE_COUNT)
                    print("MAIN COUNT", MAIN_COUNT)
                    print("PLAYER COUNT", PLAYER_TOTAL)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + color_bytes + b'\r\n')

@app.route("/")
def home():
    global PLAYER_HAND
    return render_template('index.html', cards = PLAYER_HAND)

@app.route('/video_feed_altered')
def video_feed_altered():
    return Response(gen_altered_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/player_cards')
def player_cards():
    return jsonify(PLAYER_HAND)

@app.route('/dealer_cards')
def dealer_cards():
    return jsonify(DEALER_HAND)

@app.route('/bust_percentage')
def bust_percentage():
    calculate_bust_percentage()
    return jsonify(BUST_PERCENTAGE)
                   
@app.route('/multiplier')
def multiplier():
    return jsonify("?")
                   
@app.route('/move_option')
def move_option():
    return jsonify("?")

def calculate_bust_percentage():
    global BUST_PERCENTAGE
    global BURNED_CARDS
    global PLAYER_HAND
    global DEALER_HAND

    hand_val = 0
    for card in PLAYER_HAND: 
        try:
            hand_val += int(card[:-1])
        except:
            hand_val += 10

    if hand_val > 21:
        BUST_PERCENTAGE = 100
        return BUST_PERCENTAGE
    
    if hand_val <= 11:
        BUST_PERCENTAGE = 0
        return BUST_PERCENTAGE
    
    accepted_cards = (21 - hand_val) * 4
    for card in BURNED_CARDS:
        try: 
            if int(card[:-1]) < (21 - hand_val):
                accepted_cards -= 1
        except:
            if (10 < (21 - hand_val)):
                accepted_cards -= 1
    
    BUST_PERCENTAGE = 100 - (100 * (accepted_cards / (1.0  * (52 - len(BURNED_CARDS)))))
        
    return BUST_PERCENTAGE

def transcribeSymbol(input): 
    if input[-1] == "H":
        return input[:-1] + "♥"
    if input[-1] == "C":
        return input[:-1] + "♣"
    if input[-1] == "D":
        return input[:-1] + "♦"
    if input[-1] == "S":
        return input[:-1] + "♠"
    return input

# Definitions
halves_values = {
    '2': 0.5, '3': 1, '4': 1, '5': 1.5, '6': 1, '7': 0.5, '8': 0,
    '9': -0.5, '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

def start_game(card):
    global GAME_OVER
    global PLAYER_HAND
    global DEALER_HAND
    global MAIN_COUNT
    global ACE_COUNT
    global PLAYER_TOTAL
    global DEALER_TOTAL
    global PLAYER_TURN

    if (card[0] not in halves_values):
        MAIN_COUNT += -1
    else:
        MAIN_COUNT += halves_values[card[0]]
        if card[0] == 'A':
            ACE_COUNT -= 1

    if GAME_OVER:
        PLAYER_HAND = []
        DEALER_HAND = []
        GAME_OVER = False
        PLAYER_TOTAL = 0
        DEALER_TOTAL = 0
        PLAYER_TURN = True

    if len(PLAYER_HAND) < 2:
        evaluate_hand(card)
        PLAYER_HAND.append(card)
    elif len(DEALER_HAND) < 1:
        DEALER_HAND.append(card)
        print("------------")
        print(decide_action())
        print("------------")
    elif PLAYER_TURN:
        print("------------")
        print(decide_action())
        print("------------")
        evaluate_hand(card)
        PLAYER_HAND.append(card)
    else:
        DEALER_HAND.append(card)



def evaluate_hand(card):
    # Checking for soft totals (hands with an Ace counted as 11)
    global SOFT
    global PLAYER_TOTAL
    global PLAYER_HAND

    card = card[0]
    if (card not in halves_values):
        PLAYER_TOTAL += 10
    elif card.isnumeric():
        PLAYER_TOTAL += int(card)
    elif card != "A":
        PLAYER_TOTAL += 10
    else:
        PLAYER_TOTAL += 11
        SOFT = True

    aceinhand = False
    for card in PLAYER_HAND:
        if card == 'A':
            aceinhand = True

        # Convert Ace from 11 to 1 if total goes over 21
    if PLAYER_TOTAL > 21 and aceinhand:
        SOFT = False
        PLAYER_TOTAL -= 10

# Determines Hit or Stand


def decide_action():
    global SOFT
    global PLAYER_TOTAL
    global DEALER_HAND

    dealer_up_card = DEALER_HAND[0]
    dealer_up_card = dealer_up_card[0]
    # Hard Totals (Not Involving Ace)
    if not SOFT:
        if PLAYER_TOTAL < 9:
            return "Hit"
        elif PLAYER_TOTAL == 9:
            return "Double" if dealer_up_card in ['3', '4', '5', '6'] else "Hit"
        elif PLAYER_TOTAL == 10:
            return "Double" if dealer_up_card in ['2', '3', '4', '5', '6', '7', '8', '9'] else "Hit"
        elif PLAYER_TOTAL == 11:
            return "Double" if dealer_up_card != 'A' else "Hit"
        elif PLAYER_TOTAL == 12:
            return "Hit" if dealer_up_card in ['2', '3', '7', '8', '9', '10'] else "Stand"
        elif 13 <= PLAYER_TOTAL <= 16:
            return "Stand" if dealer_up_card in ['2', '3', '4', '5', '6'] else "Hit"
        else:
            return "Stand"

    # Soft Totals (Involving Ace)
    if PLAYER_TOTAL == 13 or PLAYER_TOTAL == 14:
        return "Double" if dealer_up_card in ['5', '6'] else "Hit"
    elif PLAYER_TOTAL == 15 or PLAYER_TOTAL == 16:
        return "Double" if dealer_up_card in ['4', '5', '6'] else "Hit"
    elif PLAYER_TOTAL == 17:
        return "Double" if dealer_up_card in ['3', '4', '5', '6'] else "Hit"
    elif PLAYER_TOTAL == 18:
        if dealer_up_card in ['2', '7', '8']:
            return "Stand"
        elif dealer_up_card in ['3', '4', '5', '6']:
            return "Double"
        else:
            return "Hit"
    else:
        return "Stand"


if __name__ == '__main__':
    app.run(debug=True)
