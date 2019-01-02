#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 08:43:23 2018

@author: amandasill
"""

import urllib.request, re, os, ssl, collections as c, time

def waiting(seconds):
  #print("Waiting for", seconds, "seconds")
  time.sleep(seconds)
  #print('done waiting!')
  
def get_links(url):
    #webpage stuff
    waiting(1)
    context = ssl._create_unverified_context()
    #politeness
    req = urllib.request.Request(url, headers={'User-Agent': 'IUB-I427-asill'})
    web_page = urllib.request.urlopen(req, context = context)
    contents = web_page.read().decode(errors="replace")
    web_page.close()
    
    links = re.findall('(?<=a href=["]).+?(?=["][>]?)', contents)
    return links
    

def crawler(seed, num_pages, directory, algorithm):

    #deque and other variables
    frontier = c.deque([seed])
    front = {seed:1}
    counter = 1
    checked = []
    out_link_count_dict = {}
    in_link_dict = {}

    #the chosen algorithm determines which side of the deque is popped from
    if algorithm == "bfs":
        #first in first out
        url = frontier.popleft()
#        checked.append(url)
    elif algorithm == "dfs":
        #first in last out
        url = frontier.pop()

    #webpage stuff
    waiting(1)
    context = ssl._create_unverified_context()
    #politeness
    req = urllib.request.Request(url, headers={'User-Agent': 'IUB-I427-asill'})
    web_page = urllib.request.urlopen(req, context = context)
    contents = web_page.read().decode(errors="replace")
    web_page.close()
    checked.append(url)
    out_link_count_dict[url] = 0
    in_link_dict[url] = []

    #seems necessary
    base_url = os.path.dirname(url)

    if not base_url:
        base_url = "index.html"

    #wikipedia is weird with what os.path.dirname considers the base url -
    #it add an extra /wiki on the end
    #I haven't found a similar problem with any other site
    if "wikipedia" in base_url:
        #remove the /wiki
        base_url = base_url[:-5]

    #create file name with the counter number followed by .html
    file_name = str(counter) + ".html"

    #where to save the file
    file_path = os.path.join(directory, file_name)

    #save the html file
    with open(file_path, "w", encoding="utf-8") as file_out:
        file_out.write(contents)

    #save and update the index.dat file
    with open(os.path.join(directory, "index.dat"), "a", encoding="utf-8") as record_file:
        record_file.write(file_name + " " + url + "\n")

    #find all the links on the page
    links = re.findall('(?<=a href=["]).+?(?=["][>]?)', contents)
#    for link in links:
#        if link in checked:
#            out_link_count_dict[url] += 1

    #list of unwanted file types
    undesired = [".jpg", ".pdf", ".svg", ".png", ".doc", ".docx", ".tif", ".gif", ".txt", ".rtf", ".js"]
    #list comp to remove unwanted file types
    only_html = [link for link in links if len([extension for extension in undesired if extension in link]) == 0]

    #would not work unless I grabbed only full links
    full_html = []

    #I can't get this to work without eliminating full links
    #I tried only adding the base url to the link if http:// or https:// isn't in the link
    #but it just added it to every link instead of only the ones where the http:// or https:// was missing
    for link in only_html:
        if "http://" in link or "https://" in link:
#            full_link = base_url + link
#            full_html.append(full_link)
#        else:
            full_html.append(link)

#    for item in full_html:
#        if "#" not in item:
#            frontier.append(item)

    #crawler ethics
    robots = base_url + "/robots.txt"
    waiting(1)
    context = ssl._create_unverified_context()
    #politeness
    req = urllib.request.Request(robots, headers={'User-Agent': 'IUB-I427-asill'})
    web_page = urllib.request.urlopen(req, context = context)
    robot_contents = web_page.read().decode(errors="replace")
    web_page.close()

    #grab everything that says disallow
    disallow = re.findall('(?<=Disallow: ).+', robot_contents)

    #list of things to not look at
    dont_look = []

    #make all list item full links and put them in the don't look list
    for item in disallow:
        ignore = base_url + item
        dont_look.append(ignore)

    #add things to the frontier and the dictionary (front)
    for link in full_html:
        if link not in dont_look:
            if link not in front.keys():
                front[link] = 1
                frontier.append(link)
            else:
                front[link] += 1

    #look for links so long as the frontier has something it in
    while len(frontier) > 0:

        #break condition so crawler does not run amok
        if counter == num_pages:
            break

        #things are just repeated from above at this point but slight edits to variable names
        #the chosen algorithm determines which side of the deque is popped from
        if algorithm == "bfs":
            #first in first out
            urls = frontier.popleft()
        elif algorithm == "dfs":
            #first in last out
            urls = frontier.pop()


        #webpage stuff
        waiting(1)
        context = ssl._create_unverified_context()
        #politeness
        req = urllib.request.Request(urls, headers={'User-Agent': 'IUB-I427-asill'})
        web_page = urllib.request.urlopen(req, context = context)
        child_contents = web_page.read().decode(errors="replace")
        web_page.close()
        counter += 1
        checked.append(urls)
        out_link_count_dict[urls] = 0
        in_link_dict[urls] = []
        

        #seems necessary
        child_base_url = os.path.dirname(url)


        if not child_base_url:
            child_base_url = "index.html"

        #wikipedia is weird with what os.path.dirname considers the base url -
        #it add an extra /wiki on the end
        #I haven't found a similar problem with any other site
        if "wikipedia" in child_base_url:
            child_base_url = child_base_url[:-5]

        #create file anme with the counter number followed by .html
        file_name = str(counter) + ".html"

        #where to save the file
        file_path = os.path.join(directory, file_name)

        #save the html file
        with open(file_path, "w", encoding="utf-8") as file_out:
            file_out.write(child_contents)

        #save and update the index.dat file
        with open(os.path.join(directory, "index.dat"), "a", encoding="utf-8") as record_file:
            record_file.write(file_name + " " + urls + "\n")

        #find all the links on the child page
        child_links = re.findall('(?<=a href=["]).+?(?=["][>]?)', child_contents)
#        for link in child_links:
#            if link in checked:
#                out_link_count_dict[urls] += 1

        #list of unwanted file types
        child_undesired = [".jpg", ".pdf", ".svg", ".png", ".doc", ".docx", ".tif", ".gif", ".txt", ".rtf", ".js"]
        #list comp to remove unwanted file types
        child_only_html = [link for link in child_links if len([extension for extension in child_undesired if extension in link]) == 0]

        #would not work unless I grabbed only full links
        child_full_html = []

        #same issue as with above
        for link in child_only_html:
            if "http://" in link or "https://" in link:
                child_full_html.append(link)

        #crawler ethics
        child_robots = child_base_url + "/robots.txt"
        waiting(1)
        context = ssl._create_unverified_context()
        #politeness
        req = urllib.request.Request(child_robots, headers={'User-Agent': 'IUB-I427-asill'})
        web_page = urllib.request.urlopen(req, context = context)
        child_robot_contents = web_page.read().decode(errors="replace")
        web_page.close()

        #grab everything that says disallow
        child_disallow = re.findall('(?<=Disallow: ).+', child_robot_contents)

        #list of things to not look at
        child_dont_look = []

        #make all list item full links and put them in the don't look list
        for item in child_disallow:
            child_ignore = child_base_url + item
            dont_look.append(child_ignore)

        #add things to the frontier and the dictionary (front)
        for link in child_full_html:
            if link not in child_dont_look:
                if link not in front.keys():
                    front[link] = 1
                    frontier.append(link)
                else:
                    front[link] += 1
     
    #grab url we've looked at/saved               
    for url in checked:
        #get all the links from it
        links = get_links(url)
        #for each link in the list of links
        for link in links:
            #if we've look at/saved the link
            if link in checked:
                #add it to the out links count for the url
                out_link_count_dict[url] += 1
                in_link_dict[link].append(url)
                
    #for page rank            
    with open(os.path.join(directory, "out_link_count.txt"), "a", encoding="utf-8") as out_link_count_file:
            out_link_count_file.write(str(out_link_count_dict))
        
    with open(os.path.join(directory, "in_link.txt"), "a", encoding="utf-8") as in_link_file:
            in_link_file.write(str(in_link_dict))
            
    with open(os.path.join(directory, "checked.txt"), "a", encoding="utf-8") as checked_file:
            checked_file.write(str(checked))
    
#    print(checked)
#    print(len(checked))
#    print(counter)
#    print(out_link_count_dict)
#    print()
#    print(in_link_dict)
#    for pair in in_link_dict.items():
#        print(pair)
    

#main
#stack overflow gave me expanduser
#https://stackoverflow.com/questions/3324486/finding-a-files-directory-address-on-a-mac
#bfs_folder = os.path.expanduser("~/Desktop/asillProgAssn1/bfs")
#dfs_folder = os.path.expanduser("~/Desktop/asillProgAssn1/dfs")
bfs_folder = os.path.expanduser("~/Desktop/ASILL FINAL PROJECT")


#bfs
crawler("https://www.indiana.edu/", 200, bfs_folder, "bfs")

#dfs
#crawler("https://en.wikipedia.org/wiki/Cassowary", 50, dfs_folder, "dfs")
