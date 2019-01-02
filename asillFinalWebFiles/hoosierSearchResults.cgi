#! /usr/bin/env python3
print('Content-type: text/html\n')

#for the errors
import cgitb
cgitb.enable()

#import all the things
import cgi, re, os, nltk.stem.porter as p, nltk, string, ast, math, operator
from bs4 import BeautifulSoup as bs

#needed so it runs online
nltk.download("punkt")

#store html form data
form = cgi.FieldStorage()

#get the search terms the user entered from the html form
user = form.getfirst("search", "success grand bloomington")

#title function from part 1
def get_title(file):
    """get the title from the html file"""
    #open file and read contents
    #so many ascii code errors when I put this on burrow and loaded it via web browser
    with open(file, "r", errors="replace") as f:
        contents = f.read()

    #get the title of the file and return it
    title = re.findall('(?<=<title>).+?(?=<\/title>)', contents)

    return title

#file content function from indexer file
def get_file_contents(file, method):
    """reads files using readlines or read depending on method requested"""
    #readlines method
    if method == "l":
        #so many ascii code errors when I put this on burrow and loaded it via web browser
        with open(file, "r", errors='replace') as text:
            lines = text.readlines()

    #read method
    if method == "t":
        #so many ascii code errors when I put this on burrow and loaded it via web browser
        with open(file, "r", errors='replace') as text:
            lines = text.read()

    #return the file contents
    return lines

#used what I did in the indexer in part one to make this function
def get_index_file(indexed_file, method):
    #get the file contents
    index_file = get_file_contents(indexed_file, "l")
    #create an empty list
    index_list = []

    #look at every link in the file contents and strip it then append to the list
    for line in index_file:
        index_list.append(line.strip())

    """maps name of html file to link"""
    #create another list
    index_list_of_lists = []
    #for every item in the first list split it and add it to the new list of lists
    for item in index_list:
        index_list_of_lists.append(item.split())

    if method == "a":
        """dictionary of file name and link"""
        #make a dictionary from the list of lists where the file name is the key and the link is the value
        index_file_dict = {item[0]:item[1] for item in index_list_of_lists}

    elif method == "b":
        """dictionary of link and file name"""
        #make a dictionary from the list of lists where the link is the key and the file name is the value
        index_file_dict = {item[1]:item[0] for item in index_list_of_lists}

    #return the dictionary
    return index_file_dict

#tokenizer function from indexer file
def tokenizer(text):
    """tokenizes text"""
    #create the stopwords file link, get the contents, strip every word and put it into a list
    stop_words_file = os.path.expanduser("stopwords.txt")
    stop_words = get_file_contents(stop_words_file, "l")
    stop_words = [word.strip() for word in stop_words]

    #create an empty string
    long_string = ""
    #look at every item passed in to the function and add it to the string
    for item in text:
        # if type(item) == str:
        long_string += item

    #create a punctuation dictionary - Jason Burnett and I both did the rest of this function during lab
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

def get_word_count(file):
    contents = bs(get_file_contents(file, "t"), "html.parser")
    [tag.extract() for tag in contents(["style", "script", "head", "meta", "[document]", "footer"])]
#    try:
    contents_text = contents.body.find_all(text=True)
#    except:
#        continue

    #tokenize and stem the text
    token_text = tokenizer(contents_text)

    word_count = len(token_text)

    return(word_count)

