# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 10:56:02 2021

@author: Summer Chambers, Steve Morris and Kaleb Shikur
"""

import requests
import regex as re

class es_upload():
    def __init__(self):
        pass
    
    def splitRule_headers(self, rule_url, startdict):

        alltxt = requests.get(rule_url).text.lower()#.encode('unicode_escape').decode() #encodes like raw strings
        
        #Isolate Section 2
        initialsplit = alltxt.split("ii. provisions of the proposed regulations") #split before section 2
        sec2andon = initialsplit[1] #choose latter half
        sec2list = sec2andon.split("iii. collection of information requirements") #split before section 3
        splitlist = sec2list[0] #choose first half
        
        rulechunks = []
        
        for key, value in startdict.items():    
           splitlist = splitlist.split(value[0]) #split on start of desired section
           split_further = splitlist[1].split(value[1]) #split again on start of undesired section
           rulechunks.append({"section": key, "text": (value[0]+split_further[0])}) #choose only first half to upload to dict
           splitlist = splitlist[1] #choose second half to prepare for next split
    
        return rulechunks


    def splitRule_line_hybrid(self, rule_url, startdict):
        new_rule_chunks = []
        chunks = self.splitRule_headers(rule_url, startdict)
        for doc in chunks:
            paragraphs = doc["text"].split('\r\n')
            #add new lines while under 6000 characters
            for i in range(len(paragraphs) - 1):
                while i < (len(paragraphs)-1) and len(paragraphs[i]) < 6000:
                    paragraphs[i] += paragraphs[i+1]
                    del(paragraphs[i+1])
            for i in range(len(paragraphs)):
                new_rule_chunks.append({"section": doc["section"]+str(i), "text": paragraphs[i]})
        return new_rule_chunks
    
    
    def rulesplit_toES(self, rulechunks, es_index):
        for chunk in rulechunks:
                res = es.index(index=es_index, id=chunk["section"], body=chunk, doc_type='_doc')
                es.indices.refresh(index=es_index)
        print("Last id uploaded:", chunk["section"])
        
        



    