import json
import requests

class hand:
    def __init__(self, owner, contents):
        self.owner = owner
        self.contents = contents

    def calculate_score(self):
        score = 0
        for val in self.contents:
            score += val[0]
        return score

    def draw_cards(self, deck_id, count):
        drawn = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={count}").json()
        for i in drawn['cards']:
            self.contents[card_conversion(i['code'], True)] = (i['value'], i['image'])

def card_conversion(card, isCode):
    """
    :param card: The card code OR the card name
    :param isCode: True if converting from code->name, False if converting name->code
    :return: if isCode is true, it returns the card name. If false, it returns the card code
    """
    suits = {'S': 'SPADES', 'D': 'DIAMONDS', 'H': 'HEARTS', 'C': 'CLUBS'}
    values = {'A': 'ACE', 'J': 'JACK', 'Q': 'QUEEN', 'K': 'KING', '0': '10'}
    if isCode:
        card_value = card[0] if card[0] not in values.keys() else values[card[0]]
        card_suit = suits[card[1]]
        return f"{card_value} of {card_suit}"
    else:
        card_value = card.split(' of ')[0]
        card_value = card_value if card_value not in values.values() else list(values.keys())[list(values.values()).index(card_value)]
        card_suit = card.split(' of ')[1][:1]
        return f"{card_value}{card_suit}"

def start_game():
    dealers_hand = hand(owner="Dealer", contents={})
    players_hand = hand(owner="Player", contents={})
    # fetch a standard six-deck
    cards = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=6",
                         params={'jokers_enabled':'false'}).json()
    deck_id = cards['deck_id']
    # Starting deal:
if __name__ == '__main__':
    start_game()