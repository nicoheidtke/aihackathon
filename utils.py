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


if __name__ == '__main__':
    tweet = u"Donald Trump was killed yesterday!"
    out = transform_tweet(tweet)