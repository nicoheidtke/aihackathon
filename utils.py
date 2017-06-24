# encoding=utf8
import pandas as pd
import numpy as np
import os
import pickle
from scipy.spatial.distance import cosine
import sys
from spacy.en import English
import preprocessor as twprep
twprep.set_options(twprep.OPT.URL, twprep.OPT.MENTION, twprep.OPT.RESERVED, twprep.OPT.SMILEY, twprep.OPT.EMOJI)

import config

reload(sys)
sys.setdefaultencoding('utf8')
parser = English()


def read_csv_with_tweets(filename, regenerate=False):
    if regenerate or not os.path.isfile(os.path.join(config.data_folder, config.model_file)):
        # check if file exist
        if os.path.isfile(os.path.join(config.data_folder, config.tweets_filename)):
            df_storage = iterate_over_csv_and_put_into_storage(pd.read_csv(filename, index_col='id')[['text']])
            pickle.dump(df_storage, open(os.path.join(config.data_folder, config.model_file), 'wb'), protocol=2)
        else:
            raise('Twitter file doesnt exist!')
    else:
        df_storage = pickle.load(open(os.path.join(config.data_folder, config.model_file), 'rb'))
    return df_storage

def transform_tweet(tweet):
    twprep.clean(tweet)
    parsedEx = parser(tweet)


    #TODO: remove stop words, handle, de-hashtag
    out_vector = parsedEx.vector
    entities = list(parsedEx.ents)
    output = [((entity.text, entity.label_, out_vector)) for entity in entities]
    # TODO: kick out entities that are useless e.g. DATE
    return output

def put_gt_tweet_in_storage(tweet, df, tweet_id=0):
    for entity, entity_type, vector_array in transform_tweet(tweet):
        df = pd.concat([df, pd.DataFrame([{'Entity': entity,
                                           'Entity type': entity_type,
                                           'Vector array':vector_array}], index=[tweet_id])], axis=0)
    return df

def combine_scores(scores_dict):
    return sorted(scores_dict.values())[::-1][0]

def compare_tweet_with_storage(tweet, storage=None):
    if storage is None:
        if not os.path.isfile(os.path.join(config.data_folder, config.model_file)):
            raise('Model was not found!')
        else:
            storage = pickle.load(open(os.path.join(config.data_folder, config.model_file), 'rb'))

    transformed_tweet = transform_tweet(tweet)
    scores = {}
    for i, (entity, entity_type, vector_array) in enumerate(transformed_tweet):
        temp_score = 0
        for j, (_, item) in enumerate(storage[storage['Entity'] == entity].iterrows()):
            temp_score = np.max([1 - cosine(vector_array, item['Vector array']), temp_score])
            print(1 - cosine(vector_array, item['Vector array']), entity, tweet, str(j))
        scores.update({entity: temp_score})
    return combine_scores(scores)

def iterate_over_csv_and_put_into_storage(df_input):
    storage_df = pd.DataFrame(columns=['Entity', 'Entity type', 'Vector array'])
    for i, (tweet_id, tweet) in enumerate(df_input.iterrows()):
        print(i, tweet_id)
        storage_df = put_gt_tweet_in_storage(tweet['text'].decode(), storage_df, tweet_id)
    return storage_df


if __name__ == '__main__':
    tweet_to_check = u"Donald Trump was murdered yesterday!"
    regenerate = False
    df_storage = read_csv_with_tweets(os.path.join(config.data_folder, config.tweets_filename), regenerate=regenerate)
    scores = compare_tweet_with_storage(tweet_to_check, df_storage)
    print(scores)


    # tweets = [u"Donald Trump was killed yesterday!",
    #           u"Donald Trump was not killed yesterday!"
    #           u"Donald Trump is gay",
    #           u"Donald Trump killed his wife!",
    #           u"Donald Trump launched a rocket and started a world war!"]
