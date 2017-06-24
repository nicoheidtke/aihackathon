from flask import Flask, jsonify, request, make_response
from utils import compare_tweet_with_storage, check_virality
from utils import check_virality, compare_tweet_with_storage
from urlparse import urlparse

app = Flask(__name__)

STATUS_OK = 'ok'
STATUS_ERROR = 'error'


@app.route("/")
def hello():
    return jsonify({'status': STATUS_OK})


@app.route("/process_text", methods=['POST'])
def process_text():
    try:
        assert request.is_json
        assert 'text' in request.json

        tweet = request.json['text']
        url = request.json['pageUrl']
        comments, reaction, share, total_engaged =check_virality(url)
        analysis_result = compare_tweet_with_storage(tweet)

        result = {
            'status': STATUS_OK,
            'data': {
                'credibility': analysis_result,
                'engaged': total_engaged,
                'shares': share
            },
            'source_text': tweet
        }
        return jsonify(result)
    except AssertionError:
        return make_response(jsonify({'status': STATUS_ERROR, 'message': 'malformed request'}), 400)
    except:
        return make_response(jsonify({'status': STATUS_ERROR, 'message': 'oops...'}), 500)


if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
