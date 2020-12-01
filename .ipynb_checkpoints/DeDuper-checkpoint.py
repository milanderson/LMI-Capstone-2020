from Levenshtein import distance

"""
    Description:
        Find and return duplicative text. Based on Levenshtein edit-distance, with a minimum string length of 30 characters.

    Arguments:
        @texts - A list of strings

    Returns:
        @groups - a list of duplicative-group lists with indices to the original input
"""
def getDupes(texts):
    toProcess = [(i, t) for i, t in enumerate(texts)]

    groups = []
    curIdx, curText = toProcess.pop()
    while toProcess:
        toComb = []
        for i, (compIdx, compText) in enumerate([tup for tup in toProcess]):
            targetLen = max(len(curText), len(compText)) if not len(curText) < 60 and len(compText) < 60 else min(len(curText), len(compText))
            textDist = distance(curText, compText)
            if textDist < (targetLen * 0.30) + max(0, (targetLen/2) - 30):
                toComb.append((i, compIdx, textDist))
        if toComb:
            newGroup = [curIdx]
            for idx, _, _ in toComb:
                newGroup.append(toProcess.pop(idx)[0])
            groups.append(newGroup)
        if toProcess:
            curIdx, curText = toProcess.pop()
    return groups
