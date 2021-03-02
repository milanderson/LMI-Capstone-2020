# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 10:39:17 2021

@author: Summer Chambers, Steve Morris and Kaleb Shikur
"""
import pandas as pd
import elasticsearch
from elasticsearch import Elasticsearch, RequestsHttpConnection, ElasticsearchException
import regex as re
from bs4 import BeautifulSoup
import numpy as np
import requests #gets urls
import time
import json
import csv
import os
import sys
import string
from DeDuper import getDupes

class comment_scrapper():
    def __init__(self):
        pass
    
    def retrieve_comments(self, comment_url):
        response = requests.get(comment_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.findAll("a")
        links = [tag["href"] for tag in a_tags]
        txt_links = [link for link in links if '.txt' in link]
        comments = {}
        for suffix in txt_links:
            comments[suffix] = requests.get(comment_url+suffix).text.lower()
            #print(f"scraping comment {suffix}")
        print(f"scraped {len(txt_links)} comments")
        return comments
        


    def write_to_local(self, comments, filepath = 'comments2018.json'):
        
        
        comments = {(key[14:20]): value for key, value in comments.items()}
        sorted_keys = sorted(list(comments.keys()))

        # now for each key in the list
        for i in range(len(comments)-1):
            # get key at index i and key at index i+1 and compare them
            if sorted_keys[i+1][0:4] == sorted_keys[i][0:4]:
                comments[sorted_keys[i+1]] = comments[sorted_keys[i]] + comments[sorted_keys[i+1]]
                del(comments[sorted_keys[i]])
                
        comment_json = json.dumps(comments)
        f = open(filepath,'w')
        f.write(comment_json)
        f.close()
        
        print('successfully uploaded to {}'.format(filepath))
                       
                       
    def dup_removed_chunked_comment(filepath = 'comments2018.json', outpath = 'expanded.json'):
        
        with open(filepath) as f:
            comment = json.load(filepath)
        
        reduced_comments = {key: val for key, val in comment.items() if len(val) >= 30}
       # short_ones = {key: val for key, val in comment.items() if len(val) < 30}
        list_reduced_comments = list(reduced_comments.values())    
        
        duplicates = getDupes(list_reduced_comments)

        tb_deleted = []
        for num, duplist in enumerate(duplicates):
            for idx, comment in enumerate(list_reduced_comments):
                if idx in duplist[:-1]:
                    tb_deleted.append(comment)
        
        unique_comments = {key:value for key, value in reduced_comments.items() if value not in tb_deleted}

        long_comments = {key:value for key, value in unique_comments.items() if len(value) > 5000}  
             
        expanded = unique_comments.copy()
        for key, value in long_comments.items():
            paragraphs = value.split('\n')
            for i in range(len(paragraphs) - 1):
                while i < (len(paragraphs) - 1) and len(paragraphs[i]) < 4800:
                    paragraphs[i] += paragraphs[i+1]
                    del(paragraphs[i+1])
            for i in range(len(paragraphs)):
                expanded[key+'_'+str(i)] = paragraphs[i]
        expanded = {key:value for key, value in expanded.items() if key not in list(long_comments.keys())}

        expanded = {key:value.replace("\t", " ").replace("\r", " ").replace("\n", " ").replace("\s", " ") for key, value in expanded.items()}
        for key, value in expanded.items():
            expanded[key] = ''.join(c for c in value if c in string.printable)                      
            
        dump = json.dumps(expanded)
        f = open(outpath,'w')
        f.write(dump)
        f.close()
        
        print('final version saved as {}'.format(outpath))
                       
                       
    def get_file(self, path = 'expanded.json'):
        with open(path) as f:
            expanded = json.load(f)
        
        return expanded
            
                       
    