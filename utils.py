import pandas as pd
import numpy as np
import os
import pickle
from scipy.spatial.distance import cosine
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# encoding=utf8
from spacy.en import English
import config

parser = English()


def read_csv_with_tweets(filename, regenerate=False):
    if regenerate or not os.path.isfile(os.path.join(config.data_folder, config.model_file)):
        # check if file exist
        if os.path.isfile(os.path.join(config.data_folder, config.tweets_filename)):
            df_storage = iterate_over_csv_and_put_into_storage(pd.read_csv(filename)[['text']])
            pickle.dump(df_storage, open(os.path.join(config.data_folder, config.model_file), 'wb'), protocol=2)
        else:
            raise('Twitter file doesnt exist!')
    else:
        df_storage = pickle.load(open(os.path.join(config.data_folder, config.model_file), 'rb'))
    return df_storage


def transform_tweet(tweet):
    parsedEx = parser(tweet)
    #TODO: remove stop words
    out_vector = parsedEx.vector
    entities = list(parsedEx.ents)
    output = [((entity.text, entity.label_, out_vector)) for entity in entities]
    # TODO: kick out entities that are useless e.g. DATE
    return output


def put_gt_tweet_in_storage(tweet, df):
    for entity, entity_type, vector_array in transform_tweet(tweet):
        df = pd.concat([df, pd.DataFrame([{'Entity': entity, 'Entity type': entity_type, 'Vector array':vector_array}])], axis=0)
    return df


def compare_tweet_with_storage(tweet, storage):
    transformed_tweet = transform_tweet(tweet)
    scores = {}
    for i, (entity, entity_type, vector_array) in enumerate(transformed_tweet):
        temp_score = 0
        for j, (_, item) in enumerate(storage[storage['Entity'] == entity].iterrows()):
            # similarity
            temp_score = np.max([1 - cosine(vector_array, item['Vector array']), temp_score])
            print(1 - cosine(vector_array, item['Vector array']), entity, tweet, str(j))
        scores.update({entity: temp_score})
    return scores

def iterate_over_csv_and_put_into_storage(df_input):
    storage_df = pd.DataFrame(columns=['Entity', 'Entity type', 'Vector array'])
    for i, tweet in df_input.iterrows():
        print(i)
        storage_df = put_gt_tweet_in_storage(tweet['text'].decode(), storage_df)
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
