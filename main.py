# Library Imports
import requests
from datetime import datetime
from tkinter import *
from tkinter import ttk
# Local Imports:
import misc_functions
import popup_windows

# TODO: 1. Fix windows, they need scale, but not change size
# TODO: 2. Card Drawing

#
# Classes:
#
class hand:
    """
    The hand class tracks the contents and score of a hand.
    """
    def __init__(self, contents):
        """
        :param contents: A dict that tracks the cards in the hand as a (card name:card value) pair
        """
        self.contents = contents

    def calculate_score(self):
        """
        :return: the integer value of the hand's score
        """
        # Non-standard cards are face cards (Jack, Queen, King) and tens (0)
        # For standard cards, we can get their value by taking the first digit of the card code
        nonstandard = ['J', 'Q', 'K', '0']
        converted = [misc_functions.card_conversion(val, False) for val in self.contents]
        values = [val[0] if val[0] not in nonstandard else '10' for val in converted]
        # Calculate Aces:
        if 'A' in values:
            # Calculate the score with the ace counted as 1
            low = sum([int(value) if value != 'A' else 1 for value in values])
            # Calculate the score with the ace counted as 11
            high = sum([int(value) if value != 'A' else 11 for value in values])
            # If the higher score is over 21, take the low score. If it isn't, take the higher score.
            score = low if high > 21 else high
        else:
            score = sum([int(v) for v in values])
        return score

    def draw_cards(self, deck_id, count):
        """
        :param deck_id: The ID of the deck, which is stored in the blackjack_gui class
        :param count: How many cards to draw
        :return: Returns nothing, but adds a new card to the hand.

        The reason this exists as well as the blackjack_gui.hit() function is so the dealer can draw cards independently
        of the blackjack_gui.hit_button()
        """
        drawn = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={count}").json()
        for i in drawn['cards']:
            self.contents[misc_functions.card_conversion(i['code'], True)] = i['value']
