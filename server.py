from flask import Flask, jsonify, request, make_response
from utils import check_virality, compare_tweet_with_storage

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

        tweet = request.json['text'] if 'text' in request.json else None
        url = request.json['pageUrl'] if 'pageUrl' in request.json else None

        share, total_engaged = None, None
        if url:
            comments, reaction, share, total_engaged = check_virality(url)

        analysis_result = None
        if tweet:
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
