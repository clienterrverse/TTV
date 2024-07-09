import os


def mkdir(directory):
    os.makedirs(directory, exist_ok=True)
