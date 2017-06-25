# encoding=utf8
from credentials import FB_TOKEN
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
from urlparse import urlparse

sys.setdefaultencoding('utf8')
parser = English()

SPLIT = True
ENTITIES_TO_CONSIDER = ['PERSON', 'FACILITY', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LANGUAGE']


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
    print('Tokenizer:', tweet)
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
        output = [((entity.text, entity.label_, clust_dict)) for entity in entities if entity.label_ in ENTITIES_TO_CONSIDER]
    else:

        if SPLIT:
            verb_vector = np.zeros([300])
            noun_vector = np.zeros([300])
            adj_vector = np.zeros([300])
            verb_cnt = 0
            noun_cnt = 0
            adj_cnt = 0
            for token in parsedEx:
                if token.pos_ == 'VERB':
                    verb_vector += token.vector
                    verb_cnt += 1
                elif token.pos_ == 'NOUN':
                    noun_vector += token.vector
                    noun_cnt += 1
                elif token.pos_ == 'ADJ':
                    adj_vector += token.vector
                    adj_cnt += 1
            verb_vector = 1. * verb_vector / (verb_cnt + 10**(-10))
            noun_vector = 1. * noun_vector / (noun_cnt + 10**(-10))
            adj_vector = 1. * adj_vector / (adj_cnt + 10**(-10))
            output = [((entity.text, entity.label_, [verb_vector, noun_vector, adj_vector])) for entity in entities  if entity.label_ in ENTITIES_TO_CONSIDER]
        else:
            output = [((entity.text, entity.label_, out_vector)) for entity in entities  if entity.label_ in ENTITIES_TO_CONSIDER]
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
    print(tweet)
    transformed_tweet = transform_tweet(tweet, bow)
    print([x[0] for x in transformed_tweet], [np.sum(y) for y in (x[2] for x in transformed_tweet)])
    scores = {}
    for i, (entity, entity_type, vector_array) in enumerate(transformed_tweet):
        temp_score = 0.0
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
                if SPLIT:
                    result = [1 - cosine(vector_array[x], item['Vector array'][x]) for x in range(3)]
                    isnan = np.isnan(result)
                    res = 0.0
                    for v in range(3):
                        if not isnan[v]:
                            res+=result[v]
                    res = 1.0 * res/(np.sum(isnan==False)+10**(-10))
                    temp_score = np.max([res, temp_score])
                    # print(entity, entity_type)
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

import requests

def check_info_source(url):
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    domain = domain.replace("www.", "")

    sorces = pd.read_csv('sources.csv')
    untrusted_sources = sorces['url'].tolist()

    return int(domain not in untrusted_sources)

def check_virality(url):

    if url[-1]=='/':
        return -1,-1,-1,-1

    str =  "https://graph.facebook.com/v2.9/?id="+url+"&fields=engagement&access_token="+FB_TOKEN
    try:
        res = requests.get(str)
        out = res.json()
        comments =out['engagement']['comment_count'] + out['engagement']['comment_plugin_count']
        reaction =  out['engagement']['reaction_count']
        share = out['engagement']['share_count']
        total_engaged = comments+reaction+share
    except:
        return -1,-1,-1,-1



    return comments, reaction, share, total_engaged


if __name__ == '__main__':
    tweet_to_check = u'''Pakistan oil tanker inferno kills at least 123'''
    regenerate = False
    bow = False
    df_storage = read_csv_with_tweets(os.path.join(config.data_folder, config.tweets_filename), regenerate=regenerate, bow=bow)
    scores = compare_tweet_with_storage(tweet_to_check, df_storage, bow=bow)
    print(scores)


    # tweets = [u"Donald Trump was killed yesterday!",
    #           u"Donald Trump was not killed yesterday!"
    #           u"Donald Trump is gay",
    #           u"Donald Trump killed his wife!",
    #           u"Donald Trump launched a rocket and started a world war!"]


