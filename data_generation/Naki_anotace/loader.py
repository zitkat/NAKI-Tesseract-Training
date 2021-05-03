import glob
import os
import os.path
import codecs
import numpy as np


def loadDir(directory):
    indexes = []
    data = {}
    files = sorted(glob.glob(os.path.join(directory, "*.txt")))
    for f in files:
        text = list(reversed(codecs.open(f, encoding="utf-8").read().split("\n")))
        for row in text:
            if len(row) == 0:
                continue
            arr = row.split("#")
            if int(arr[2]) in indexes:
                continue
            indexes.append(int(arr[2]))
            if arr[3] == "THRASH" or arr[3] == "DEL":
                key0 = arr[3]
                if data.get(key0, None) is None:
                    data[key0] = []
                data[key0].append({"our": [int(arr[6]), int(arr[7]), int(arr[8]), int(arr[9])],
                                       "original": [int(arr[11]), int(arr[12]), int(arr[13]), int(arr[14])],
                                       "key1": arr[4].lower(), "key2": arr[5].lower(),
                                   "conf": float(arr[10]), "file": arr[1]})
            else:
                if data.get(arr[5].lower(), None) is None:
                    data[arr[5].lower()] = []
                data[arr[5].lower()].append({"our": [int(arr[6]), int(arr[7]), int(arr[8]), int(arr[9])],
                   "original": [int(arr[11]), int(arr[12]), int(arr[13]), int(arr[14])],
                   "key1": arr[4].lower(), "key2": arr[5].lower(), "conf": float(arr[10]), "file": arr[1]})
    return data

def printStat(d):
    print("Celkem:", len(d))
    for key in d:
        print(key, len(d[key]))

def computeConfVector(f, chars, pairs):
    text = list(reversed(codecs.open(f, encoding="utf-8").read().split("\n")))
    indexes = []
    for row in text:
        if len(row) == 0:
            continue
        arr = row.split("#")
        if int(arr[2]) in indexes:
             continue
        indexes.append(int(arr[2]))
        if arr[3] == "THRASH":
            continue
        else:
            key1 = arr[4].lower()
            key2 = arr[5].lower()
            if key1 not in chars:
                chars.append(key1)
            if key2 not in chars:
                chars.append(key2)
            pairs.append([chars.index(key1), chars.index(key2)])
    return chars, pairs


def confMatrix(chars, pairs):
    M = np.zeros((len(chars), len(chars)))
    for item in pairs:
        M[item[0], item[1]] += 1
    return M


def confMatrixAll(directory):
    files = sorted(glob.glob(os.path.join(directory, "*.txt")))
    chars = []
    pairs = []
    for f in files:
        chars, pairs = computeConfVector(f, chars, pairs)
    M = confMatrix(chars, pairs)
    return chars, M


def main():
    chars, M = confMatrixAll("anotace")
    print(chars)
    for row in M:
        print(row)
    file = open('ConvM.txt', 'w')
    file.write(str(chars)+"\n")
    for row in M:
        file.write(str(row)+"\n")

    file.close()

if __name__ == "__main__":
    main()
#printStat(loadDir("output"))

# Spocteni confusion pro vsechny anotace
#ch, m = confMatrixAll("output")
#print(m)
#print(len(ch),ch)


