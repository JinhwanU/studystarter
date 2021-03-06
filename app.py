import hashlib

import jwt
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from bson.objectid import ObjectId
from forms import LoginForm, SignupForm

app = Flask(__name__)

# CSRF(Cross-Site Request Forgery) 보호하기 위해 사용
# WTForms 라이브러리 사용 시 필수적으로 포함되어야 한다
# secrets import 후 secrets.token_hex(16) 해시함수 사용하여 토큰 생성
app.config["SECRET_KEY"] = 'sparta'
SECRET_KEY = "sparta"

from pymongo import MongoClient

client = MongoClient('mongodb://test:test@localhost', 27017)
# client = MongoClient('localhost', 27017)
db = client.gangchu


# 평점평균 값 추가해주기
def gi(name):
    temp = list(db.review.find({'title': name}, ))
    cnt = 0;
    for i in temp:
        rating = int(i['rating'])
        cnt += rating
    if cnt == 0:
        aver = '없음'
    else:
        aver = round(cnt / len(temp), 2)
    db.classlist.update_one({'title': name}, {'$set': {"aver": aver}}, False, True)


def gi2(name):
    temp = list(db.review.find({'title': name}, ))
    cnt = 0;
    for i in temp:
        rating = int(i['rating'])
        cnt += rating
    if cnt == 0:
        aver = '없음'
    else:
        aver = round(cnt / len(temp), 2)
    db.academies.update_one({'name': name}, {'$set': {"aver": aver}}, False, True)


# HTML 화면 보여주기
@app.route('/')
def home():
    # 평점평균 입력
    temp = list(db.classlist.find({}))
    temp1 = list(db.academies.find({}))
    for h in temp:
        insert = h['title']
        gi(insert);
    for h in temp1:
        insert = h['name']
        gi2(insert);
    # 로그인 확인
    token_receive = request.cookies.get('mytoken')
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"id": payload["id"]})
            return render_template('main.html', user_info=user_info)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("home", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))
    return render_template('main.html')


@app.route('/readClass', methods=['GET'])
def read_ClassList():
    class_list = list(db.classlist.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'class_list': class_list})


@app.route('/readAcademy', methods=['GET'])
def read_AcademyList():
    academy_list = list(db.academies.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'academy_list': academy_list})


@app.route('/map')
def route_map():
    token_receive = request.cookies.get('mytoken')
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"id": payload["id"]})
            return render_template('map.html', user_info=user_info)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("home", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))
    return render_template('map.html')


# 클릭한 강의리뷰 보러이동
@app.route('/boardclass', methods=['get'])
def route_board():
    title_receive = request.args.get('title')
    img_receive = db.classlist.find_one({'title': title_receive})
    img_url = img_receive['img_url']

    token_receive = request.cookies.get('mytoken')
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"id": payload["id"]})
            return render_template('board.html', title=title_receive, img_url=img_url, user_info=user_info)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("home", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))
    return render_template('board.html', title=title_receive, img_url=img_url)


@app.route('/boardacademy', methods=['get'])
def route_Aboard():
    title_receive = request.args.get('title')
    img_receive = db.academies.find_one({'name': title_receive})
    img_url = img_receive['imgsrc']

    token_receive = request.cookies.get('mytoken')
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"id": payload["id"]})
            return render_template('board.html', title=title_receive, img_url=img_url, user_info=user_info)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("home", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))
    return render_template('board.html', title=title_receive, img_url=img_url)


# 클릭한 강의리뷰출력
@app.route('/readBoard', methods=['get'])
def read_review():
    title_receive = request.args.get('title')
    mongo_list = db.review.find({'title': title_receive})
    sec_id = []
    for id_list in mongo_list:
        id_list['_id'] = str(id_list['_id'])
        sec_id.append(id_list)

    review_list = list(db.review.find({'title': title_receive}, {'_id': False}))
    return jsonify({'review_list': review_list, 'sec_id': sec_id, 'result': 'success'})


# 선택한 리뷰삭제
@app.route('/deleteBoard', methods=['POST'])
def delete_review():
    id_receive = request.form["id_give"]
    db.review.delete_one({'_id': ObjectId(id_receive)})
    return jsonify({'result': 'success'})


# 선택한 리뷰수정
@app.route('/updateBoard', methods=['POST'])
def update_review():
    id_receive = request.form["id_give"]
    review_receive = request.form["review_give"]
    db.review.update_one({'_id': ObjectId(id_receive)}, {'$set': {'review': review_receive}})
    return jsonify({'result': 'success'})


# 리뷰작성
@app.route('/writeBoard', methods=['POST'])
def write_review():
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


@app.route("/login", methods=["GET", "POST"])
def route_login():
    # forms에 선언한 RegistrationForm클래스의 자식 객체 생성
    form = LoginForm()

    # POST방식으로 호출한 경우 유효성 검증
    if request.method == 'POST':
        if not form.validate():
            return render_template('login.html', form=form)

        # 로그인 검증
        else:
            receive_id = form.userID.data
            receive_pw = form.password.data
            password_hash = hashlib.sha256(receive_pw.encode('utf-8')).hexdigest()

            result = db.users.find_one({'id': receive_id, 'password': password_hash})

            # 로그인 성공
            if result is not None:
                payload = {'id': receive_id, 'exp': datetime.utcnow() + timedelta(hours=1)}  # 로그인 1시간 유지
                token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
                return render_template("main.html", token=token)

            # 로그인 실패
            else:
                flash('아이디와 패스워드를 확인해주세요')
                return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/login/<signup>', methods=["GET", "POST"])
def route_signup(signup):
    form = SignupForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('login.html', form=form, login_form=signup)
        else:
            duplic_id = db.users.find_one({'id': form.userID.data}, {'_id': False, 'id': 1})
            duplic_email = db.users.find_one({'email': form.email.data}, {'_id': False, 'email': 1})
            duplic_check = [duplic_id, duplic_email]

            # None 필터링
        result = list(filter(None, duplic_check))

        # 중복 검사 ( result에 값이 존재하면 if문 내부 진입 )
        if result:
            for i in result:
                key = list(i.keys())
                flash(f'이미 사용된 {key} 입니다.')
            return render_template('login.html', form=form, login_form=signup)

        # 회원가입 성공(DB에 저장)
        else:
            # 비밀번호 암호화(hash)
            password_hash = hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()
            doc = {
                'id': form.userID.data, 'email': form.email.data, 'password': password_hash
            }
            db.users.insert_one(doc)
            flash(f'{form.userID.data}님 환영합니다. 로그인 후 이용해주세요')
            return redirect(url_for("home"))

    return render_template('login.html', form=form, login_form=signup)


@app.route('/api/maplist', methods=["GET"])
def get_map():
    # 학원 목록을 반환하는 API
    # 1. 데이터 베이스에서 학원 목록을 꺼내와야 한다.
    aca_list = list(db.academies.find({}, {'_id': False}))
    # aca_list 라는 키 값에 학원 목록을 담아 클라이언트에게 반환합니다.
    # 2. 그걸 클라이언트에 돌려준다
    return jsonify({'result': 'success', 'aca_list': aca_list})


@app.route('/like_academy', methods=["POST"])
def like_aca():
    title_receive = request.form["title_give"]
    address_receive = request.form["address_give"]
    action_receive = request.form["action_give"]
    print(title_receive, address_receive, action_receive)

    if action_receive == "like":
        db.shops.update_one({"title": title_receive, "address": address_receive}, {"$set": {"liked": True}})
    else:
        db.shops.update_one({"title": title_receive, "address": address_receive}, {"$unset": {"liked": False}})
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
