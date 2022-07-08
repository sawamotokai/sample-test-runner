import os

def writeFile(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        for _row in data:
            row = _row.replace("\n", "")
            if row != "" and row != " ":
                f.write(row + "\n")
