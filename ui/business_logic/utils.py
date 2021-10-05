'''Choices list getters, to fill the page select-boxes'''
import os


'''Returns the list of shares stored in .../static/csv'''
def get_shares():
    shares = []
    for filename in os.listdir('ui/static/csv'):
        if filename.endswith('.csv'):
            name = filename[:-4]
            shares.append((name, name.capitalize()))
    return shares