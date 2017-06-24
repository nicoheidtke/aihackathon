# encoding=utf8
import pandas as pd
import numpy as np
import os
import pickle
from scipy.spatial.distance import cosine
import sys
from spacy.en import English
import preprocessor as twprep
twprep.set_options(twprep.OPT.URL, twprep.OPT.HASHTAG, twprep.OPT.MENTION, twprep.OPT.RESERVED, twprep.OPT.SMILEY, twprep.OPT.EMOJI)
reload(sys)
import config
sys.setdefaultencoding('utf8')
parser = English()


def read_csv_with_tweets(filename, regenerate=False,  bow=False):
    if regenerate or not os.path.isfile(os.path.join(config.data_folder, config.model_file)):
        # check if file exist
        if os.path.isfile(os.path.join(config.data_folder, config.tweets_filename)):
            df_storage = iterate_over_csv_and_put_into_storage(pd.read_csv(filename, index_col='id')[['text']], bow)
            pickle.dump(df_storage, open(os.path.join(config.data_folder, config.model_file), 'wb'), protocol=2)
        else:
            raise('Twitter file doesnt exist!')
    else:
        df_storage = pickle.load(open(os.path.join(config.data_folder, config.model_file), 'rb'))
    return df_storage

def transform_tweet(tweet, bow=False):
    # tweet = twprep.clean(tweet)
    parsedEx = parser(tweet.decode()) # .decode()
    tokens = [token.text for token in parsedEx if token.text not in config.STOPLIST and token.text not in config.SYMBOLS]
    tweet = " ".join(tokens)
    parsedEx = parser(tweet.decode()) # .decode()
    print(parsedEx)
    #TODO: handle, de-hashtag
    out_vector = parsedEx.vector
    entities = list(parsedEx.ents)
    if bow: # actually it is a bag of clusters
        clust_dict = {}
        for token in parsedEx:
            cluster = token.cluster
            if cluster in clust_dict.keys():
                clust_dict[cluster] += 1
            else:
                clust_dict[cluster] = 1
        output = [((entity.text, entity.label_, clust_dict)) for entity in entities]
    else:
        output = [((entity.text, entity.label_, out_vector)) for entity in entities]
    # TODO: kick out entities that are useless e.g. DATE
    return output

def put_gt_tweet_in_storage(tweet, df, tweet_id=0, bow=False):
    for entity, entity_type, vector_array in transform_tweet(tweet, bow):
        df = pd.concat([df, pd.DataFrame([{'Entity': entity,
                                           'Entity type': entity_type,
                                           'Vector array':vector_array}], index=[tweet_id])], axis=0)
    return df

def combine_scores(scores_dict):
    if not len(scores_dict.values()):
        output = 0
    else:
        output = sorted(scores_dict.values())[::-1]
        nans = [ind for ind in np.where(np.isnan(output) ==1)]
        nn = []
        for nanid in nans:
            if nanid.shape[0]:
                nn.append(nanid[0])
        for nanindex in nn:
            del output[nanindex]
        if len(output):
            output = output[0]
        else:
            output = 0
    return output

def compare_tweet_with_storage(tweet, storage=None, bow=False):
    if storage is None:
        if not os.path.isfile(os.path.join(config.data_folder, config.model_file)):
            raise('Model was not found!')
        else:
            storage = pickle.load(open(os.path.join(config.data_folder, config.model_file), 'rb'))

    transformed_tweet = transform_tweet(tweet, bow)
    scores = {}
    for i, (entity, entity_type, vector_array) in enumerate(transformed_tweet):
        temp_score = 0
        for j, (tweetid, item) in enumerate(storage[storage['Entity'] == entity].iterrows()):
            if bow:
                clusterids = np.unique([vector_array.keys() + item['Vector array'].keys()])
                vector1 = np.zeros([len(clusterids)])
                vector2 = np.zeros([len(clusterids)])
                for k, cid in enumerate(clusterids):
                    vector1[k] = vector_array.get(cid, 0)
                    vector2[k] = item['Vector array'].get(cid, 0)
                temp_score = np.max([1.0 * np.sum(np.logical_and(vector1, vector2)) / np.min([np.sum(vector1), np.sum(vector2)]), temp_score])
            else:
                temp_score = np.max([1 - cosine(vector_array, item['Vector array']), temp_score])
                print(1 - cosine(vector_array, item['Vector array']), entity, tweet, str(tweetid))
        scores.update({entity: temp_score})
    return combine_scores(scores)

def iterate_over_csv_and_put_into_storage(df_input, bow=False):
    storage_df = pd.DataFrame(columns=['Entity', 'Entity type', 'Vector array'])
    for i, (tweet_id, tweet) in enumerate(df_input.iterrows()):
        print(i, tweet_id)
        try:
            storage_df = put_gt_tweet_in_storage(tweet['text'].decode(), storage_df, tweet_id, bow=bow) #.decode()
        except:
            print('Failed to process twitt: {0}, {1}'.format(i, tweet_id))
    return storage_df


if __name__ == '__main__':
    tweet_to_check = u'''Donald Trump is not fucking dead'''
    regenerate = True
    bow = False
    df_storage = read_csv_with_tweets(os.path.join(config.data_folder, config.tweets_filename), regenerate=regenerate, bow=bow)
    scores = compare_tweet_with_storage(tweet_to_check, df_storage, bow=bow)
    print(scores)


    # tweets = [u"Donald Trump was killed yesterday!",
    #           u"Donald Trump was not killed yesterday!"
    #           u"Donald Trump is gay",
    #           u"Donald Trump killed his wife!",
    #           u"Donald Trump launched a rocket and started a world war!"]


