#!/home/rudraksh/anaconda2/bin/python
# -*- coding: utf-8 -*-

import argparse
from CustomTokenizer import RedditTokenizer	
import re
from nltk.corpus import stopwords
import codecs
from nltk import PunktSentenceTokenizer

parser = argparse.ArgumentParser()

parser.add_argument("-rp","--remove_punctuation", help="Strips punctuation from tweets. (Leaves 'he's','good-job' etc. unchanged)", type=bool, default=True)
parser.add_argument("-rl","--remove_links", help="Removes HTTP links from tweets.", type=bool, default=True)
parser.add_argument("-l","--lowercase", help="Convert to lowercase", type=bool, default=True)
parser.add_argument("-rlen","--reduce_len", help="Reduce len of strings like heyyyy to heyy etc.", type=bool, default=True)
parser.add_argument("-rstop","--remove_stopwords", help="Removes stopwords (and, are, not etc.) from tweets. Default: English", type=bool, default=False)
parser.add_argument("-p2l","--para_to_lines", help="Splits paragraph to lines.", type=bool, default=True)


parser.add_argument("input_file", help="Location of input file along with name", type=str)
parser.add_argument("output_file", help="Location of output file along with name", type=str)
args = parser.parse_args()


class Config():
    def __init__(self, remove_punctuation, remove_links, lowercase, reduce_len,
                 remove_stopwords, para_to_lines, input_file, output_file):
        

        self.remove_punctuation = remove_punctuation#
        self.remove_links = remove_links
        self.lowercase = lowercase
        self.reduce_len = reduce_len
        self.remove_stopwords = remove_stopwords#
        self.para_to_lines = para_to_lines#
        
        # Storage Related
        self.input_file = input_file
        self.output_file = output_file

def main():
    c = Config(
        args.remove_punctuation,
        args.remove_links,
        args.lowercase,
        args.reduce_len,
        args.remove_stopwords,
        args.para_to_lines,
        args.input_file,
        args.output_file
    )

    # Configure TweetTokenizer.
    tknzr = RedditTokenizer(
                           strip_links = c.remove_links,
                           preserve_case = not c.lowercase,
                           reduce_len = c.reduce_len,
                           )

    p_tknzr = PunktSentenceTokenizer()

    # Punctuation to remove.
    punct_re = re.compile(r"[\!\"\'\#\$\%\&\\\(\)\*\+\,\-\.\/\:\@\;\<\=\>\?\[\\\]\^\_\`\{\|\}\~]")
    
    # Stopwords.
    en_stopwords =  set(stopwords.words('english'))

    i = 1

    with codecs.open(c.output_file, 'w', 'utf-8')  as outfile:
        
        j = 0
        # Count the number of comments in file.
        with codecs.open(c.input_file, 'r', 'utf-8') as infile:
            for comment in infile:
                j += 1

        with codecs.open(c.input_file, 'r', 'utf-8') as infile:
            for comment in infile:
                try:
                    # Convert paragraph into individual lines, if mentioned in config file.
                    if c.para_to_lines:
                        
                        lines = [p_tknzr.tokenize(x) for x in comment.split('\n')]
                        # Flatten list.
                        lines = [item for sublist in lines for item in sublist]
                    else:
                        lines = [comment]
                            
                    
                    for line in lines:
                        try:
                            # Tokenize the line based on config.
                            line = tknzr.tokenize(line)

                            if len(line) != 0:
                            
                                if c.remove_punctuation:
                                    line = [word for word in line if len(punct_re.findall(word)) != len(word)]
                                    
                                if c.remove_stopwords:
                                    line = [word for word in line if word.lower() not in en_stopwords]
                                    
                                outfile.write(' '.join(line) + '\n')  
                        except:                           
                            continue

                    i+= 1

                    if i % 10000 == 0:
                        print("Iterated over {}/{} comments.".format(i,j)) 
                except:
                    continue

if __name__ == "__main__":
    main()
    print('Task Completed.')
