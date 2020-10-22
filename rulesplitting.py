'''
Rule Splitting, Uploading to ES
'''
from elasticsearch import Elasticsearch
es = Elasticsearch() #put the aws url in here


def splitRule():
    ...
    #return rulechunks


def ruletoES_lists(rulechunks, i):
    for chunk in rulechunks:
        res = es.index(index=chunk.key, id=i, body=chunk.value)
        i += 1
    print(f"Last id uploaded: {i-1}")


def ruletoES_dicts(rulechunks, i):
    for chunk in rulechunks:
        j = 0
        for key, value in chunk.items():
            res = es.index(index=key, id=i+j, body=value)
            j += 1
        i += j
    print(f"Last id uploaded: {i-1}")

