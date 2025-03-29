from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests


app = Flask(__name__)

#client = MongoClient('localhost', 27017)
client = MongoClient('3.83.230.66', 27017, username="test", password="test")
db = client.dbsparta_plus_week2


@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    msg = request.args.get("msg")
    words = list(db.words.find({}, {"_id": False}))
    return render_template("index.html", words=words, msg=msg)


@app.route('/detail/<keyword>')
def detail(keyword):
    # 단어장에 있는 단어냐 없는 단어냐에 따라 버튼 다르게 표시하기
    status_receive = request.args.get("status_give")

    # API에서 단어 뜻 찾아서 결과 보내기
    r = requests.get(f"https://www.dictionaryapi.com/api/v3/references/spanish/json/{keyword}?key=84c2e134-b89b-44b9-bdb5-597521f39ecd")
    if r.status_code != 200:
        return redirect(url_for("main", msg=f"'{keyword}' doesn't exist"))
    result = r.json()
    print(result)
    return render_template("detail.html", word=keyword, results=result, status=status_receive)


@app.route('/api/save_word', methods=['POST'])
def save_word():
    # 단어 저장하기
    word_receive = request.form["word_give"]
    definition_receive = request.form["definition_give"]
    doc = {"word": word_receive, "definition": definition_receive}
    db.words.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f'successfully saved the word "{word_receive}"!'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    # 단어 삭제하기
    word_receive = request.form["word_give"]
    db.words.delete_one({"word": word_receive})
    db.examples.delete_many({"word": word_receive})
    return jsonify({'result': 'success', 'msg': f'successfully deleted the word "{word_receive}"!'})


@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    # 예문 가져오기
    word_receive = request.args.get("word_give")
    examples = list(db.examples.find({"word": word_receive}, {"_id": False}))
    return jsonify({'result': 'success', 'examples': examples})


@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    # 예문 저장하기
    word_receive = request.form["word_give"]
    ex_receive = request.form["ex_give"]
    doc = {"word": word_receive, "example": ex_receive}
    db.examples.insert_one(doc)
    return jsonify({'result': 'success', 'msg': 'successfully saved!'})


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    # 예문 삭제하기
    word_receive = request.form["word_give"]
    number_receive = request.form["number_give"] #와 씨바 이거 스트링이었다.. 이거 안봤으면 어쩔뻔 ㅠ 인티저로 바꿔주기! 드뎌 끝!!!!!!!!!!!!
    
    examples = list(db.examples.find({"word": word_receive}, {"_id": False}))
    print(examples, "hahahah")

    for idx, ex in enumerate(examples): #이부분 어려웟쪙 ㅠ 순서대로 저장되니까 html에서 받은 number를 인덱스삼아 enumerate해서 찾는것 좋은 아이디어!
        if idx == int(number_receive):
            print(idx, ex)
            db.examples.delete_one({"example": ex["example"]}) #이것도 개어려웠따 ㅠ ex가 "word"랑 "example"로 이루어진 딕셔너리라는걸 까묵었네 ㅅㅂ ㅠ
        
    return jsonify({'result': 'success', 'msg': 'successfully deleted!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)