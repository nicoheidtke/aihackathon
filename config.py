# encoding=utf8
import string
from nltk.corpus import stopwords
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS


data_folder = 'data'
tweets_filename = 'tweetz.csv'
model_file = 'model.pkl'


# A custom stoplist
STOPLIST = set(stopwords.words('english') + ["'s", "'m", "ca"] + list(ENGLISH_STOP_WORDS))
# List of symbols we don't care about
SYMBOLS = set([x for x in string.punctuation] + ["-----", "---", "...", "'ll", "'s", "’s", "’m"])