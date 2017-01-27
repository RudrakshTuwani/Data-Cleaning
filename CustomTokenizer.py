#!/home/rudraksh/anaconda2/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
from nltk.compat import htmlentitydefs, int2byte, unichr


######################################################################
# The following strings are components in the regular expression
# that is used for tokenizing. It's important that phone_number
# appears first in the final regex (since it can contain whitespace).
# It also could matter that tags comes after emoticons, due to the
# possibility of having text like
#

#     <:| and some text >:)
#
# Most importantly, the final element should always be last, since it
# does a last ditch whitespace-based tokenization of whatever is left.

# ToDo: Update with http://en.wikipedia.org/wiki/List_of_emoticons ?

# This particular element is used in a couple ways, so we define it
# with a name:
EMOTICONS = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
      |
      <3                         # heart
    )"""

# URL pattern due to John Gruber, modified by Tom Winzig. See
# https://gist.github.com/winzig/8894715

URLS = r"""     # Capture 1: entire matched URL
  (?:
  https?:       # URL protocol and colon
    (?:
      /{1,3}        # 1-3 slashes
      |         #   or
      [a-z0-9%]       # Single letter or digit or '%'
                                       # (Trying not to match e.g. "URI::Escape")
    )
    |         #   or
                                       # looks like domain name followed by a slash:
    [a-z0-9.\-]+[.]
    (?:[a-z]{2,13})
    /
  )
  (?:         # One or more:
    [^\s()<>{}\[\]]+      # Run of non-space, non-()<>{}[]
    |         #   or
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\) # balanced parens, one level deep: (...(...)...)
    |
    \([^\s]+?\)       # balanced parens, non-recursive: (...)
  )+
  (?:         # End with:
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\) # balanced parens, one level deep: (...(...)...)
    |
    \([^\s]+?\)       # balanced parens, non-recursive: (...)
    |         #   or
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]  # not a space or one of these punct chars
  )
  |         # OR, the following to match naked domains:
  (?:
    (?<!@)              # not preceded by a @, avoid matching foo@_gmail.com_
    [a-z0-9]+
    (?:[.\-][a-z0-9]+)*
    [.]
    (?:[a-z]{2,13})
    \b
    /?
    (?!@)             # not succeeded by a @,
                            # avoid matching "foo.na" in "foo.na@example.com"
  )
