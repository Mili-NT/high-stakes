import requests
import game_functions
from tkinter import *

# TODO: Popup window announce call doesnt work
# TODO: Card drawing (oh boy)
# TODO: Implement the victory and defeat functions
# TODO: Still, the actual game.

class hand:
    def __init__(self, owner, contents):
        self.owner = owner
        self.contents = contents

    def calculate_score(self):
        nonstandard = ['J', 'Q', 'K', '0']
        converted = [game_functions.card_conversion(val, False) for val in self.contents]
        values = [val[0] if val[0] not in nonstandard else '10' for val in converted]
        if 'A' in values:
            low = sum([int(value) if value != 'A' else 1 for value in values])
            high = sum([int(value) if value != 'A' else 11 for value in values])
            print(f"{low}, {high}")
            score = low if high > 21 else high
        else:
            score = sum([int(v) for v in values])
        return score

    def draw_cards(self, deck_id, count):
        drawn = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={count}").json()
        for i in drawn['cards']:
            self.contents[game_functions.card_conversion(i['code'], True)] = i['value']
class popupWindow(object):
    def __init__(self,master):
        top = self.top=Toplevel(master)
        self.l = Label(top,text="Enter number of files you want to bet: ")
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top,text='Proceed',command=self.cleanup)
        self.b.pack()
        self.master = master
    def cleanup(self):
        blackjack_gui.file_number = self.e.get()
        self.master.announce(f"You bet {blackjack_gui.file_number} files!") # TODO: Yes officer, this line right here
        self.top.destroy()
class blackjack_gui:
    def __init__(self, root):
        self.root = root
        self.file_number = 0
        self.root.title("High-Stakes")
        self.root.geometry("600x400")
        popupWindow(root)
        self.dealer_hand = hand("Dealer", {})
        self.player_hand = hand("Player", {})
        self.deck_id = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=6",
                         params={'jokers_enabled':'false'}).json()['deck_id']
        # Frames And Canvases:
        self.left = Frame(self.root, borderwidth=2, relief="solid")
        self.right = Frame(self.root, borderwidth=2, relief="solid")
        self.opponent_cards = Canvas(self.left, borderwidth=2, relief="solid")
        self.player_cards = Canvas(self.right, borderwidth=2, relief="solid")
        # Announcements:
        self.announcements = Canvas(self.left, borderwidth=2, relief="solid")
        self.scrollbar = Scrollbar(self.announcements)
        self.announcements_label = Label(self.announcements, text="Announcements")
        # Announcements packing:
        self.announcements.pack(side="bottom", expand=True, fill="both", padx=5, pady=5)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.announcements_label.pack()
        # Buttons:
        self.hit_button = Button(self.right, text="Hit", fg="white", bg="black",
                                 command=lambda: self.hit())
        self.stand_button = Button(self.right, text="Stand", fg="white", bg="black",
                                   command=lambda: self.stand())
        # Labels:
        self.opponent_label = Label(self.opponent_cards, text="Opponent's Cards")
        self.player_label = Label(self.player_cards, text="Your Cards")
        self.hit_label = Label(self.hit_button, text="Hit")
        self.stand_label = Label(self.stand_button, text="Stand")
        # Packing:
        self.left.pack(side="left", expand=True, fill="both")
        self.right.pack(side="right", expand=True, fill="both")
        self.stand_button.pack(side="bottom")
        self.hit_button.pack(side="bottom")
        self.opponent_cards.pack(expand=True, fill="both", padx=5, pady=5)
        self.player_cards.pack(expand=True, fill="both", padx=5, pady=5)
        self.opponent_label.pack()
        self.player_label.pack()
        self.hit_label.pack()
        self.stand_label.pack()

    def announce(self, message):
        label = Label(self.announcements, text=message)
        label.pack()

    def hit(self):
        hit = requests.get(f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count=1").json()
        for i in hit['cards']:
            self.player_hand.contents[game_functions.card_conversion(i['code'], True)] = i['value']
            self.announce(f"You drew an {game_functions.card_conversion(i['code'], True)}")
        if self.player_hand.calculate_score() == 21:
            self.announce("Blackjack! You won!")
            game_functions.victory()
    def stand(self):
        dealer_score = self.dealer_hand.calculate_score()
        player_score = self.player_hand.calculate_score()
        if dealer_score > 21:
            self.announce("The dealer has busted!")
            game_functions.victory()
        if player_score > 21:
            self.announce("You busted! What a shame.")
            game_functions.defeat()
        if dealer_score > player_score:
            self.announce(f"The dealer won, with a {dealer_score} to your {player_score}!")
            game_functions.defeat()
        else:
            self.announce(f"You won, with a {player_score} to the dealer's {dealer_score}")
            game_functions.victory()
if __name__ == '__main__':
    root = Tk()
    interface = blackjack_gui(root)
    interface.announce("The Game Has Started!")
    root.mainloop()
