#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 11:02:39 2018

@author: amandasill
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 12:15:57 2018

@author: amandasill
"""

"""
For this assignment, I worked with lists,  dictionaries, and files. THe files were read
in and the turned into lists. From there, the lists were used to create dictionaries. 
Some of the dictionaries were then used to create lists inside dictionaries.

In this assignment, I decided to create helper functions that I could call as opposed
to doing everything inside the main program as I did last time. So all file opening and
reading of contents is a helper function call. I also did the tokenizing and stemming in
a helper function as both programs for this assignment needed to use tokenizing and
stemming.

Some of the code in this file was stuff I pulled from lab assignments. During lab 
assignments, Jason Burnett and I discuss the assignment and approaches so some code 
may be similar to his due to that. Additionally, Moses has gone over some difficult 
parts of lab assignments and I made note of how he went about things, so some code 
below is how he created things in lab. All code relevant to that is noted where
appropriate in the code below.

The issue I had with this file was in creating the final inverted index (inversion{}).
I tried several different things to get it to populate correctly, but had to go with 
what I have below. It's mostly correct, and the output for the retriever isn't 
affected, so ultimately it's fine. I describe more in detail in comments by that section.
"""

import re, os, nltk.stem.porter as p, nltk, string
from bs4 import BeautifulSoup as bs

def get_title(file):
    """get the title from the html file"""
    #open file and read contents
    with open(file, "r") as f:
        contents = f.read()
    
    #get the title of the file and return it
    title = re.findall('(?<=<title>).+?(?=<\/title>)', contents)
    
    return title

def get_file_contents(file, method):
    """reads files using readlines or read depending on method requested"""
    #readlines method
    if method == "l":
        with open(file, "r") as text:
            lines = text.readlines()
    
    #read method
    if method == "t":
        with open(file, "r") as text:
            lines = text.read()
    
    #return the file contents
    return lines

def tokenizer(text):
    """tokenizes text"""
    #create the stopwords file link, get the contents, strip every word and put it into a list
    stop_words_file = os.path.expanduser("~/Desktop/stopwords.txt")
    stop_words = get_file_contents(stop_words_file, "l")
    stop_words = [word.strip() for word in stop_words]

    #create an empty string
    long_string = ""
    #look at every item passed in to the function and add it to the string
    for item in text:
        long_string += item
    
    #create a punctuation dictionary - Jason Burnett and I both did the rest of this function during lab very similarly
    translation = str.maketrans("","",string.punctuation)
    #clean up the text anf remove punctuation
    clean = long_string.replace("\n", " ").lower()
    clean = clean.translate(translation)
    #tokenize the clean text
    tokenize = nltk.word_tokenize(clean)
    
    #remove stopwords and any term that starts with http (it feel unnecessary to have)
    [tokenize.remove(word) for word in tokenize if word in stop_words]
    [tokenize.remove(word) for word in tokenize if word.startswith("http")]

    #create the stemmer
    stemmer = p.PorterStemmer()
    #stem all the words that were tokenized and put them in a list
    stem_words = [stemmer.stem(word) for word in tokenize]
    
    #return the stemmed text
    return stem_words

def indexer(folder, indexed_file):
    """a function to index a webpage"""
    #get the file contents of the indexed file
    index_file = get_file_contents(indexed_file, "l")
    #create a new list
    index_list = []
    
    #look at every line in the indexed file, strip it, and append it to the list
    for line in index_file:
        index_list.append(line.strip())
    
    """maps name of html file to link"""
    #create another list
    index_list_of_lists = []
    #for every item in the first list split it and add it to the new list of lists
    for item in index_list:
        index_list_of_lists.append(item.split())
    
    """dictionary of file name and link"""
    #make a dictionary from the list of lists where the file name is the key and the link is the value
    index_file_dict = {item[0]:item[1] for item in index_list_of_lists}   
    
    #create dictionaries 
    """inverted index with all the things"""
    word_map_dict = {}
    
    #create a list and populate with files from folder
    file_list = [folder +"/"+ file for file in os.listdir(folder) if file[-5:] == ".html"]
    
    file_count_dict = {}
    
    words_lst = []
    
    
    #this is to test program on smaller scale
#    file_list2 = [os.path.expanduser("~/Desktop/asillProgAssn2/dfs/0.html"), os.path.expanduser("~/Desktop/asillProgAssn2/dfs/1.html")]
#    print(file_list)
#    titles = []
    #look through the list of files
    for item in file_list:
        #create individual file 
        file = os.path.expanduser(item)
        
        #pulling just the file not from the path
        file_name = file[-7:]
        file_name = file_name.strip("/")
       
        #get the title from the file
        title = get_title(file)
#        titles.append(title)
#
        #get contents of file using beautiful soup
        contents = bs(get_file_contents(file, "t"), "html.parser")
        #get rid of stull we don't need
        [tag.extract() for tag in contents(["style", "script", "head", "meta", "[document]", "footer"])]
        #get everything from the bosy using beautiful soup
        try:
            contents_text = contents.body.find_all(text=True)
        except:
            continue

        #tokenize and stem the text
        token_text = tokenizer(contents_text)
        
        word_count = len(token_text)
        
        #use the file name from above to find the key and put the tokenized text for that key as the value
#        link_word_dict[index_file_dict[file_name]] = token_text
        
        #create url variable
        url = index_file_dict[file_name]
        
        file_count_dict[url] = word_count
        
        #create dictionary with necessary information to output into the docs.dat file
        file_write_dict = {'Name':file_name, 'Length':word_count, 'Title':title, 'URL':url}
#        
#        #docs.dat file creation    
        with open(os.path.join(folder, "docs.dat"), "a", encoding="utf-8") as record_file:
            record_file.write(str(file_write_dict)) 

        for word in token_text:
            if word not in words_lst:
                words_lst.append(word)
                
#        for i in range(len(file_list)):
        for word in words_lst:
            if word in token_text:
                word_total = token_text.count(word)
            else:
                word_total = 0
#            print(word_total)
            word_map = []
            link_name = index_file_dict[file_name]
            word_map.append([link_name,word_total])
            if word in word_map_dict:
                word_map_dict[word] += word_map
            else:
                word_map_dict[word] = word_map
#         
        

#    print(word_map_dict)

                             
    #write final inverted index dictionary to invindex.dat file
    with open(os.path.join(folder, "invindex.dat"), "a", encoding="utf-8") as test_file:
            test_file.write(str(word_map_dict))
            
    with open(os.path.join(folder, "file_count.txt"), "a", encoding="utf-8") as new_file:
            new_file.write(str(file_count_dict))
    

#main
#bfs stuff
bfs_folder = os.path.expanduser("~/Desktop/bfs")
bfs_index = os.path.expanduser("~/Desktop/bfs/index.dat")
#dfs stuff
dfs_folder = os.path.expanduser("~/Desktop/dfs")
dfs_index = os.path.expanduser("~/Desktop/dfs/index.dat")

indexer(bfs_folder, bfs_index)
indexer(dfs_folder, dfs_index)