def retriever(terms_list):
    bfs_invindex = os.path.expanduser("searchFinal/invindex.dat")
    #this page showed me ast
    #https://www.calazan.com/how-to-convert-a-string-to-a-dictionary-in-python/
    #get the inverted index file contents
    invindex_str = get_file_contents(bfs_invindex, "t")
    #turn them into a dictionary we can actually use
    invindex = ast.literal_eval(invindex_str)
    #file with dictionary in it - maps link to word count
    bfs_file_count = os.path.expanduser("searchFinal/file_count.txt")
    #get contents of file and turn back into dictionary
    file_count = get_file_contents(bfs_file_count, "t")
    #maps link to word count of link file - link is key, word count is value
    file_count_dict = ast.literal_eval(file_count)

    #list to put search term in
    terms = []
    #for every word in the terms list qeury
    for word in terms_list:
        #tokenize them - returns a list
        token = tokenizer(word)
        #if the token exists (is not empty)
        if len(token) != 0:
            #add to the created terms list
            terms.append(token[0])

    #list of links that matched the search terms
    exists = []
    #number of hits found
    hits = 0
    #number of pages searched
    count = 0

    #This is really cool.
    #You create a list of lists - there is a sub list for the number of items in the list of query terms.
    #ie list 1 has 4 items so the list of lists has 4 sub lists.
    #Thank you internet:
    #https://stackoverflow.com/questions/5358530/python-creating-a-number-of-lists-depending-on-the-count
    lst_check = [[] for i in range(len(terms))]

    """these pages helped me with tf-idf"""
    #https://medium.freecodecamp.org/how-to-process-textual-data-using-tf-idf-in-python-cd2bbc0a94a3
    #https://towardsdatascience.com/tfidf-for-piece-of-text-in-python-43feccaa74f8

    #all the files needed for this to work
    folder = os.path.expanduser("searchFinal")
    bfs_index = os.path.expanduser("searchFinal/index.dat")
    #link:file name dictionary
    index_dict_b = get_index_file(bfs_index, "b")
    #file name:link dictionary
    index_dict_a = get_index_file(bfs_index, "a")
    #files contained dictionaries to be used for PageRank
    bfs_out_link = os.path.expanduser("searchFinal/out_link_count.txt")
    bfs_in_link = os.path.expanduser("searchFinal/in_link.txt")
    #file containing list to be used for PageRank
    bfs_checked = os.path.expanduser("searchFinal/checked.txt")
    #out link count dictionary
    out_link_count =  get_file_contents(bfs_out_link, "t")
    out_link_count_dict = ast.literal_eval(out_link_count)
    #in link dictionary
    in_link =  get_file_contents(bfs_in_link, "t")
    in_link_dict = ast.literal_eval(in_link)
    #list of all links looked at
    checked =  get_file_contents(bfs_checked, "t")
    checked_list = ast.literal_eval(checked)

    #total number of pages
    N = len(checked_list)

    #list to hold the idf scores for each term
    idf_scores = []

    #look at all terms in the query list
    for term in terms:
        #if the term in a key in the dictionary
        if term in invindex.keys():
            #look through all the sub lists in the value for the term in question
            for item in invindex[term]:
                #update the count since you looked at it
                count += 1
                #if the count for that term is > 0
                if int(item[1]) > 0:
                    #update the count because there was a hit
                    hits += 1
                    #append the link to the lst_check sub list which matches its index position
                    lst_check[terms.index(term)].append(item[0])
                    #append the link to the lst_check sub list which matches its index position
                    total_link = 0
                    #for every sub list in lst)check
                    for lst in lst_check:
                        #count the number of time a link appears and add it to the total link count
                        link_count = lst.count(item[0])
                        total_link += link_count
                        #add it to the exists list if it's not already there
                        if total_link >= (len(lst_check) / 2):
                            if item[0] not in exists:
                                exists.append(item[0])
            #get the number of documents that contain this term
            num_docs = len(lst_check[terms.index(term)])
            #compute the idf score for the given term
            idf = math.log10(N/float(num_docs))
            #add the list of the term and its idf score to the idf_scores list
            idf_scores.append([term,idf])

    #list to hold the tf scores for each document for a given search term
    tf_scores = [[] for i in range(len(terms))]

    #for every file in the link:file name dictionary
    for file in index_dict_b:
        #create path variable
       path = folder + "/" + index_dict_b[file]
       #get just the file name for that file
       fil_nam = index_dict_b[file]
       #get the word count for the file
       word_count = get_word_count(path)
       #get the link for that file
       link = index_dict_a[fil_nam]

       #for each term in the terms list
       for term in terms:
           #if the term is in the inverted index
           if term in invindex.keys():
               #for each list of lists for that term
               for item in invindex[term]:
                   #if the link referenced in the for loop above is in the list
                   if link in item:
                       #if the second item in the list if greater than 0
                       if int(item[1]) > 0:
                           #add the list of the link and the second item/wordcount from above for loop
                           #to the tf_scores sublist that correcponds to the same index position of the term
                           tf_scores[terms.index(term)].append([link,int(item[1])/word_count])

    #create new list for creating tf_scores for the each page-term pair by adding all of
    #the tf_scores list to this new list
    indv_tfidf = tf_scores

    #for every list in the indv tfidf list
    for lst in indv_tfidf:
        #for every list in the idf_scores list
        for pair in idf_scores:
            #for the individual items in every list
            for item in lst:
                #if the index position of the list is the same as the index position of the pair
                if indv_tfidf.index(lst) == idf_scores.index(pair):
                    #the second item in the list is now iteself multiplied by the second item in the pair
                    item[1] = item[1] * pair[1]

    #create a list to put the links in so they only appear once
    full_tfidf = []

    #for every list in the indv_tfidf list
    for lst in indv_tfidf:
        #if the index position of that list is 0
        if indv_tfidf.index(lst) == 0:
            #take that item
            for item in lst:
                #and put it in the tfidf list
                full_tfidf.append(item)
        #if the index position of that list is greater than 0
        elif indv_tfidf.index(lst) > 0:
            #look at the items in the list
            for item  in lst:
                #if the first item is not in the lst
                if item[0] not in lst:
                    #add the whole item to tfidf list
                    full_tfidf.append(item)

    #create dictionary to put final page tfidf scores in
    final_tfidf = {}

    #for each list in the tfidf list
    for item in full_tfidf:
        #if the first item in that list is in the tfidf dictionary
        if item[0] in final_tfidf.keys():
            #set the value for that item to equal its value plus the value of the other item
            final_tfidf[item[0]] += item[1]
        #otherwise
        else:
            #add that item as a key, value pair
            final_tfidf[item[0]] = item[1]

    #for PageRank
    #arbitrarily defined constant
    P = 0.15
    #original PageRank value for all pages
    original = 1/float(N)

    #create initial dictionary to map all links to initial PageRank value
    initial_rank_dict = {}
    for link in in_link_dict.keys():
        initial_rank_dict[link] = original

    #create dictionary where final PageRank values will go
    new_rank_dict = {}

    #this would ne necessary if I kept the while loop for more accuracy, but alas...
    new_ranks_dict = {}
    #look at all the things in the in link dictionary
    for connect, connections in in_link_dict.items():
        #look at the list in the value for the key
        for item in in_link_dict[connect]:
            #if the length of that list is 0
            if len(item) == 0:
                #the page rank for that item is the arbitrary constant / total number of pages
                new_ranks_dict[connect] = P/N
            #otherwise
            else:
                #create variable to hold summed values - make it a float
                summation = 0.0
                #look at the individual links in the list
                for connection in connections:
                    #divide the PageRank of that item buy it's total number of out links
                    summation += initial_rank_dict[connection]/out_link_count_dict[connection]
                #multiply summation by some basic stuff for normalization
                new_ranks_dict[connect] = P/N + (1-P) * summation
    #update dictionary
    new_rank_dict = new_ranks_dict

    #create new dictionary for storing final scores
    most_matched = {}

    #look at all the items in the exists list
    for item in exists:
        #if the item is in both tf-idf and PageRank dictionaries - this account for errors
        if item in final_tfidf.keys() and item in new_rank_dict.keys():
            #add it to the most_matched dictionary and set its value to 0
            most_matched[item] = 0

    #for every link in the dictionary
    for link in most_matched.keys():
        #multiply their tf-idf and PageRank score together and set and value
        most_matched[link] = final_tfidf[link] * new_rank_dict[link]

    #thanks internet for teaching me how to sort dictionaries based on value
    #https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    sort_matches= sorted(most_matched.items(), key=operator.itemgetter(1), reverse=True)

    #limit print out to 25 items - this works even when there are less than 25
    #I tested on another file
    only_25 = sort_matches[0:25]


    #create output variable and tell users how many documents were search and
    #number of hits found
    # output = '<p>Total documents searched: ' + str(count) + '<br>Number of hits found: ' + str(hits) + '</p>'
    output = ""

    #create folder variable
    folder = os.path.expanduser("searchFinal")

    #if the exists list is empty
    if len(exists) == 0:
        #tell user their search did not return any results
        output += '<p>Your search term(s) did not return any results.</p>'
    #otherwise
    else:
    #for each item in the limit to 25 list
        for item in only_25:
            #the first item in that list is the link
            link = item[0]
            #use the link to get the file
            base_file = index_dict_b[link]
            #create full file track
            file_name = folder + "/" + base_file
            #get title from file
            title = get_title(file_name)
            #if the file doesn't have a title
            if len(title) != 0:
                #add to the output telling users the page has no title, make the title a clickable link,
                #and tell users what the tfidf score for that link is for the search terms used
                output += '<p><a href="'+ link +'">' + title[0] + '</a><br>' + link + '<br>TF-IDF Score: ' + str(final_tfidf[link]) + '<br>PageRank Score: ' + str(new_rank_dict[link]) + '<br>TF-IDF * PageRank Score: ' + str(item[1]) + '</p>'
            #otherwise
            else:
                #add to the output telling users the page title, make the title a clickable link,
                #and tell users what the tfidf score for that link is for the search terms used
                output += '<p><a href="' + link + '">This page has no title</a><br>' + link + '<br>TF-IDF Score: ' + str(final_tfidf[link]) + '<br>PageRank Score: ' + str(new_rank_dict[link]) + '<br>TF-IDF * PageRank Score: ' + str(item[1]) + '</p>'

    return output

#main
#make the users search terms a variable and turn them into a list
terms = user.split(" ")

#make the output from the retriever function a variable while calling the function
output = retriever(terms)

#put the html into a variable with a placeholder for the function output
html = '''
<html>
<head><meta charset="utf-8">
<title>Hoosier Search Results</title>
<!-- reset browser -->
    <link rel="stylesheet" href="css/normalize.css"></head>
    <link href="https://fonts.googleapis.com/css?family=Pacifico" rel="stylesheet">
    <link href="css/hoosierSearchResults.css" rel="stylesheet" media="all">
    <body>
        <div class="top">
        <div class="header">
            <a href="hoosierSearch.html">Home</a>
            <a href="aboutSearch.html">About</a>
        </div>
        <div class="row0">
            <h1 class="hoosier">Hoosier</h1>
            <h1 class="logo">Search</h1>
        </div>
            <div class="search">
                <form method="post" action="hoosierSearchResults.cgi">
                    <input type="text" name="search" size="50">
                    <input class="submit" type="submit" name="submit">
                </form>
            </div>
            </div>
            <div class="container">
            <div class="results">
                {content}
            </div>
        </div>
    </body>
</html>'''

#print the function output un the html variable
print(html.format(content = output))
