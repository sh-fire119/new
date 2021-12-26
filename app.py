
from re import template
from sqlite3.dbapi2 import complete_statement
from types import MethodDescriptorType
from typing import ItemsView
from flask import Flask, render_template, request, redirect, session,  url_for
import os
import sqlite3, random

from flask.wrappers import Request

app = Flask(__name__)

app.secret_key = "sunabaco"


#TOP画面（login.html)からスタートできるようにした。
@app.route("/")
def index():
    return render_template("login.html")




# タスク追加ページを表示
@app.route("/add", methods = ["GET"])
def add_get():
    if "user_id" in session:
        return render_template("add.html")
    else:
        return redirect("/list")

# 入力フォームで追加したタスクをＤＢに登録する処理
@app.route("/add", methods = ["POST"])
def add_post():
    if "user_id" in session:
        user_id =session["user_id"]
        date = request.form.get("date")
        who = request.form.get("who")
        present = request.form.get("present")
        comment = request.form.get("comment")
        pic = request.form.get("pic")

         # ＤＢの接続
        conn = sqlite3.connect("present.db")
        c = conn.cursor()
        c.execute("insert into presents values (null,?,?,?,?,?,?)",(date,who,present,comment,pic,user_id))
        # ＤＢに登録する(＝変更を加える）ので、変更の内容を保存する
        conn.commit()
        c.close()
        return redirect("/list")
    else:
        return redirect("/login")


# リストの表示
@app.route("/list")
def list(): #ＤＥへの接続と、データをとってくるＳＱＬ文を書いて
    if "user_id" in session:
        user_id = session["user_id"]
        conn = sqlite3.connect("present.db")
        c = conn.cursor()
        c.execute("select id,date,who,present,comment,pic from presents where user_id = ?",(user_id,))
        present_list = [] #task_listという変数の中の配列に以下のものを入れる
        for row in c.fetchall():
            present_list.append({"id":row[0],"date":row[1],"who":row[2],"present":row[3],"comment":row[4],"pic":row[5]})
        c.close()
        print(present_list)
        return render_template("list.html",present_list=present_list)
    else:
        return redirect("/login")


#編集
@app.route("/edit/<int:id>")
def edit(id):
    if "user_id" in session:
        conn = sqlite3.connect("present.db")
        c = conn.cursor()
        c.execute("select * from presents where id = ?",(id,))  
        present = c.fetchall()
        c.close()
        if present is not None:
            present = present[0] #タプルを外している
        
        else:
            return "タスクがないよ"
        print(present)
        item = {"id":id,"date":present[1],"who":present[2],"present":present[3],"comment":present[4],"pic":present[5]}
        return render_template("edit.html",item = item)
    else:
        return redirect("/login")


    #タスクの内容を編集(更新）する
@app.route("/edit",methods = ["POST"])
def edit_post():
    if "user_id" in session:
        # 入力フォームのデータをとってくる
        present_id = request.form.get("present_id")
        present_date = request.form.get("date")
        present_who = request.form.get("who")
        present_present = request.form.get("present")
        present_comment = request.form.get("comment")
        present_pic = request.form.get("pic")
        

        # データベースとの接続
        conn = sqlite3.connect("present.db")
        c = conn.cursor()
        c.execute("update presents set date = ?, who = ?, present = ?, comment = ?, pic = ? where id = ?",(present_date,present_who,present_present,present_comment,present_pic,present_id))
        # データの更新
        conn.commit()
        c.close()
        # /listを表示
        return redirect("/list")
    else:
        return redirect("/login")

# 削除
@app.route("/del/<int:id>")
def del_present(id):
    if "user_id" in session:
        conn = sqlite3.connect("present.db")
        c = conn.cursor()
        c.execute("delete from presents where id = ?",(id,))
        conn.commit()
        c.close()
        return redirect("/list")
    else:
        return redirect("/login")    



#新規登録のページを表示
@app.route("/regist", methods=["GET"])
def regist_get():
    if "user_id" in session:
        return render_template("regist.html")
    else:
        return render_template("regist.html")
#新規登録の処理
@app.route("/regist", methods=["POST"])
def regist_post():
    #入力ホームのデータをとってくる
    name = request.form.get("user_name")
    password = request.form.get("password")
    # user_id = request.form.get("user_id")
# ＤＢの接続
    conn = sqlite3.connect("present.db")
    c = conn.cursor()
    c.execute("insert into users values (null,?,?)",(name,password))
    # ＤＢに登録する(＝変更を加える）ので、変更の内容を保存する
    conn.commit()
    c.close()
    return redirect("/login")

#ログイン画面の表示
@app.route("/login", methods = ["GET"])
def login_get():
    if "user_id" in session:
        return redirect("/list")
    else:
        return render_template("/login.html")
        
#ログイン機能の処理
@app.route("/login", methods = ["POST"])
def login_post():
    #入力ホームのデータをとってくる
    name = request.form.get("user_name")
    password = request.form.get("password")
# ＤＢの接続
    conn = sqlite3.connect("present.db")
    c = conn.cursor()
    c.execute("select id from users where name = ? and password = ?",(name,password))
    user_id = c.fetchone()
    c.close()
    if user_id is None:
        return render_template("login.html")
    else:
        session["user_id"] = user_id[0]
        print(user_id)
        return redirect("/list")

#ログアウト
@app.route("/logout", methods = ["GET"])
def logout():
    session.pop("user_id",None) #sessionからuser_idを取り除く
    return redirect("/login")

#画像のアップロード
# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = './static/img/'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route("/uploads", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == " ":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("uploaded_file",
                                    filename=filename))
    return '<!doctype html><title>Upload new File</title><h1>Upload new File</h1><form method=post enctype=multipart/form-data><input type=file name=file><input type=submit value=Upload></form>'

@app.route("/uploads/<filename>")
# ファイルを表示する
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)




if __name__ =="__main__":
    app.run(debug=True)