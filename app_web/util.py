import joblib
from nltk.corpus import stopwords
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer

model = joblib.load('model_v2.joblib')

from bs4 import BeautifulSoup
import requests


def standardize_phrase(donnees):
        donnees = donnees.replace(r"http\S+", "")
        donnees = donnees.replace(r"http", "")
        donnees = donnees.replace(r"@\S+", "")
        donnees = donnees.replace(r"[0-9(),;!:?@<>.=\'\`\"\-\_\n]", " ")
        donnees = donnees.replace(r"@", "at")
        donnees = donnees.lower()
        
        lemmatizer = FrenchLefffLemmatizer()
        corpus = []
        message = donnees.split()
        message =[word for word in message if word not in stopwords.words('french')]
        message = [lemmatizer.lemmatize(word, 'n') for word in message]
        message = [lemmatizer.lemmatize(word, 'v') for word in message]
        message = [lemmatizer.lemmatize(word, 'a') for word in message]
        message = [lemmatizer.lemmatize(word, 'r') for word in message]       

        message = ' '.join(message)
        corpus.append(message)
        
        return corpus
    
def predict_com(corpus_phrase):
    vectorisation=model['vectorizer'].transform(corpus_phrase)
    prediction = model['model_regressor'].predict(vectorisation)
    proba = model['model_regressor'].predict_proba(vectorisation)

    return (prediction, proba)

def web_scrapping(num_film, note = 5):  
            """recueil tous les commentaires d'un film à partir de son numéro"""
            commentaires= []
            i = 1

            #la boucle se stoppe quand une span particulière est détecté sur une page de commentaire
            while True:
                url = f'''https://www.allocine.fr/film/fichefilm-{num_film}/critiques/spectateurs/?page={i}'''
                response = requests.get(url)
                soup = BeautifulSoup(response.text,'html.parser')

                links=soup.findAll('div', {"class": "hred review-card cf"})

                i += 1
                
                for link in links: 
                    new_com = {}
                    new_com['note'] = float(link.find("span", {'class':"stareval-note"}).text.replace(',', '.'))
                    new_com['commentaire'] = link.find("div", {'class':"content-txt review-card-content"}).text.replace('"', '').replace("\n", '').replace('’', "'")
                    new_com['avis_IA'] = predict_com(standardize_phrase(link.find("div", {'class':"content-txt review-card-content"}).text.replace('"', '').replace("\n", '').replace('’', "'")))[0]
                    if float(new_com['note']) <= float(note):
                        commentaires.append(new_com)

                #permet de stopper le scrapping sans préciser le nombre de page dans la fonction 'web_scrapping'
                stop = soup.find('span', {"class": "button button-md button-primary-full button-right button-disabled"})
                if stop:
                    break
            return commentaires

def titre_film_allocine(num_film):
        url = f'''https://www.allocine.fr/film/fichefilm_gen_cfilm={num_film}.html'''
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'html.parser')

        links = soup.findAll("div", {"class": "titlebar titlebar-page"})              

        for link in links:  
            title = link.find("div", {'class':"titlebar-title-lg"}).text
        return title
            