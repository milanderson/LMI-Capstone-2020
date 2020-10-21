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
    return i


def ruletoES_dicts(rulechunks, i):
    for chunk in rulechunks:
        for j, (key, value) in enumerate(chunk.items()):
            res = es.index(index=chunk.key+key, id=i+j, body=value)
        i += 1
    return i
    
