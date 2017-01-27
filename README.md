# Data-Cleaning

**1) CustomTokenizer.py**  
- Mostly reused code from NLTK's TweetTokenizer.
- Contains specific tokenizers for both Reddit and Twitter.
- Support for Tokenizing Emojis. Earlier, emojis like 👩‍🏫 (specifically modifier and zwj sequences) would get split into 👩 and 🏫. This tokenizer takes care of that case.
- For emojis containing variation filter, the filter tag ranging from u"\U0001F3FB-\U0001F3FF" is removed.

**2) CleanTwitter.py** - Command line utility for pre-processing Twitter data.

**3) CleanReddit.py** - Command line utility for pre-processing Reddit data.