class blackjack_gui:
    """
    The blackjack_gui is the main class of the program.
    It creates and manages both the top-level window, and the game functions such as hitting, standing, and dealing

    GUI Functions: __init__, announce()
    Game Functions: decide_outcome(), check_bust(), deal(), hit(), stand()
    """
    def __init__(self, root):
        # Basic setup, such as window title and geometry, hand initialization, deck_id fetching
        self.root = root
        self.root.title("High-Stakes")
        self.root.geometry("600x400")
        self.dealer_hand = hand({})
        self.player_hand = hand({})
        self.deck_id = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=6",
                         params={'jokers_enabled':'false'}).json()['deck_id']
        # Frames And Canvases:
        self.left = ttk.Frame(self.root, borderwidth=2, relief="solid")
        self.right = ttk.Frame(self.root, borderwidth=2, relief="solid")
        self.opponent_cards = Canvas(self.left, borderwidth=2, relief="solid")
        self.player_cards = Canvas(self.right, borderwidth=2, relief="solid")
        self.announcements = Canvas(self.left, borderwidth=2, relief="solid")
        # Buttons And Widgets:
        self.hit_button = Button(self.right, text="Hit", command=lambda: self.hit())
        self.stand_button = Button(self.right, text="Stand", command=lambda: self.stand(True))
        self.scrollbar = ttk.Scrollbar(self.announcements)
        # Labels:
        self.opponent_label = ttk.Label(self.opponent_cards, text="Opponent's Cards")
        self.player_label = ttk.Label(self.player_cards, text="Your Cards")
        self.announcements_label = ttk.Label(self.announcements, text="Announcements")
        # Packing:
        self.left.pack(side="left", expand=True, fill="both")
        self.right.pack(side="right", expand=True, fill="both")
        self.announcements.pack(side="bottom", expand=True, fill="both", padx=5, pady=5)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.announcements_label.pack()
        self.stand_button.pack(side="bottom")
        self.hit_button.pack(side="bottom")
        self.opponent_cards.pack(expand=True, fill="both", padx=5, pady=5)
        self.player_cards.pack(expand=True, fill="both", padx=5, pady=5)
        self.opponent_label.pack()
        self.player_label.pack()
        self.file_number = IntVar()
        if misc_functions.isAdmin() is False:
            popup_windows.access_denied_window(root, self)
        else:
            popup_windows.file_entry_window(root, self)


    #
    # GUI Functions:
    #
    def announce(self, message):
        """
        :param message: The text to be printed into the annoucements canvas in the GUI
        :return: Returns nothing, packs the label to display it
        """
        label = ttk.Label(self.announcements, text=f"{datetime.now().strftime('%X')}: {message}\n")
        label.pack()


    #
    # Game Functions
    #
    def decide_outcome(self):
        player_score = self.player_hand.calculate_score()
        dealer_score = self.dealer_hand.calculate_score()
        outcome_announcement = f"{player_score} to the dealer's {dealer_score}"
        # Blackjack cases
        if player_score == 21:
            self.announce(f"BLACKJACK! You won {outcome_announcement}!")
            outcome = 'win'
        elif dealer_score == 21:
            self.announce(f"The dealer got blackjack! You lost {outcome_announcement}!")
            outcome = 'loss'
        # Tie case
        elif player_score == dealer_score:
            self.announce(f"You and the dealer tied with {dealer_score} points!")
            outcome = 'tie'
        # Score comparison
        else:
            outcome = 'loss' if dealer_score > player_score else 'win'
            message = f"You won with {outcome_announcement}! Good job!" if outcome == 'win' else f"You lost with {outcome_announcement}! Too bad!"
            self.announce(message)
        # Calls the outcomeWindow and passes the outcome to it
        popup_windows.outcome_window(root, self, outcome, self.file_number)
    def check_bust(self):
        """
        :return: Returns True if bust and False if not
        If the player does bust, it goes ahead and calls the outcomeWindow. The reason it also returns True instead of
        just calling the outcomeWindow is to prevent the dealer from performing further action.
        """
        player_score = self.player_hand.calculate_score()
        dealer_score = self.dealer_hand.calculate_score()
        if player_score > 21:
            self.announce(f"You busted with a {player_score}! Too bad!")
            popup_windows.outcome_window(root, self, 'loss', self.file_number)
            return True
        if dealer_score > 21:
            self.announce(f"The dealer busted with a {dealer_score}! You win!")
            popup_windows.outcome_window(root, self, 'win', self.file_number)
            return True
        return False
    def deal(self):
        """
        Fetches a standard six-deck and deals 2 cards to the player, and two to the dealer. This function starts the
        game and is called from outside the blackjack_gui class in the main program
        """
        self.announce("The Game Has Started!")
        draw = requests.get(f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count=2").json()
        # The player draws:
        player_dealt_cards = [] # This variable is to store the drawn card names for making the announcement
        for i in draw['cards']:
            card_name = misc_functions.card_conversion(i['code'], True)
            self.player_hand.contents[card_name] = i['value']
            # Appends the card name along with the correct article
            player_dealt_cards.append(f"{'an' if card_name[0] in ['A', 'E', 'I', 'O', 'U'] else 'a'} {card_name}")
        # Because there are only ever 2 cards dealt initally, we can just access by index
        self.announce(f"You drew {player_dealt_cards[0]} and {player_dealt_cards[1]}")
        self.announce(f"Your score is {self.player_hand.calculate_score()}")
        # The dealer draws:
        self.dealer_hand.draw_cards(self.deck_id, 2)
        self.announce(f"The dealer drew 2 cards!")
    def hit(self):
        """
        This function is bound to the blackjack_gui.hit_button().
        It allows the player to add one card to their deck, and also allows the dealer to either stand or hit
        """
        # Player hitting:
        hit = requests.get(f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count=1").json()
        for i in hit['cards']:
            card_name = misc_functions.card_conversion(i['code'], True)
            self.player_hand.contents[card_name] = i['value']
            self.announce(f"You drew {'an' if card_name[0] in ['A', 'E', 'I', 'O', 'U'] else 'a'} {card_name}")
            self.announce(f"Your score is {self.player_hand.calculate_score()}")
            # If the player gets blackjack
            if self.player_hand.calculate_score() == 21:
                self.decide_outcome()
        # This is why blackjack_gui.check_bust() returns True if it busts
        if self.check_bust() is False:
            # Dealer stands on 17 or higher
            if self.dealer_hand.calculate_score() >= 17:
                self.stand(False)
            else:
                # Dealer draws, and then it checks for a bust
                self.announce("The dealer draws a card!")
                self.dealer_hand.draw_cards(self.deck_id, 1)
                # If the dealer gets blackjack:
                if self.dealer_hand.calculate_score() == 21:
                    self.decide_outcome()
                else:
                    self.check_bust()
    def stand(self, userStand):
        """
        :param userStand: True if its the player standing (aka the blackjack_gui.stand_button() was pressed) and False
        if the dealer is standing (aka this function was called manually)
        :return: Returns nothing, but calls blackjack_gui.decide_outcome() to determine the winner
        """
        if userStand:
            self.announce("You stand!")
        else:
            self.announce("The dealer stands!")
        self.decide_outcome()
#
# Main:
#
if __name__ == '__main__':
    root = Tk()
    interface = blackjack_gui(root)
    root.mainloop()