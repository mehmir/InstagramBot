import flask

from api.BotService import BotService

app = flask.Flask(__name__)
# app.config["DEBUG"] = True


@app.route('/instauser/verify', methods=['GET'])
def verify_user():
    insta_user = flask.request.args.get('user')
    BotService.check_update_login(insta_user)
    return "<h1>"+insta_user+"</h1><p>login checked.</p>"


@app.route('/targetpage/update', methods=['GET'])
def target_page_update():
    insta_user = flask.request.args.get('target')
    BotService.update_page_info(insta_user)
    return "<h1>"+insta_user+"</h1><p>Page info updated.</p>"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
