# Simple Summarizer  
A simple summarizer that summarizes all course reviews for a given class in a user-specified number of sentences, as well as sentiment scoring of the produced summary. 

## Introduction & Motivation  
Team: Dana Wang, Emma Vorenberg, Michelle Li  
Final project for CS35: CS for Insight  

What constitutes a 'good' class for a student varies by student and their priorities. Currently, in order for students to learn about a course, they must read through every review and depend on a simple aggregated rating out of 5 stars. However, reading every review is time-consuming and star ratings give little information on understanding more nuanced information about a course--a person may rate a course 4/5 stars, but for many different reasons (too much work but interesting content, unapproachable professor but good lecturer, great professor but insanely difficult, etc.). 

Thus, we set out to create a program that could output a few-sentence summary of any given course on the ASPC course review website, plus sentiment analysis. The summary gives more detail and specificity into the experience of a  course in a short read. 


## Tech/Framework
Project is created with:  
* Python v. 3.6
* Main libraries:
  + Selenium: webdriver to log in to Pomona's Central Authentication System
  + Beautiful Soup: scrape course reviews from sites
  + NLTK: text analysis
  + TextBlob: sentiment analysis 

We modeled our code off of the following sources:  
(1) https://towardsdatascience.com/write-a-simple-summarizer-in-python-e9ca6138a08e  
(2) https://towardsdatascience.com/text-summarization-with-amazon-reviews-41801c2210b  

We created a program that, given the entirety of text of course reviews for a specific course, would clean the text (convert to lowercase, remove whitespace, expand contractions, etc.), tokenize by word and sentence, and score each sentence. The scoring is done by TFI-DF (term frequency–inverse document frequency). Instead of scraping the course website every time we needed to produce a summary, we decided to simply store many courses and their corresponding reviews in a dictionary. This is done to maximize the number of words in the TFI-DF corpus.

We also included a polarity scoring (ranging from -1, strongly negative, to +1, strongly positive). First, we averaged the polarity score of every sentence in every review for a given course, but found these scores to be less informative than we imagined because overall, people tend to give positive reviews. Thus, we chose to output a polarity score based on the summary we output (not the reviews overall). 

How the program functions:  
First, our program prompts the user for a course name. If it is not in the dictionary, the user is told as such. If it is, our program then uses our summarizing functionality to output a 5 sentence summary on the course and its corresponding polarity score. The user is repeatedly prompted to input more courses, until they type ‘break’. At this point, our program outputs a list of all inputted course titles, listed from highest to lowest polarity scoring. We added this function so that we could give the user an immediate sense of how positively/negatively the courses are rated in relation to each other, which can help guide them in making a decision about which course to take. 

Our program performed surprisingly well, especially given such a simple scoring algorithm and we were very pleased with our results.


## Example Summaries  
These are actual outputs from our program. 

CS5:  

“I loved this course! There is a written midterm and final as well as a final project, but they are weighted as two homework assignments each, which is really nice. If you are not really planning on taking a lot of comp sci, but want to explore the field, definitely take it with him. Not hard to get an a if you put in the work, and you learn a lot about coding and how computers work in general. One of the best classes I have taken in my time at Pomona.”

Overall sentiment: Positive, polarity = 0.425


Economic Statistics:  

“This class was hard. Do not take this class with gary smith! Such a bad class. Awful class. This class was painful for me.”

Overall sentiment: Negative, polarity = -0.468

