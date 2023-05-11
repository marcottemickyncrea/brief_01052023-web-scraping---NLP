import mysql.connector as mysqlpy
from util import standardize_phrase, predict_com, web_scrapping, titre_film_allocine
from flask import render_template, redirect, request, flash
from app import app

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


coms_db = {'user': 'root',
           'password': 'example',
           'host': 'localhost',
           'port': '3308',
           'database': 'com_testés'}


@app.route('/', methods=['GET', 'POST', 'PUT'])
def textarea():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        commentaire = request.form['commentaire']
        sentiment = request.form['sentiment']
        bool = ''
        proba = ''

        if len(commentaire) == 0:
            flash('Votre commentaire est trop court !!')
        else:
            standard = standardize_phrase(commentaire)
            predict = predict_com(standard)

            if predict[0] == 0:
                bool = False
            elif predict[0] == 1:
                bool = True

            if predict[1][0][0] > predict[1][0][1]:
                proba = f'''Je suis sûr à {round(predict[1][0][0] * 100, 2)} que le commentaire est négatif !'''
            elif predict[1][0][1] > predict[1][0][0]:
                proba = f'''Je suis sûr à {round(predict[1][0][1] * 100, 2)} que le commentaire est positif !'''

            bdd = mysqlpy.connect(user=coms_db["user"], password=coms_db["password"],
                                  host=coms_db["host"], port=coms_db["port"], database=coms_db["database"])
       
            cursor = bdd.cursor()
            cursor.execute(
                f'''INSERT INTO commentaires (commentaire, avis_model_IA, avis_perso)
                VALUES("{commentaire.replace('"', "'")}", "{float(predict[0])}", "{float(sentiment)}");''')
            bdd.commit()
   
            cursor.close()
            bdd.close()

        return render_template('index.html', commentaire=commentaire, like=bool, proba=proba)

@app.route('/com-analysés', methods=['GET'])
def com_analysés():
    if request.method == 'GET':
        bdd = mysqlpy.connect(user=coms_db["user"], password=coms_db["password"],
                                  host=coms_db["host"], port=coms_db["port"], database=coms_db["database"])
       
        cursor = bdd.cursor()
        cursor.execute(
            f'''SELECT * FROM commentaires ORDER BY date DESC;''')
        commentaires = cursor.fetchall()

        cursor.close()
        bdd.close()

        return render_template('com-analysés.html', commentaires= commentaires)

@app.route('/scrapping', methods=['GET', 'POST'])
def scrapping():
    if request.method == 'GET':
        return render_template('scrapping.html')
    elif request.method == 'POST':
        num_film = request.form['numero-film']        
        
        commentaires = web_scrapping(num_film)
        titre_film = titre_film_allocine(num_film)

        return render_template('scrapping.html', commentaires = commentaires, titre_film = titre_film)
