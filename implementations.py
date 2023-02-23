
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from deep_translator import GoogleTranslator
import detectlanguage

from flask import Flask, render_template, request, url_for, flash, redirect
from flask_wtf.csrf import CSRFProtect

import random
import os
from environs import Env


env = Env()
env.read_env()

analyzer = SentimentIntensityAnalyzer()

phrases = [
    {'title': '1',
     'phrase': 'This film is very very good!',
     'score': '0.5808',
     'score_tb': '1.0',
     'score_subjectivity': '0.78',
     'sentiment': 'positive',
     'sentiment_tb': 'positive',
     'subjectivity_tb': 'subjective', 
     'language': 'EN',
     'translated': 'Zaj movie no zoo saib heev!',
     'language_translated': 'Hmong',
     'translated_es': 'Esta película es muy muy buena!',


    },    
    {'title': '2',
     'phrase': 'Esta rádio até que é boa.',
     'score': '0.4927',
     'score_tb': '0.7',
     'score_subjectivity': '0.60',
     'sentiment': 'neutral',
     'sentiment_tb': 'positive',
     'subjectivity_tb': 'subjective',
     'language': 'PT',
     'translated':'Radio ena e ntle ruri.',
     'language_translated': 'Sesotho',
     'translated_es': 'Esta radio es muy buena.',
    },
]


# instance flask
app = Flask(__name__)
#app.secret_key = env.str('FLASK_SECRET_KEY')
app.secret_key = os.getenv('FLASK_SECRET_KEY')

#detectlanguage.configuration.api_key = env.str('DETETCLANGUAGE_API_KEY')
detectlanguage.configuration.api_key = os.getenv('DETETCLANGUAGE_API_KEY')


# home
@app.route('/', methods=('GET', 'POST'))
def index():    
    if request.method == 'POST':
        try:
            title = {'title': request.form['title']}
        except:
            
            title = {'title': str(len(phrases)+1)}

        content = request.form['content']

        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:

            res = sentence_analysis(content)
            
            res_full = {**title, **res}
            phrases.append(res_full)
            return redirect(url_for('index'))
            
    return render_template('index.html', phrases=phrases)    


# check subjectivity: very objective (0) or very subjective (1)
def check_subjectivity(score):
    if 0 <= score <= 0.4:
        sentiment = 'objective'
    elif 0.4 <= score < 0.6:
        sentiment = 'neutral'
    elif 0.6 <= score <= 1:
        sentiment = 'subjective'
    return sentiment

# check whether sentiment very positive (1), neutral(0) or very negative (-1)
def check_sentiment(score):
    if -0.5 <= score <= 0.5:
        sentiment = 'neutral'
    elif score > 0.5:
        sentiment = 'positive'
    elif score < -0.5:
        sentiment = 'negative'
    return sentiment


# sentence analysis
def sentence_analysis(sentence):
    # input: user sentence
    # output: score
    
    sentence_en, _ = language_translate(sentence, lang='en')
    
    analyzer.polarity_scores(sentence_en)
    score = analyzer.polarity_scores(sentence_en)['compound']
    sentiment = check_sentiment(score)

    score_tb = TextBlob(sentence_en).sentiment.polarity    
    sentiment_tb = check_sentiment(score_tb)
    score_subjectivity = TextBlob(sentence_en).sentiment.subjectivity
    subjectivity_tb = check_subjectivity(score_subjectivity)

    lang = language_detect(sentence)
    lang_choosed = random.choice(GoogleTranslator().get_supported_languages())
    translated, lang_translated = language_translate(sentence, lang_choosed)
    translated_es, lang_translated_es = language_translate(sentence_en, 'es')

    res = {
        'phrase': sentence, 'score': score, 'score_tb': score_tb, 'score_subjectivity': score_subjectivity,
        'sentiment': sentiment, 'sentiment_tb': sentiment_tb, 'subjectivity_tb': subjectivity_tb, 
        'language': lang, 'translated': translated, 'language_translated': lang_translated,
        'translated_es': translated_es,
    }
    return res


# language detect
def language_detect(sentence):
    try:
        lang = detectlanguage.detect(sentence)[0]['language']
        
    except:
        lang = ''
    return lang.upper()


# language translate
def language_translate(sentence, lang):
    try:
        translator = GoogleTranslator(source='auto', target=lang)
        translated = translator.translate(str(sentence))        
    except:
        translated = 'Error'
    
    return translated, lang.title()
