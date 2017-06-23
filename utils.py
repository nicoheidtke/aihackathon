import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from spacy.en import English
parser = English()

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

if __name__ == '__main__':
    tweet_to_check = u"Donald Trump was murdered yesterday!"

    tweets = [u"Donald Trump was killed yesterday!",
              u"Donald Trump is gay",
              u"Donald Trump killed his wife!",
              u"Donald Trump launched a rocket and started a world war!"]
    df = pd.DataFrame(columns=['Entity', 'Entity type', 'Vector array'])
    for tweet in tweets:
        df = put_gt_tweet_in_storage(tweet, df)
    print(df.head())
    scores = compare_tweet_with_storage(tweet_to_check, df)
    print(scores)
