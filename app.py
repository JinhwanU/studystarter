from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, session
from forms import RegistrationForm

app = Flask(__name__)
app.config["SECRET_KEY"] = 'd2707fea9778e085491e2dbbc73ff30e'

from pymongo import MongoClient

# client = MongoClient('mongodb://test:test@localhost', 27017)
client = MongoClient('localhost', 27017)
db = client.gangchu


# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('main.html')

@app.route('/readList', methods=['GET'])
def read_list():
    class_list = list(db.mystar.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'stars_list': class_list})


@app.route('/map')
def route_map():
    return render_template('map.html')


@app.route('/board')
def route_board():
    title_receive = request.args.get('title')
    review_list = list(db.review.find({'title': title_receive}, {'_id': False}))
    return render_template('board.html', review_list=review_list, title=title_receive)

@app.route('/writeBoard', methods=['POST'])
def write_review():
    # 1. 클라이언트로부터 데이터를 받기
    id_receive = request.form["id_give"]
    rating_receive = request.form["rating_give"]
    review_receive = request.form["review_give"]
    title_receive = request.form["title_give"]
    doc = {
        'id': id_receive, 'rating': rating_receive,
        'title': title_receive, 'review': review_receive,
    }
    db.review.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/mypage')
def route_mypage():
    return render_template('mypage.html')


@app.route('/signup', methods=["GET", "POST"])
def route_signup():
    form = RegistrationForm()

    if request.method == 'POST':
        if (form.validate() == False):
            return render_template('signup.html', form=form)
        else:
            flash(f'{form.username.data}님 환영합니다')
            return redirect(url_for("home"))

        # user = User.query.filter_by(username=form.username.data).first()
        # if not user:
        #     user = User(username=form.username.data,
        #                 password=generate_password_hash(form.password1.data),
        #                 email=form.email.data)
        #     db.session.add(user)
        #     db.session.commit()
        #     return redirect(url_for('main.index'))
        # else:
        #     flash('이미 존재하는 사용자입니다.')

    return render_template('signup.html', form=form)


@app.route("/login")
def route_login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
