"""
Simple Summarizer for ASPC course reviews 
https://github.com/jodylecompte/Simple-Summarizer
"""
# import argparse

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from nltk.probability import FreqDist
from heapq import nlargest
from collections import defaultdict
import time
import re
import pandas as pd 
import numpy as np 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from textblob import TextBlob
import math

# list of course numbers to scrape
#we chose these course numbers as a way to get as many as possible, while
#balancing scraping time. It is around 3 min right now. 
l = ['12', 
'30',
'31',
'66',
'67',
'69',
'72',
'73',
'75',
'76',
'82',
'99',
'100',
'101',
'110',
'111',
'125',
'128',
'130',
'132',
'138',
'169',
'179',
'186',
'191',
'196',
'200',
'206',
'218',
'238',
'255',
'256',
'258',
'261',
'284',
'285',
'290',
'336',
'340',
'344',
'346',
'386',
'411',
'420',
'427',
'433',
'436',
'447',
'448',
'479',
'480',
'486',
'488',
'489',
'501',
'504',
'513',
'518',
'520',
'545',
'586',
'589',
'601',
'606',
'1507',
'1522',
'1550',
'1616',
'1619',
'1621',
'1622',
'1623',
'1632',
'1646',
'1648',
'1652']


NUM_SENT = 5

def main():
    d = compile_reviews()
    d2 = make_dictofsummaries(d)
    give_summaries(d2)


def give_summaries(summarydict):
    """
    Asks user to input names of courses they would like to see summaries of; outputs summary and polarity of all reviews if course
    is in stored dictionary of summaries. When user types break, prints list of courses they have asked about in order of highest
    sentiment score to lowest.
    """
    rankdict = {}
    print("Input courses you are interested in; type break to stop inputting and received ranked list")
    while True:
        course = input("Course name?")
        course = course.lower()
        if course == 'break':
            print("From best ranked by sentiment of all reviews to worst:")
            listofsentiments = list(rankdict.keys())
            listofsentiments.sort(reverse = True) 
            for e in listofsentiments:
                print(rankdict[e])
            break
        elif course in summarydict.keys():
            polarity = round(summarydict[course][1], 5)    
            rankdict[polarity] = course   
            print()
            print('"', summarydict[course][0], '"')
            print('Polarity: ', polarity)
            print() 
        else:
            print('Sorry; not in scraped data')

def make_dictofsummaries(dictofreviews):
    """
    Takes in dictionary where keys are course titles and values are review text and outputs dictionary where 
    keys are course titles and values are summary text
    """
    dictofsummaries = {}
    dictlength = len(dictofreviews.keys())
    for e in dictofreviews.keys():
        text = dictofreviews[e]
        text = clean(text)
        sentence_tokens, word_tokens = tokenize(text)  
        sentence_ranks = score_tokens(word_tokens, sentence_tokens, dictofreviews, dictlength)[0]
        reviews_sentiment = score_tokens(word_tokens, sentence_tokens, dictofreviews, dictlength)[1]
        output = summarize(sentence_ranks, sentence_tokens, NUM_SENT)
        e = e.lower()
        dictofsummaries[e] = [output, reviews_sentiment]
    return dictofsummaries


def compile_reviews():
    """
    go to review pages and get html data
    returns dictionary of course titles with their review text
    """
    reviewdict = defaultdict(str)
    driver = webdriver.Chrome()
    driver.get('https://pomonastudents.org/login/cas')
    select = Select(driver.find_element_by_id('selCollege'))
    select.select_by_visible_text('Pomona College')  # insert any Claremont College name
    driver.find_element_by_id('dispname').send_keys('')  # insert username
    driver.find_element_by_id ('password').send_keys('')  # insert password
    driver.find_element_by_name('_eventId').submit()
    time.sleep(1)
    for e in l:
        classurl = 'https://pomonastudents.org/courses/' + e
        driver.get(classurl)
        data_from_url = driver.page_source
        soup = BeautifulSoup(data_from_url,"html.parser")     
     
        # store course title
        allentries = soup.find_all('h1', {'title'})
        title = str(allentries[-1]) # get course title
        title = re.sub(r'<h1 class="title">', '', title)
        title = re.sub(r'\s+</h1>', '', title)

        # store review text
        allreviews = str(soup.find_all('p', {'subtitle'}))

        reviewdict[title] = allreviews
    driver.close()
    return reviewdict


