from flask import Flask, render_template, request, flash
from wordcloud import WordCloud,  ImageColorGenerator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from youtube_search import YoutubeSearch
from pytube import YouTube
import pandas as pd
from LeXmo import LeXmo
import plotly.express as px
import plotly.graph_objects as go


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.secret_key = "asdasdjkjk1kj2kljkjk"
app.config["CACHE_TYPE"] = "null"

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

#export FLASK_ENV=development
#index file:
@app.route("/")
def index():

	return render_template("index.html")

@app.route("/analysis", methods=['POST', 'GET'])
#conduct sentiment analysis
def analysis():
   
   #contains dictionary of emotions
    other_emotions_dictionary={
        'positive':0,
        'negative':0,
        'anger':0,
        'anticipation':0, 
        'disgust':0,
        'fear':0,
        'joy':0,
        'sadness':0,
        'surprise':0,
        'trust':0
    }

    #generates urls from url_request
    input = str(request.form['topic_input'])
    ids=[]
    results = YoutubeSearch(input, max_results=30).to_dict()
    for v in results:
        ids.append('https://www.youtube.com' + v['url_suffix'])


    #creates string using list of titles
    list_of_info=""
    for id in range (0,min(30,len(ids))):
        title = ids[id]
        video = YouTube(title)
        list_of_info+=video.title + "\n"

 

    #calculate emotions utizling Lexmo (unigram-sentiment analyzer)
    emotions=LeXmo.LeXmo(list_of_info)
    
    #adds emotions to dicionary
    for key in other_emotions_dictionary:
        other_emotions_dictionary[key] = emotions[key]


    #generates sentiment values
    sentiment = max(other_emotions_dictionary, key=other_emotions_dictionary.get)
    sentiment_empirical = other_emotions_dictionary.get(sentiment)
    
    #final sentiment
    overall = "The overall sentiment of " +str(input) + " is " + str(sentiment) + " with a value of " + str(sentiment_empirical)
   
    #generate graph
    names = list(other_emotions_dictionary.keys())
    values = list(other_emotions_dictionary.values())

    plt.bar(range(len(other_emotions_dictionary)), values, tick_label=names)
    plt.xticks(range(10)) # add loads of ticks
    plt.grid()

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = 0.2 # inch margin
    s = maxsize/plt.gcf().dpi*10+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    plt.savefig('static/other_emotions.png',dpi=100)

    plt.clf()
    plt.cla()
    plt.close()

 

    #generation of WordCloud from words
    wordcloud = WordCloud(background_color="white",max_words=200, contour_width=1, contour_color='firebrick', collocations=False).generate(list_of_info)
    plt.figure(figsize=[80,40])
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig('static/word_cloud.png',dpi=100)

    plt.clf()
    plt.cla()
    plt.close()


    flash(overall)
    return render_template("analysis.html")
    



#tries to get rid of cash
if __name__ == "__main__":
    if app.config["DEBUG"]:
        @app.after_request
        def after_request(response):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
            response.headers["Expires"] = 0
            response.headers["Pragma"] = "no-cache"
            return response
    app.run(host="127.0.0.1", port=5001)
    
#export FLASK_DEBUG=1