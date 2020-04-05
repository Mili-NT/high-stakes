import os
import ctypes
import random
from tkinter import *
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor # You know its gonna be a fun time when you see this bad boy

def isAdmin():
    """
    :return: True if script is ran as admin/root, otherwise False
    """
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


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
def select_files(number_of_files):
    """
    :param number_of_files: The amount of files you want this function to return
    :return: A list of x number of files, randomly selected
    """
    # Subfunction Code for threading:
    def subcrawler(pathitem):
        for index, path in enumerate(pathitem):
            if index < number_of_files:
                files.append(str(path))
            else:
                randinteger = random.randint(0, index)
                if randinteger < number_of_files:
                    files[randinteger] = str(path)
    # select_files() code:
    files = []
    # The list comprehension creates a list of Path objects for all subdirectories in the root directory
    pathlists = [Path(subdir).rglob('*.*') for subdir in [f.path for f in os.scandir(os.path.abspath(os.sep)) if f.is_dir()]]
    # Creates a ThreadPoolExecutor with a max worker value equal to the amount of subdirectories in the root directory
    with ThreadPoolExecutor(max_workers=len(pathlists)) as executor:
        for i in range(len(pathlists)):
            executor.submit(subcrawler, pathlists[i])
    # The files list ends up being larger than the number_of_files value, and i'm not sure why
    # This simply returns a list of the correct size by randomly picking elements from the files list
    return random.choices(files, k=number_of_files)
def listremove(filelist):
    """
    :param filelist: The list of files to remove, from select_files()
    :return: Nothing
    """
    with open("history.txt", 'a') as f:
        with open("err.txt", 'a') as err:
            for x in filelist:
                try:
                    os.remove(x)
                    f.write(f"{x}\n")
                except PermissionError:
                    err.write(f"Permission Denied: {x}")