# list of contractions 
contractions = { 
"ain't": "am not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he would",
"he'd've": "he would have",
"he'll": "he will",
"he's": "he is",
"how'd": "how did",
"how'll": "how will",
"how's": "how is",
"i'd": "i would",
"i'll": "i will",
"i'm": "i am",
"i've": "i have",
"isn't": "is not",
"it'd": "it would",
"it'll": "it will",
"it's": "it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"must've": "must have",
"mustn't": "must not",
"needn't": "need not",
"oughtn't": "ought not",
"shan't": "shall not",
"sha'n't": "shall not",
"she'd": "she would",
"she'll": "she will",
"she's": "she is",
"should've": "should have",
"shouldn't": "should not",
"that'd": "that would",
"that's": "that is",
"there'd": "there had",
"there's": "there is",
"they'd": "they would",
"they'll": "they will",
"they're": "they are",
"they've": "they have",
"wasn't": "was not",
"we'd": "we would",
"we'll": "we will",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what will",
"what're": "what are",
"what's": "what is",
"what've": "what have",
"where'd": "where did",
"where's": "where is",
"who'll": "who will",
"who's": "who is",
"won't": "will not",
"wouldn't": "would not",
"you'd": "you would",
"you'll": "you will",
"you're": "you are"
}


def clean(text):
    """ 
    Clean text to be used for summarizing. Convert to
    lowercase, remove whitespace, replace contractions, 
    remove unwanted characters.
    """
    text = re.sub(r'<p class="subtitle">Reason for taking course: [a-zA-Z]+', '', text)
    text = text.lower()
    replace = {
        ord('\f') : ' ',
        ord('\t') : ' ',
        ord('\n') : ' ',
        ord('\r') : None,
    }
    text = text.translate(replace)
    text = re.sub(r'<p class="subtitle">', '', text)
    text = re.sub(r'</p>', '', text)

   # text = re.sub(r'Reason for taking course: [A-Za-z]+', '', text)

    # Replace contractions
    if True:
        text = text.split()
        new_text = []
        for word in text:
            if word in contractions:
                new_text.append(contractions[word])
            else:
                new_text.append(word)
        text = " ".join(new_text)
    
    # Format words and remove unwanted characters
    text = re.sub(r'https?:\/\/.*[\r\n]*', '', text,  
                  flags=re.MULTILINE)
    text = re.sub(r'\<a href', ' ', text)
    text = re.sub(r'&amp;', '', text) 
    # text = re.sub(r'[_"\-;%()|+&=*%.,!?:#$@\[\]/]', ' ', text)
    text = re.sub(r'[_"\;%()|+&=*%:#$@\[\]/]', ' ', text)   # keep .!?,-
    text = re.sub(r'<br />', ' ', text)
    text = re.sub(r'\'', ' ', text)
    text = re.sub(r'([\.!])\s*,', r'\1 ', text)
    #text = re.sub(r'[\.!]\s*,', ',', text)
    
    # # remove stop words
    #text = text.split()
    #stops = set(stopwords.words("english"))
    #text = [w for w in text if not w in stops]
    #text = " ".join(text)
    return text



def tokenize(content):
    """
    Produces a list of tokenized sentences, 
    a list of tokenized words, and then a list of the tokenized words
    with stop words built from NLTK corpus and Python string class filtered out. 
    """
    stop_words = set(stopwords.words('english') + list(punctuation))
    words = word_tokenize(content)
    
    return [
        sent_tokenize(content),
        [word for word in words if word not in stop_words]    
    ]

# sentence_ranks = score_tokens(word_tokens, sentence_tokens)

dfdict = {} # for document frequency
def score_tokens(filterd_words, sentence_tokens, d, totaldocs):
    """
    Builds a frequency map based on the tf-idf scores for the filtered list of words and 
    uses this to produce a map of each sentence and its total score
    """
    tfdict = {} # for term frequency
    #compiling dictionaries of tf and df
    totalwords = 0
    for word in filterd_words:
        if word in tfdict:
            tfdict[word] += 1
        else:
            tfdict[word] = 1
        for course in d.keys():
            if word in d[course] and word in dfdict:
                dfdict[word] += 1
            elif word in d[course]:
                dfdict[word] = 1
        totalwords += 1
                
    #word_freq = FreqDist(filterd_words)

    tfidf = defaultdict(int)
    sentlength = defaultdict(int)
    score = defaultdict(int)
    totalpolarity = 0
    count = 0
    for i, sentence in enumerate(sentence_tokens):
        count += 1
        sent = TextBlob(sentence)
        totalpolarity += sent.sentiment.polarity
        for word in word_tokenize(sentence):
            if word in tfdict and word in dfdict:
                tfidf[i] += (tfdict[word]/totalwords)*(math.log10(totaldocs/dfdict[word]))
                sentlength[i] += 1
        if sentlength[i] != 0:
            score[i] = (tfidf[i]*100) / sentlength[i]
    return [score, totalpolarity/count]


def summarize(scores, sentences, length):
    """
    Utilizes a ranking map produced by score_token to extract
    the highest ranking sentences in order after converting from
    array to string.  
    """
    if int(length) > len(sentences): 
        print("Error, more sentences requested than available. Use --l (--length) flag to adjust.")
        exit()
    

    indexes = nlargest(length, scores, key=scores.get)
    final_sentences = [sentences[j] for j in sorted(indexes)]
    outputsentences = []
    for sentence in final_sentences:
        newfirst = sentence[0].upper()
        outputsentences.append(newfirst + sentence[1:])
    output = ' '.join(outputsentences) 
    return output



if __name__ == "__main__":
    main()
