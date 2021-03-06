from flask import Flask, jsonify, request, make_response
from utils import check_virality, compare_tweet_with_storage, check_info_source
from images import check_url

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

        share, total_engaged, resource_trust = None, None, None
        if url:
            comments, reaction, share, total_engaged = check_virality(url)
            resource_trust = check_info_source(url)

        analysis_result = None
        if tweet:
            tweet = tweet if len(tweet) < 1000 else tweet[:1000]
            analysis_result = compare_tweet_with_storage(tweet)

        result = {
            'status': STATUS_OK,
            'data': {
                'credibility': analysis_result,
                'engaged': total_engaged,
                'shares': share,
                'site_credibility': resource_trust
            },
            'source_text': tweet
        }
        return jsonify(result)
    except AssertionError:
        return make_response(jsonify({'status': STATUS_ERROR, 'message': 'malformed request'}), 400)
    # except:
    #     return make_response(jsonify({'status': STATUS_ERROR, 'message': 'oops...'}), 500)


@app.route("/process_image", methods=['POST'])
def process_image():
    try:
        assert request.is_json
        assert 'imageUrl' in request.json

        image_url = request.json['imageUrl']
        trusted_source_url, trusted_source_image = None, None
        trusted_data = check_url(image_url)
        if trusted_data is not None and 'image_url' in trusted_data:
            trusted_source_image = trusted_data.image_url
            trusted_source_url = trusted_data.url

        result = {
            'status': STATUS_OK,
            'trusted_source_url': trusted_source_url,
            'trusted_source_image': trusted_source_image,
            'source_url': image_url
        }
        return jsonify(result)
    except AssertionError:
        return make_response(jsonify({'status': STATUS_ERROR, 'message': 'malformed request'}), 400)


if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
