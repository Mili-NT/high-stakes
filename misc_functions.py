from tkinter import *
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

def load_image(card, isHidden):
    """
    :param card: The card code, which is also the image name
    :param isHidden: Is this card hidden (any of the dealers cards that arent the first?) if so, display the back side
    :return: Returns a PhotoImage object of the .png file
    """
    return PhotoImage(file=f"resources/{card}.png") if isHidden is False else PhotoImage(file=f"resources/hidden.png")

