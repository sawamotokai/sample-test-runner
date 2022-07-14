import os
import inquirer
from inquirer.themes import GreenPassion


def writeFile(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        for _row in data:
            row = _row.replace("\n", "")
            if row != "" and row != " ":
                f.write(row + "\n")

def touch(fname):
    try:
        os.utime(fname, None)
    except OSError as e:
        open(fname, 'a').close()

class Ask():
    @staticmethod
    def text(message):
        return inquirer.prompt(
            questions=[
                inquirer.Text('ans',
                message=message)],
            theme=GreenPassion())['ans']

    @staticmethod
    def list_input(message, choices):
        return inquirer.prompt(
            questions=[
                inquirer.List('ans',
                message=message,
                choices=choices)],
            theme=GreenPassion())['ans']

    

