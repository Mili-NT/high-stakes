import requests
import game_functions
from datetime import datetime
from tkinter import *
from tkinter import ttk


# TODO: Card drawing (oh boy)
# TODO: File entry and defeat function
# TODO: Announcement window scrolling and frame locking

class hand:
    def __init__(self, contents):
        self.contents = contents

    def calculate_score(self):
        nonstandard = ['J', 'Q', 'K', '0']
        converted = [game_functions.card_conversion(val, False) for val in self.contents]
        values = [val[0] if val[0] not in nonstandard else '10' for val in converted]
        if 'A' in values:
            low = sum([int(value) if value != 'A' else 1 for value in values])
            high = sum([int(value) if value != 'A' else 11 for value in values])
            score = low if high > 21 else high
        else:
            score = sum([int(v) for v in values])
        return score

    def draw_cards(self, deck_id, count):
        drawn = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={count}").json()
        for i in drawn['cards']:
            self.contents[game_functions.card_conversion(i['code'], True)] = i['value']

class outcomeWindow(object):
    def __init__(self,master, outcome):
        self.master = master
        top=self.top=Toplevel(master)
        if outcome == 'win':
            self.l=Label(top,text="You won! Your files live another day")
        elif outcome == 'tie':
            self.l = Label(top, text="You tied! Your files live another day")
        else:
            self.l = Label(top, text="Uh oh, you lost! You know what that means.")
        self.l.pack()
        self.b=Button(top,text='Close',command=self.cleanup)
        self.b.pack()
        self.top.lift()
    def cleanup(self):
        self.master.destroy()
class blackjack_gui:
    def __init__(self, root):
        self.root = root
        self.file_number = 0
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
        # Announcements:
        self.announcements = Canvas(self.left, borderwidth=2, relief="solid")
        self.scrollbar = ttk.Scrollbar(self.announcements)
        self.announcements_label = ttk.Label(self.announcements, text="Announcements")
        # Announcements packing:
        self.announcements.pack(side="bottom", expand=True, fill="both", padx=5, pady=5)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.announcements_label.pack()
        # Buttons:
        self.hit_button = Button(self.right, text="Hit", command=lambda: self.hit())
        self.stand_button = Button(self.right, text="Stand", command=lambda: self.stand(True))
        # Labels:
        self.opponent_label = ttk.Label(self.opponent_cards, text="Opponent's Cards")
        self.player_label = ttk.Label(self.player_cards, text="Your Cards")
        #self.hit_label = Label(self.hit_button, text="Hit", fg="black")
        #self.stand_label = Label(self.stand_button, text="Stand", fg="black")
        # Packing:
        self.left.pack(side="left", expand=True, fill="both")
        self.right.pack(side="right", expand=True, fill="both")
        self.stand_button.pack(side="bottom")
        self.hit_button.pack(side="bottom")
        self.opponent_cards.pack(expand=True, fill="both", padx=5, pady=5)
        self.player_cards.pack(expand=True, fill="both", padx=5, pady=5)
        self.opponent_label.pack()
        self.player_label.pack()

    def announce(self, message):
        label = ttk.Label(self.announcements, text=f"{datetime.now().strftime('%X')}: {message}\n")
        label.pack()
    def decide_outcome(self):
        player_score = self.player_hand.calculate_score()
        dealer_score = self.dealer_hand.calculate_score()
        outcome_announcement = f"{player_score} to the dealer's {dealer_score}"
        if player_score == dealer_score:
            self.announce(f"You and the dealer tied with {dealer_score} points!")
            outcome = 'tie'
        else:
            outcome = 'loss' if dealer_score > player_score else 'win'
            message = f"You won with {outcome_announcement}! Good job!" if outcome == 'win' else f"You lost with {outcome_announcement}! Too bad!"
            self.announce(message)

        outcomeWindow(root, outcome)
    def check_bust(self):
        player_score = self.player_hand.calculate_score()
        dealer_score = self.dealer_hand.calculate_score()
        if player_score > 21:
            self.announce(f"You busted with a {player_score}! Too bad!")
            outcomeWindow(root, 'loss')
            return True
        if dealer_score > 21:
            self.announce(f"The dealer busted with a {dealer_score}! You win!")
            outcomeWindow(root, 'win')
            return True
        return False
    def deal(self):
        draw = requests.get(f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count=2").json()
        for i in draw['cards']:
            card_name = game_functions.card_conversion(i['code'], True)
            self.player_hand.contents[card_name] = i['value']
            self.announce(f"You drew {'an' if card_name[0] in ['A', 'E', 'I', 'O', 'U'] else 'a'} {card_name}")
        self.announce(f"Your score is {self.player_hand.calculate_score()}")
        self.dealer_hand.draw_cards(self.deck_id, 2)
        self.announce(f"The dealer drew 2 cards!")
    def hit(self):
        hit = requests.get(f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count=1").json()
        for i in hit['cards']:
            card_name = game_functions.card_conversion(i['code'], True)
            self.player_hand.contents[card_name] = i['value']
            self.announce(f"You drew {'an' if card_name[0] in ['A', 'E', 'I', 'O', 'U'] else 'a'} {card_name}")
            self.announce(f"Your score is {self.player_hand.calculate_score()}")
        if self.check_bust() is False:
            # Dealer:
            if self.dealer_hand.calculate_score() >= 17:
                self.stand(False)
            else:
                self.announce("The dealer draws a card!")
                self.dealer_hand.draw_cards(self.deck_id, 1)
                self.check_bust()
    def stand(self, userStand):
        if userStand:
            self.announce("You stand!")
        else:
            self.announce("The dealer stands!")
        self.decide_outcome()


if __name__ == '__main__':
    root = Tk()
    interface = blackjack_gui(root)
    interface.announce("The Game Has Started!")
    interface.deal()
    root.mainloop()