"""

# The components of the tokenizer:
REGEXPS = (
    URLS,
    # Phone numbers:
    r"""
    (?:
      (?:            # (international)
        \+?[01]
        [\-\s.]*
      )?
      (?:            # (area code)
        [\(]?
        \d{3}
        [\-\s.\)]*
      )?
      \d{3}          # exchange
      [\-\s.]*
      \d{4}          # base
    )"""
    ,
    # ASCII Emoticons
    EMOTICONS
    
    ,
    # Unicode Emojis.
    r'\U0001f469\u200d\U0001f467\u200d\U0001f467|\U0001f469\u200d\U0001f467\u200d\U0001f466|\U0001f469\u200d\U0001f467|\U0001f469\u200d\U0001f466\u200d\U0001f466|\U0001f469\u200d\U0001f466|\U0001f468\u200d\U0001f467\u200d\U0001f467|\U0001f468\u200d\U0001f467\u200d\U0001f466|\U0001f468\u200d\U0001f467|\U0001f468\u200d\U0001f466\u200d\U0001f466|\U0001f468\u200d\U0001f466|\U0001f469\u200d\U0001f469\u200d\U0001f467\u200d\U0001f467|\U0001f469\u200d\U0001f469\u200d\U0001f466\u200d\U0001f466|\U0001f469\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466|\U0001f469\u200d\U0001f469\u200d\U0001f467|\U0001f469\u200d\U0001f469\u200d\U0001f466|\U0001f468\u200d\U0001f468\u200d\U0001f467\u200d\U0001f467|\U0001f468\u200d\U0001f468\u200d\U0001f466\u200d\U0001f466|\U0001f468\u200d\U0001f468\u200d\U0001f467\u200d\U0001f466|\U0001f468\u200d\U0001f468\u200d\U0001f467|\U0001f468\u200d\U0001f468\u200d\U0001f466|\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f467|\U0001f468\u200d\U0001f469\u200d\U0001f466\u200d\U0001f466|\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466|\U0001f468\u200d\U0001f469\u200d\U0001f467|\U0001f468\u200d\U0001f469\u200d\U0001f466|\U0001f469\u200d\U0001f692|\U0001f468\u200d\U0001f692|\U0001f469\u200d\U0001f680|\U0001f468\u200d\U0001f680|\U0001f469\u200d\U0001f3a8|\U0001f468\u200d\U0001f3a8|\U0001f469\u200d\U0001f3a4|\U0001f468\u200d\U0001f3a4|\U0001f469\u200d\U0001f4bb|\U0001f468\u200d\U0001f4bb|\U0001f469\u200d\U0001f52c|\U0001f468\u200d\U0001f52c|\U0001f469\u200d\U0001f4bc|\U0001f468\u200d\U0001f4bc|\U0001f469\u200d\U0001f3ed|\U0001f468\u200d\U0001f3ed|\U0001f469\u200d\U0001f527|\U0001f468\u200d\U0001f527|\U0001f469\u200d\U0001f373|\U0001f468\u200d\U0001f373|\U0001f469\u200d\U0001f33e|\U0001f468\u200d\U0001f33e|\U0001f469\u200d\U0001f3eb|\U0001f468\u200d\U0001f3eb|\U0001f469\u200d\U0001f393|\U0001f468\u200d\U0001f393|\U0001f3f3\u200d\U0001f308|\U0001f441\u200d\U0001f5e8|\U0001f469\u200d\u2764\u200d\U0001f469|\U0001f468\u200d\u2764\u200d\U0001f468|\U0001f469\u200d\u2764\u200d\U0001f468|\U0001f469\u200d\u2764\u200d\U0001f48b\u200d\U0001f469|\U0001f468\u200d\u2764\u200d\U0001f48b\u200d\U0001f468|\U0001f469\u200d\u2764\u200d\U0001f48b\u200d\U0001f468|\U0001f939\u200d\u2640|\U0001f939\u200d\u2642|\U0001f93e\u200d\u2640|\U0001f93e\u200d\u2642|\U0001f93d\u200d\u2640|\U0001f93c\u200d\u2642|\U0001f938\u200d\u2640|\U0001f938\u200d\u2642|\U0001f6b5\u200d\u2640|\U0001f6b5\u200d\u2642|\U0001f6b4\u200d\u2640|\U0001f6b4\u200d\u2642|\U0001f3cb\u200d\u2640|\U0001f3cb\u200d\u2642|\u26f9\u200d\u2640|\u26f9\u200d\u2642|\U0001f3ca\u200d\u2640|\U0001f3ca\u200d\u2642|\U0001f6a3\u200d\u2640|\U0001f6a3\u200d\u2642|\U0001f3c4\u200d\u2640|\U0001f3c4\u200d\u2642|\U0001f3cc\u200d\u2640|\U0001f46f\u200d\u2642|\U0001f3c3\u200d\u2640|\U0001f3c3\u200d\u2642|\U0001f6b6\u200d\u2640|\U0001f6b6\u200d\u2642|\U0001f487\u200d\u2640|\U0001f487\u200d\u2642|\U0001f486\u200d\u2640|\U0001f486\u200d\u2642|\U0001f937\u200d\u2640|\U0001f937\u200d\u2642|\U0001f926\u200d\u2640n|\U0001f926\u200d\u2642|\U0001f647\u200d\u2640|\U0001f647\u200d\u2642|\U0001f64b\u200d\u2640|\U0001f64b\u200d\u2642|\U0001f481\u200d\u2640|\U0001f481\u200d\u2642|\U0001f646\u200d\u2640|\U0001f646\u200d\u2642|\U0001f645\u200d\u2640|\U0001f645\u200d\u2642|\U0001f64e\u200d\u2640|\U0001f64e\u200d\u2642|\U0001f64d\u200d\u2640|\U0001f64d\u200d\u2642|\U0001f471\u200d\u2640|\U0001f471\u200d\u2642|\U0001f473\u200d\u2640|\U0001f473\u200d\u2642|\U0001f477\u200d\u2640|\U0001f477\u200d\u2642|\U0001f482\u200d\u2640|\U0001f482\u200d\u2642|\U0001f575\u200d\u2640|\U0001f575\u200d\u2642|\U0001f46e\u200d\u2640|\U0001f46e\u200d\u2642|\U0001f469\u200d\u2708|\U0001f468\u200d\u2708|\U0001f469\u200d\u2696|\U0001f468\u200d\u2696|\U0001f469\u200d\u2695|\U0001f468\u200d\u2695|\U0001f1ff\U0001f1fc|\U0001f1ff\U0001f1f2|\U0001f1ff\U0001f1e6|\U0001f1fe\U0001f1f9|\U0001f1fe\U0001f1ea|\U0001f1fd\U0001f1f0|\U0001f1fc\U0001f1f8|\U0001f1fc\U0001f1eb|\U0001f1fb\U0001f1fa|\U0001f1fb\U0001f1f3|\U0001f1fb\U0001f1ee|\U0001f1fb\U0001f1ec|\U0001f1fb\U0001f1ea|\U0001f1fb\U0001f1e8|\U0001f1fb\U0001f1e6|\U0001f1fa\U0001f1ff|\U0001f1fa\U0001f1fe|\U0001f1fa\U0001f1f8|\U0001f1fa\U0001f1f3|\U0001f1fa\U0001f1f2|\U0001f1fa\U0001f1ec|\U0001f1fa\U0001f1e6|\U0001f1f9\U0001f1ff|\U0001f1f9\U0001f1fc|\U0001f1f9\U0001f1fb|\U0001f1f9\U0001f1f9|\U0001f1f9\U0001f1f7|\U0001f1f9\U0001f1f4|\U0001f1f9\U0001f1f3|\U0001f1f9\U0001f1f2|\U0001f1f9\U0001f1f1|\U0001f1f9\U0001f1f0|\U0001f1f9\U0001f1ef|\U0001f1f9\U0001f1ed|\U0001f1f9\U0001f1ec|\U0001f1f9\U0001f1eb|\U0001f1f9\U0001f1e9|\U0001f1f9\U0001f1e8|\U0001f1f9\U0001f1e6|\U0001f1f8\U0001f1ff|\U0001f1f8\U0001f1fe|\U0001f1f8\U0001f1fd|\U0001f1f8\U0001f1fb|\U0001f1f8\U0001f1f9|\U0001f1f8\U0001f1f8|\U0001f1f8\U0001f1f7|\U0001f1f8\U0001f1f4|\U0001f1f8\U0001f1f3|\U0001f1f8\U0001f1f2|\U0001f1f8\U0001f1f1|\U0001f1f8\U0001f1f0|\U0001f1f8\U0001f1ef|\U0001f1f8\U0001f1ee|\U0001f1f8\U0001f1ed|\U0001f1f8\U0001f1ec|\U0001f1f8\U0001f1ea|\U0001f1f8\U0001f1e9|\U0001f1f8\U0001f1e8|\U0001f1f8\U0001f1e7|\U0001f1f8\U0001f1e6|\U0001f1f7\U0001f1fc|\U0001f1f7\U0001f1fa|\U0001f1f7\U0001f1f8|\U0001f1f7\U0001f1f4|\U0001f1f7\U0001f1ea|\U0001f1f6\U0001f1e6|\U0001f1f5\U0001f1fe|\U0001f1f5\U0001f1fc|\U0001f1f5\U0001f1f9|\U0001f1f5\U0001f1f8|\U0001f1f5\U0001f1f7|\U0001f1f5\U0001f1f3|\U0001f1f5\U0001f1f2|\U0001f1f5\U0001f1f1|\U0001f1f5\U0001f1f0|\U0001f1f5\U0001f1ed|\U0001f1f5\U0001f1ec|\U0001f1f5\U0001f1eb|\U0001f1f5\U0001f1ea|\U0001f1f5\U0001f1e6|\U0001f1f4\U0001f1f2|\U0001f1f3\U0001f1ff|\U0001f1f3\U0001f1fa|\U0001f1f3\U0001f1f7|\U0001f1f3\U0001f1f5|\U0001f1f3\U0001f1f4|\U0001f1f3\U0001f1f1|\U0001f1f3\U0001f1ee|\U0001f1f3\U0001f1ec|\U0001f1f3\U0001f1eb|\U0001f1f3\U0001f1ea|\U0001f1f3\U0001f1e8|\U0001f1f3\U0001f1e6|\U0001f1f2\U0001f1ff|\U0001f1f2\U0001f1fe|\U0001f1f2\U0001f1fd|\U0001f1f2\U0001f1fc|\U0001f1f2\U0001f1fb|\U0001f1f2\U0001f1fa|\U0001f1f2\U0001f1f9|\U0001f1f2\U0001f1f8|\U0001f1f2\U0001f1f7|\U0001f1f2\U0001f1f6|\U0001f1f2\U0001f1f5|\U0001f1f2\U0001f1f4|\U0001f1f2\U0001f1f3|\U0001f1f2\U0001f1f2|\U0001f1f2\U0001f1f1|\U0001f1f2\U0001f1f0|\U0001f1f2\U0001f1ed|\U0001f1f2\U0001f1ec|\U0001f1f2\U0001f1eb|\U0001f1f2\U0001f1ea|\U0001f1f2\U0001f1e9|\U0001f1f2\U0001f1e8|\U0001f1f2\U0001f1e6|\U0001f1f1\U0001f1fe|\U0001f1f1\U0001f1fb|\U0001f1f1\U0001f1fa|\U0001f1f1\U0001f1f9|\U0001f1f1\U0001f1f8|\U0001f1f1\U0001f1f7|\U0001f1f1\U0001f1f0|\U0001f1f1\U0001f1ee|\U0001f1f1\U0001f1e8|\U0001f1f1\U0001f1e7|\U0001f1f1\U0001f1e6|\U0001f1f0\U0001f1ff|\U0001f1f0\U0001f1fe|\U0001f1f0\U0001f1fc|\U0001f1f0\U0001f1f7|\U0001f1f0\U0001f1f5|\U0001f1f0\U0001f1f3|\U0001f1f0\U0001f1f2|\U0001f1f0\U0001f1ee|\U0001f1f0\U0001f1ed|\U0001f1f0\U0001f1ec|\U0001f1f0\U0001f1ea|\U0001f1ef\U0001f1f5|\U0001f1ef\U0001f1f4|\U0001f1ef\U0001f1f2|\U0001f1ef\U0001f1ea|\U0001f1ee\U0001f1f9|\U0001f1ee\U0001f1f8|\U0001f1ee\U0001f1f7|\U0001f1ee\U0001f1f6|\U0001f1ee\U0001f1f4|\U0001f1ee\U0001f1f3|\U0001f1ee\U0001f1f2|\U0001f1ee\U0001f1f1|\U0001f1ee\U0001f1ea|\U0001f1ee\U0001f1e9|\U0001f1ee\U0001f1e8|\U0001f1ed\U0001f1fa|\U0001f1ed\U0001f1f9|\U0001f1ed\U0001f1f7|\U0001f1ed\U0001f1f3|\U0001f1ed\U0001f1f2|\U0001f1ed\U0001f1f0|\U0001f1ec\U0001f1fe|\U0001f1ec\U0001f1fc|\U0001f1ec\U0001f1fa|\U0001f1ec\U0001f1f9|\U0001f1ec\U0001f1f8|\U0001f1ec\U0001f1f7|\U0001f1ec\U0001f1f6|\U0001f1ec\U0001f1f5|\U0001f1ec\U0001f1f3|\U0001f1ec\U0001f1f2|\U0001f1ec\U0001f1f1|\U0001f1ec\U0001f1ee|\U0001f1ec\U0001f1ed|\U0001f1ec\U0001f1ec|\U0001f1ec\U0001f1eb|\U0001f1ec\U0001f1ea|\U0001f1ec\U0001f1e9|\U0001f1ec\U0001f1e7|\U0001f1ec\U0001f1e6|\U0001f1eb\U0001f1f7|\U0001f1eb\U0001f1f4|\U0001f1eb\U0001f1f2|\U0001f1eb\U0001f1f0|\U0001f1eb\U0001f1ef|\U0001f1eb\U0001f1ee|\U0001f1ea\U0001f1fa|\U0001f1ea\U0001f1f9|\U0001f1ea\U0001f1f8|\U0001f1ea\U0001f1f7|\U0001f1ea\U0001f1ed|\U0001f1ea\U0001f1ec|\U0001f1ea\U0001f1ea|\U0001f1ea\U0001f1e8|\U0001f1ea\U0001f1e6|\U0001f1e9\U0001f1ff|\U0001f1e9\U0001f1f4|\U0001f1e9\U0001f1f2|\U0001f1e9\U0001f1f0|\U0001f1e9\U0001f1ef|\U0001f1e9\U0001f1ec|\U0001f1e9\U0001f1ea|\U0001f1e8\U0001f1ff|\U0001f1e8\U0001f1fe|\U0001f1e8\U0001f1fd|\U0001f1e8\U0001f1fc|\U0001f1e8\U0001f1fb|\U0001f1e8\U0001f1fa|\U0001f1e8\U0001f1f7|\U0001f1e8\U0001f1f5|\U0001f1e8\U0001f1f4|\U0001f1e8\U0001f1f3|\U0001f1e8\U0001f1f2|\U0001f1e8\U0001f1f1|\U0001f1e8\U0001f1f0|\U0001f1e8\U0001f1ee|\U0001f1e8\U0001f1ed|\U0001f1e8\U0001f1ec|\U0001f1e8\U0001f1eb|\U0001f1e8\U0001f1e9|\U0001f1e8\U0001f1e8|\U0001f1e8\U0001f1e6|\U0001f1e7\U0001f1ff|\U0001f1e7\U0001f1fe|\U0001f1e7\U0001f1fc|\U0001f1e7\U0001f1fb|\U0001f1e7\U0001f1f9|\U0001f1e7\U0001f1f8|\U0001f1e7\U0001f1f7|\U0001f1e7\U0001f1f6|\U0001f1e7\U0001f1f4|\U0001f1e7\U0001f1f3|\U0001f1e7\U0001f1f2|\U0001f1e7\U0001f1f1|\U0001f1e7\U0001f1ef|\U0001f1e7\U0001f1ee|\U0001f1e7\U0001f1ed|\U0001f1e7\U0001f1ec|\U0001f1e7\U0001f1eb|\U0001f1e7\U0001f1ea|\U0001f1e7\U0001f1e9|\U0001f1e7\U0001f1e7|\U0001f1e7\U0001f1e6|\U0001f1e6\U0001f1ff|\U0001f1e6\U0001f1fd|\U0001f1e6\U0001f1fc|\U0001f1e6\U0001f1fa|\U0001f1e6\U0001f1f9|\U0001f1e6\U0001f1f8|\U0001f1e6\U0001f1f7|\U0001f1e6\U0001f1f6|\U0001f1e6\U0001f1f4|\U0001f1e6\U0001f1f2|\U0001f1e6\U0001f1f1|\U0001f1e6\U0001f1ee|\U0001f1e6\U0001f1ec|\U0001f1e6\U0001f1eb|\U0001f1e6\U0001f1ea|\U0001f1e6\U0001f1e9|\U0001f1e6\U0001f1e8|\U0001f3f4|\U0001f38c|\U0001f6a9|\U0001f3c1|\U0001f535|\U0001f534|\u26ab|\u26aa|\U0001f533|\U0001f532|\U0001f518|\U0001f4a0|\U0001f53b|\U0001f53a|\U0001f539|\U0001f538|\U0001f537|\U0001f536|\u2b1c|\u2b1b|\u25fe|\u25fd|\U0001f235|\U0001f23a|\U0001f233|\U0001f234|\U0001f238|\U0001f251|\U0001f232|\U0001f21a|\U0001f239|\U0001f250|\U0001f22f|\U0001f236|\U0001f201|\U0001f19a|\U0001f199|\U0001f198|\U0001f197|\U0001f196|\U0001f195|\U0001f194|\U0001f193|\U0001f192|\U0001f191|\U0001f18e|\U0001f524|\U0001f523|\U0001f522|\U0001f521|\U0001f520|\U0001f4af|\U0001f51f|\u2757|\u2755|\u2754|\u2753|\u27bf|\u27b0|\u2797|\u2796|\u2795|\u274e|\u274c|\u2705|\u2b55|\U0001f531|\U0001f530|\U0001f4db|\U0001f4f4|\U0001f4f3|\U0001f4f6|\U0001f506|\U0001f505|\U0001f3a6|\u23ec|\U0001f53d|\u23eb|\U0001f53c|\u23ea|\u23e9|\U0001f502|\U0001f501|\U0001f500|\u26ce|\u2653|\u2652|\u2651|\u2650|\u264f|\u264e|\u264d|\u264c|\u264b|\u264a|\u2649|\u2648|\U0001f52f|\U0001f54e|\U0001f6d0|\U0001f51d|\U0001f51c|\U0001f51b|\U0001f51a|\U0001f519|\U0001f504|\U0001f503|\U0001f51e|\U0001f4f5|\U0001f6b7|\U0001f6b1|\U0001f6af|\U0001f6ad|\U0001f6b3|\U0001f6ab|\u26d4|\U0001f6b8|\U0001f6c5|\U0001f6c4|\U0001f6c3|\U0001f6c2|\U0001f6be|\U0001f6bc|\U0001f6bb|\U0001f6ba|\U0001f6b9|\u267f|\U0001f6b0|\U0001f6ae|\U0001f3e7|\U0001f6d2|\U0001f52e|\U0001f5ff|\U0001f6ac|\U0001f48a|\U0001f489|\U0001f517|\U0001f529|\U0001f527|\U0001f3f9|\U0001f52b|\U0001f528|\U0001f511|\U0001f510|\U0001f50f|\U0001f513|\U0001f512|\U0001f4d0|\U0001f4cf|\U0001f4ce|\U0001f4cd|\U0001f4cc|\U0001f4cb|\U0001f4ca|\U0001f4c9|\U0001f4c8|\U0001f4c7|\U0001f4c6|\U0001f4c5|\U0001f4c2|\U0001f4c1|\U0001f4bc|\U0001f4dd|\U0001f4ee|\U0001f4ed|\U0001f4ec|\U0001f4ea|\U0001f4eb|\U0001f4e6|\U0001f4e5|\U0001f4e4|\U0001f4e9|\U0001f4e8|\U0001f4e7|\U0001f4b2|\U0001f4b1|\U0001f4b9|\U0001f4b3|\U0001f4b8|\U0001f4b7|\U0001f4b6|\U0001f4b5|\U0001f4b4|\U0001f4b0|\U0001f516|\U0001f4d1|\U0001f4f0|\U0001f4c4|\U0001f4dc|\U0001f4c3|\U0001f4d2|\U0001f4d3|\U0001f4da|\U0001f4d9|\U0001f4d8|\U0001f4d7|\U0001f4d6|\U0001f4d5|\U0001f4d4|\U0001f3ee|\U0001f526|\U0001f4a1|\U0001f4e1|\U0001f52d|\U0001f52c|\U0001f50e|\U0001f50d|\U0001f4fc|\U0001f4f9|\U0001f4f8|\U0001f4f7|\U0001f4fa|\U0001f3ac|\U0001f3a5|\U0001f4c0|\U0001f4bf|\U0001f4be|\U0001f4bd|\U0001f4bb|\U0001f50c|\U0001f50b|\U0001f4e0|\U0001f4df|\U0001f4de|\U0001f4f2|\U0001f4f1|\U0001f941|\U0001f3bb|\U0001f3ba|\U0001f3b9|\U0001f3b8|\U0001f3b7|\U0001f4fb|\U0001f3a7|\U0001f3a4|\U0001f3b6|\U0001f3b5|\U0001f3bc|\U0001f515|\U0001f514|\U0001f4ef|\U0001f4e3|\U0001f4e2|\U0001f50a|\U0001f509|\U0001f508|\U0001f507|\U0001f3b4|\U0001f004|\U0001f0cf|\U0001f3b2|\U0001f3ae|\U0001f3bf|\U0001f3bd|\U0001f3a3|\u26f3|\U0001f3af|\U0001f945|\U0001f94b|\U0001f94a|\U0001f3f8|\U0001f3d3|\U0001f3d2|\U0001f3d1|\U0001f3cf|\U0001f3b3|\U0001f3b1|\U0001f3be|\U0001f3c9|\U0001f3c8|\U0001f3d0|\U0001f3c0|\u26be|\u26bd|\U0001f949|\U0001f948|\U0001f947|\U0001f3c5|\U0001f3c6|\U0001f3ab|\U0001f381|\U0001f380|\U0001f391|\U0001f390|\U0001f38f|\U0001f38e|\U0001f38d|\U0001f38b|\U0001f38a|\U0001f389|\U0001f388|\u2728|\U0001f387|\U0001f386|\U0001f384|\U0001f383|\U0001f30a|\U0001f4a7|\U0001f525|\u26c4|\u26a1|\u2614|\U0001f302|\U0001f308|\U0001f300|\u26c5|\U0001f320|\U0001f31f|\u2b50|\U0001f31e|\U0001f31d|\U0001f31c|\U0001f31b|\U0001f31a|\U0001f319|\U0001f318|\U0001f317|\U0001f316|\U0001f315|\U0001f314|\U0001f313|\U0001f312|\U0001f311|\U0001f566|\U0001f55a|\U0001f565|\U0001f559|\U0001f564|\U0001f558|\U0001f563|\U0001f557|\U0001f562|\U0001f556|\U0001f561|\U0001f555|\U0001f560|\U0001f554|\U0001f55f|\U0001f553|\U0001f55e|\U0001f552|\U0001f55d|\U0001f551|\U0001f55c|\U0001f550|\U0001f567|\U0001f55b|\u23f0|\u231a|\u23f3|\u231b|\U0001f6c1|\U0001f6c0|\U0001f6bf|\U0001f6bd|\U0001f6cc|\U0001f6aa|\U0001f680|\U0001f6a1|\U0001f6a0|\U0001f69f|\U0001f681|\U0001f4ba|\U0001f6ec|\U0001f6eb|\U0001f6a2|\U0001f6a4|\U0001f6f6|\u26f5|\u2693|\U0001f6d1|\U0001f6a7|\U0001f6a6|\U0001f6a5|\U0001f6a8|\u26fd|\U0001f68f|\U0001f6f5|\U0001f6f4|\U0001f6b2|\U0001f69c|\U0001f69b|\U0001f69a|\U0001f699|\U0001f698|\U0001f697|\U0001f696|\U0001f695|\U0001f694|\U0001f693|\U0001f692|\U0001f691|\U0001f690|\U0001f68e|\U0001f68d|\U0001f68c|\U0001f68b|\U0001f69e|\U0001f69d|\U0001f68a|\U0001f689|\U0001f688|\U0001f687|\U0001f686|\U0001f685|\U0001f684|\U0001f683|\U0001f682|\U0001f3b0|\U0001f3a8|\U0001f3ad|\U0001f3aa|\U0001f488|\U0001f3a2|\U0001f3a1|\U0001f3a0|\U0001f30c|\U0001f309|\U0001f307|\U0001f306|\U0001f305|\U0001f304|\U0001f303|\U0001f301|\u26fa|\u26f2|\U0001f54b|\U0001f54d|\U0001f54c|\u26ea|\U0001f5fd|\U0001f5fc|\U0001f492|\U0001f3f0|\U0001f3ef|\U0001f3ed|\U0001f3ec|\U0001f3eb|\U0001f3ea|\U0001f3e9|\U0001f3e8|\U0001f3e6|\U0001f3e5|\U0001f3e4|\U0001f3e3|\U0001f3e2|\U0001f3e1|\U0001f3e0|\U0001f5fb|\U0001f30b|\U0001f5fe|\U0001f310|\U0001f30f|\U0001f30e|\U0001f30d|\U0001f3fa|\U0001f52a|\U0001f944|\U0001f374|\U0001f943|\U0001f942|\U0001f37b|\U0001f37a|\U0001f379|\U0001f378|\U0001f377|\U0001f37e|\U0001f376|\U0001f375|\u2615|\U0001f95b|\U0001f37c|\U0001f36f|\U0001f36e|\U0001f36d|\U0001f36c|\U0001f36b|\U0001f370|\U0001f382|\U0001f36a|\U0001f369|\U0001f368|\U0001f367|\U0001f366|\U0001f361|\U0001f365|\U0001f364|\U0001f363|\U0001f362|\U0001f360|\U0001f35d|\U0001f35c|\U0001f35b|\U0001f35a|\U0001f359|\U0001f358|\U0001f371|\U0001f37f|\U0001f957|\U0001f372|\U0001f958|\U0001f373|\U0001f95a|\U0001f959|\U0001f32f|\U0001f32e|\U0001f32d|\U0001f355|\U0001f35f|\U0001f354|\U0001f953|\U0001f357|\U0001f356|\U0001f9c0|\U0001f95e|\U0001f956|\U0001f950|\U0001f35e|\U0001f330|\U0001f95c|\U0001f344|\U0001f952|\U0001f33d|\U0001f955|\U0001f954|\U0001f346|\U0001f951|\U0001f345|\U0001f95d|\U0001f353|\U0001f352|\U0001f351|\U0001f350|\U0001f34f|\U0001f34e|\U0001f34d|\U0001f34c|\U0001f34b|\U0001f34a|\U0001f349|\U0001f348|\U0001f347|\U0001f343|\U0001f342|\U0001f341|\U0001f340|\U0001f33f|\U0001f33e|\U0001f335|\U0001f334|\U0001f333|\U0001f332|\U0001f331|\U0001f337|\U0001f33c|\U0001f33b|\U0001f33a|\U0001f940|\U0001f339|\U0001f4ae|\U0001f338|\U0001f490|\U0001f982|\U0001f41e|\U0001f41d|\U0001f41c|\U0001f41b|\U0001f40c|\U0001f98b|\U0001f991|\U0001f990|\U0001f980|\U0001f41a|\U0001f419|\U0001f988|\U0001f421|\U0001f420|\U0001f41f|\U0001f42c|\U0001f40b|\U0001f433|\U0001f409|\U0001f432|\U0001f40d|\U0001f98e|\U0001f422|\U0001f40a|\U0001f438|\U0001f989|\U0001f986|\U0001f985|\U0001f427|\U0001f426|\U0001f425|\U0001f424|\U0001f423|\U0001f413|\U0001f414|\U0001f983|\U0001f43e|\U0001f43c|\U0001f428|\U0001f43b|\U0001f987|\U0001f407|\U0001f430|\U0001f439|\U0001f400|\U0001f401|\U0001f42d|\U0001f98f|\U0001f418|\U0001f42b|\U0001f42a|\U0001f410|\U0001f411|\U0001f40f|\U0001f43d|\U0001f417|\U0001f416|\U0001f437|\U0001f404|\U0001f403|\U0001f402|\U0001f42e|\U0001f984|\U0001f98c|\U0001f40e|\U0001f434|\U0001f406|\U0001f405|\U0001f42f|\U0001f981|\U0001f408|\U0001f431|\U0001f98a|\U0001f43a|\U0001f429|\U0001f415|\U0001f436|\U0001f98d|\U0001f412|\U0001f435|\U0001f48e|\U0001f48d|\U0001f484|\U0001f4ff|\U0001f393|\U0001f3a9|\U0001f452|\U0001f451|\U0001f462|\U0001f461|\U0001f460|\U0001f45f|\U0001f45e|\U0001f392|\U0001f45d|\U0001f45c|\U0001f45b|\U0001f45a|\U0001f459|\U0001f458|\U0001f457|\U0001f456|\U0001f455|\U0001f454|\U0001f453|\U0001f4ad|\U0001f4ac|\U0001f4ab|\U0001f4a8|\U0001f4a6|\U0001f4a5|\U0001f4a3|\U0001f4a2|\U0001f4a4|\U0001f48c|\U0001f49f|\U0001f49e|\U0001f49d|\U0001f5a4|\U0001f49c|\U0001f49b|\U0001f49a|\U0001f499|\U0001f497|\U0001f496|\U0001f495|\U0001f494|\U0001f493|\U0001f498|\U0001f48b|\U0001f444|\U0001f445|\U0001f440|\U0001f463|\U0001f443|\U0001f442|\U0001f485|\U0001f91d|\U0001f64f|\U0001f64c|\U0001f450|\U0001f44f|\U0001f44b|\U0001f91a|\U0001f91c|\U0001f91b|\U0001f44a|\u270a|\U0001f44e|\U0001f44d|\U0001f44c|\u270b|\U0001f919|\U0001f918|\U0001f596|\U0001f91e|\U0001f447|\U0001f595|\U0001f446|\U0001f449|\U0001f448|\U0001f933|\U0001f4aa|\U0001f46a|\U0001f491|\U0001f48f|\U0001f46d|\U0001f46c|\U0001f46b|\U0001f939|\U0001f93e|\U0001f93d|\U0001f93c|\U0001f938|\U0001f6b5|\U0001f6b4|\U0001f3ca|\U0001f6a3|\U0001f3c4|\U0001f3c2|\U0001f3c7|\U0001f93a|\U0001f465|\U0001f464|\U0001f46f|\U0001f57a|\U0001f483|\U0001f3c3|\U0001f6b6|\U0001f487|\U0001f486|\U0001f937|\U0001f926|\U0001f647|\U0001f64b|\U0001f481|\U0001f646|\U0001f645|\U0001f64e|\U0001f64d|\U0001f472|\U0001f930|\U0001f935|\U0001f470|\U0001f934|\U0001f478|\U0001f936|\U0001f385|\U0001f471|\U0001f473|\U0001f477|\U0001f482|\U0001f46e|\U0001f47c|\U0001f476|\U0001f475|\U0001f474|\U0001f469|\U0001f468|\U0001f467|\U0001f466|\U0001f64a|\U0001f649|\U0001f648|\U0001f63e|\U0001f63f|\U0001f640|\U0001f63d|\U0001f63c|\U0001f63b|\U0001f639|\U0001f638|\U0001f63a|\U0001f4a9|\U0001f916|\U0001f47e|\U0001f47d|\U0001f47b|\U0001f480|\U0001f47a|\U0001f479|\U0001f47f|\U0001f608|\U0001f927|\U0001f922|\U0001f915|\U0001f912|\U0001f637|\U0001f925|\U0001f921|\U0001f920|\U0001f607|\U0001f620|\U0001f621|\U0001f635|\U0001f633|\U0001f631|\U0001f630|\U0001f62c|\U0001f629|\U0001f628|\U0001f627|\U0001f626|\U0001f62d|\U0001f622|\U0001f624|\U0001f61f|\U0001f61e|\U0001f616|\U0001f641|\U0001f632|\U0001f911|\U0001f643|\U0001f615|\U0001f614|\U0001f613|\U0001f612|\U0001f924|\U0001f61d|\U0001f61c|\U0001f61b|\U0001f913|\U0001f60c|\U0001f634|\U0001f62b|\U0001f62a|\U0001f62f|\U0001f910|\U0001f62e|\U0001f625|\U0001f623|\U0001f60f|\U0001f644|\U0001f636|\U0001f611|\U0001f610|\U0001f914|\U0001f917|\U0001f642|\U0001f61a|\U0001f619|\U0001f617|\U0001f618|\U0001f60d|\U0001f60e|\U0001f60b|\U0001f60a|\U0001f609|\U0001f606|\U0001f605|\U0001f604|\U0001f603|\U0001f923|\U0001f602|\U0001f601|\U0001f600|\U0001f3f3|\u25fc|\u25fb|\u25ab|\u25aa|\u3299|\u3297|\U0001f237|\U0001f202|\U0001f17f|\U0001f17e|\u24c2|\u2139|\U0001f171|\U0001f170|9\u20e3|8\u20e3|7\u20e3|6\u20e3|5\u20e3|4\u20e3|3\u20e3|2\u20e3|1\u20e3|0\u20e3|#\u20e3|\u2122|\xae|\xa9|\u3030|\u2049|\u203c|\u2747|\u2734|\u2733|\u303d|\u2695|\u2642|\u2640|\u2716|\u2714|\u2611|\u269c|\u267b|\u23cf|\u23fa|\u23f9|\u23f8|\u23ee|\u25c0|\u23ef|\u23ed|\u25b6|\u262e|\u262a|\u2626|\u271d|\u262f|\u2638|\u2721|\U0001f549|\u269b|\u2935|\u2934|\u21aa|\u21a9|\u2194|\u2195|\u2196|\u2b05|\u2199|\u2b07|\u2198|\u27a1|\u2197|\u2b06|\u2623|\u2622|\u26a0|\U0001f6e2|\u26b1|\u26b0|\u26d3|\u2696|\u2697|\U0001f5dc|\u2699|\U0001f6e1|\u2694|\U0001f5e1|\U0001f6e0|\u2692|\u26cf|\U0001f5dd|\U0001f5d1|\U0001f5c4|\U0001f5c3|\u2702|\U0001f587|\U0001f5d3|\U0001f5d2|\U0001f5c2|\U0001f58d|\U0001f58c|\U0001f58a|\U0001f58b|\u2712|\u270f|\U0001f5f3|\u2709|\U0001f3f7|\U0001f5de|\U0001f56f|\U0001f4fd|\U0001f39e|\U0001f5b2|\U0001f5b1|\u2328|\U0001f5a8|\U0001f5a5|\u260e|\U0001f39b|\U0001f39a|\U0001f399|\u2663|\u2666|\u2665|\u2660|\U0001f579|\u26f8|\U0001f396|\U0001f39f|\U0001f397|\u2604|\u2603|\u2744|\u26f1|\u2602|\U0001f32c|\U0001f32b|\U0001f32a|\U0001f329|\U0001f328|\U0001f327|\U0001f326|\U0001f325|\U0001f324|\u26c8|\u2601|\u2600|\U0001f321|\U0001f570|\u23f2|\u23f1|\U0001f6cb|\U0001f6cf|\U0001f6ce|\U0001f6f0|\U0001f6e9|\u2708|\U0001f6e5|\u26f4|\U0001f6f3|\U0001f6e4|\U0001f6e3|\U0001f5bc|\u2668|\u26e9|\U0001f3da|\U0001f3d9|\U0001f3d8|\U0001f3d7|\U0001f3db|\U0001f3df|\U0001f3de|\U0001f3dd|\U0001f3dc|\U0001f3d6|\U0001f3d5|\u26f0|\U0001f3d4|\U0001f5fa|\U0001f37d|\U0001f336|\u2618|\U0001f3f5|\U0001f578|\U0001f577|\U0001f54a|\U0001f43f|\u26d1|\U0001f6cd|\U0001f576|\U0001f573|\U0001f5ef|\U0001f5e8|\u2763|\u2764|\U0001f441|\u270d|\U0001f590|\u270c|\u261d|\U0001f3cd|\U0001f3ce|\U0001f3cb|\u26f9|\U0001f3cc|\u26f7|\U0001f5e3|\U0001f574|\U0001f575|\u2620|\u2639|\u263a'
    ,
    # HTML tags:
    r"""<[^>\s]+>"""
    ,
    # ASCII Arrows
    r"""[\-]+>|<[\-]+"""
    ,
    # Twitter username:
    r"""(?:@[\w_]+)"""
    ,
    # Twitter hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,
    # email addresses
    r"""[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]"""
    ,
    # Remaining word types:
    r"""
    
    (?:[^\W\d_](?:[^\W\d_]|['\-_])+[^\W\d_]) # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots.
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
    )

######################################################################
# This is the core tokenizing regex:

WORD_RE = re.compile(r"""(%s)""" % "|".join(REGEXPS), re.VERBOSE | re.I
                     | re.UNICODE)

# WORD_RE performs poorly on these patterns:
HANG_RE = re.compile(r'([^a-zA-Z0-9])\1{3,}')

# The emoticon string gets its own regex so that we can preserve case for
# them as needed:
EMOTICON_RE = re.compile(EMOTICONS, re.VERBOSE | re.I | re.UNICODE)

# These are for regularizing HTML entities to Unicode:
ENT_RE = re.compile(r'&(#?(x?))([^&;\s]+);')


######################################################################
# Functions for converting html entities
######################################################################

def _str_to_unicode(text, encoding=None, errors='strict'):
    if encoding is None:
        encoding = 'utf-8'
    if isinstance(text, bytes):
        return text.decode(encoding, errors)
    return text

def _replace_html_entities(text, keep=(), remove_illegal=True, encoding='utf-8'):
    """
    Remove entities from text by converting them to their
    corresponding unicode character.

    :param text: a unicode string or a byte string encoded in the given
    `encoding` (which defaults to 'utf-8').

    :param list keep:  list of entity names which should not be replaced.\
    This supports both numeric entities (``&#nnnn;`` and ``&#hhhh;``)
    and named entities (such as ``&nbsp;`` or ``&gt;``).

    :param bool remove_illegal: If `True`, entities that can't be converted are\
    removed. Otherwise, entities that can't be converted are kept "as
    is".

    :returns: A unicode string with the entities removed.

    See https://github.com/scrapy/w3lib/blob/master/w3lib/html.py

        >>> from nltk.tokenize.casual import _replace_html_entities
        >>> _replace_html_entities(b'Price: &pound;100')
        'Price: \\xa3100'
        >>> print(_replace_html_entities(b'Price: &pound;100'))
        Price: £100
        >>>
    """

    def _convert_entity(match):
        entity_body = match.group(3)
        if match.group(1):
            try:
                if match.group(2):
                    number = int(entity_body, 16)
                else:
                    number = int(entity_body, 10)
                # Numeric character references in the 80-9F range are typically
                # interpreted by browsers as representing the characters mapped
                # to bytes 80-9F in the Windows-1252 encoding. For more info
                # see: http://en.wikipedia.org/wiki/Character_encodings_in_HTML
                if 0x80 <= number <= 0x9f:
                    return int2byte(number).decode('cp1252')
            except ValueError:
                number = None
        else:
            if entity_body in keep:
                return match.group(0)
            else:
                number = htmlentitydefs.name2codepoint.get(entity_body)
        if number is not None:
            try:
                return unichr(number)
            except ValueError:
                pass

        return "" if remove_illegal else match.group(0)

    return ENT_RE.sub(_convert_entity, _str_to_unicode(text, encoding))


######################################################################


class TweetTokenizer:
    r"""
    Tokenizer for tweets.
    """

    def __init__(self, preserve_case=True, reduce_len=False, strip_handles=False, strip_hashtags=False, strip_links=False, strip_RT=False):
        self.preserve_case = preserve_case
        self.reduce_len = reduce_len
        self.strip_handles = strip_handles
        self.strip_hashtags = strip_hashtags
        self.strip_links = strip_links
        self.strip_RT = strip_RT

    def tokenize(self, text):
        """
        :param text: str
        :rtype: list(str)
        :return: a tokenized list of strings; concatenating this list returns\
        the original string if `preserve_case=False`
        """
        # Fix HTML character entities:
        text = _replace_html_entities(text)

        # Remove variation filter skins.
        var = re.compile("["
          u"\U0001F3FB-\U0001F3FF"
          "]+", flags=re.UNICODE)
        text = var.sub('', text)

        # Remove username handles
        if self.strip_handles:
            text = remove_handles(text)
        # Remove hashtags
        if self.strip_hashtags:
            text = remove_hashtags(text)
        # Remove links
        if self.strip_links:
            text = remove_links(text)
        # Remove RT tag
        if self.strip_RT:
            text = remove_RT(text)
        # Normalize word lengthening
        if self.reduce_len:
            text = reduce_lengthening(text)


        # Shorten problematic sequences of characters
        safe_text = HANG_RE.sub(r'\1\1\1', text)
        # Tokenize:
        words = WORD_RE.findall(safe_text)
        # Possibly alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:
            words = list(map((lambda x : x if EMOTICON_RE.search(x) else
                              x.lower()), words))
        return words

class RedditTokenizer:
    r"""
    Tokenizer for Reddit.
    """

    def __init__(self, preserve_case=True, reduce_len=False, strip_links=True):
        self.preserve_case = preserve_case
        self.reduce_len = reduce_len
        self.strip_links = strip_links

    def tokenize(self, text):
        """
        :param text: str
        :rtype: list(str)
        :return: a tokenized list of strings; concatenating this list returns\
        the original string if `preserve_case=False`
        """
        # Fix HTML character entities:
        text = _replace_html_entities(text)

        # Remove variation filter skins.
        var = re.compile("["
          u"\U0001F3FB-\U0001F3FF"
          "]+", flags=re.UNICODE)
        text = var.sub('', text)

        # Remove links
        if self.strip_links:
            text = remove_links(text)
        # Normalize word lengthening
        if self.reduce_len:
            text = reduce_lengthening(text)


        # Shorten problematic sequences of characters
        safe_text = HANG_RE.sub(r'\1\1\1', text)
        # Tokenize:
        words = WORD_RE.findall(safe_text)
        # Possibly alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:
            words = list(map((lambda x : x if EMOTICON_RE.search(x) else
                              x.lower()), words))
        return words


######################################################################
# Normalization Functions
######################################################################

def reduce_lengthening(text):
    """
    Replace repeated character sequences of length 3 or greater with sequences
    of length 3.
    """
    pattern = re.compile(r"(.)\1{2,}")
    return pattern.sub(r"\1\1\1", text)


def remove_handles(text):
    """
    Remove Twitter username handles from text.
    """
    pattern = re.compile(r"(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){20}(?!@))|(?<![A-Za-z0-9_!@#\$%&*])@(([A-Za-z0-9_]){1,19})(?![A-Za-z0-9_]*@)")
    # Substitute hadnles with ' ' to ensure that text on either side of removed handles are tokenized correctly
    return pattern.sub(' ', text)

def remove_hashtags(text):
    """
    Remove Twitter hashtags from text.
    """
    pattern = re.compile(r"(?<![A-Za-z0-9_!@#\$%&*])#(([A-Za-z0-9_]){140}(?!@))|(?<![A-Za-z0-9_!@#\$%&*])#(([A-Za-z0-9_]){1,140})(?![A-Za-z0-9_]*@)")
    # Substitute hadnles with ' ' to ensure that text on either side of removed hashtags are tokenized correctly
    return pattern.sub(' ', text)

def remove_links(text):
    """
    Remove Links from Tweets
    """
    return re.sub(r"http\S+", "", text)

def remove_RT(text):
    """ Remove the RT tag from tweets """
    return re.sub("RT", "", text)

    



######################################################################
# Tokenization Function
######################################################################



def casual_tokenize(text, preserve_case=True, reduce_len=False, strip_handles=False, strip_hashtags=False, strip_links=False, strip_RT=True):
    """
    Convenience function for wrapping the tokenizer.
    """
    return TweetTokenizer(preserve_case=preserve_case, reduce_len=reduce_len,
                          strip_handles=strip_handles, strip_hashtags=strip_hashtags,
                          strip_links=strip_links, strip_RT=strip_RT).tokenize(text)


