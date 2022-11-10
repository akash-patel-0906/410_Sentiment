from flask import Flask, render_template, request, flash
from textblob import TextBlob
import urllib.request
import re
from youtube_transcript_api import YouTubeTranscriptApi
import webbrowser
from wordcloud import WordCloud,  ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
from youtube_search import YoutubeSearch
from pytube import YouTube

app = Flask(__name__)
app.secret_key = "asdasdjkjk1kj2kljkjk"

@app.route('/static/images/<cropzonekey>')
def images(cropzonekey):
    return render_template("images.html", title=cropzonekey)

#export FLASK_ENV=development
#index file:
@app.route("/")
def index():

	return render_template("index.html")

@app.route("/analysis", methods=['POST', 'GET'])
#conduct sentiment analysis
def analysis():

    #generates urls
    input = str(request.form['topic_input'])
    ids=[]
    results = YoutubeSearch(input, max_results=10).to_dict()
    for v in results:
        ids.append('https://www.youtube.com' + v['url_suffix'])


    #string containing titles
    list_of_info=""
    for id in range (0,min(10,len(ids))):
        title = ids[id]
        video = YouTube(title)
        print(video.title)
        list_of_info+=video.title + "\n"

    #sentiment calculation
    sentiment = TextBlob(list_of_info).sentiment.polarity

    #add negative boundary here:
    #add positive bounday here:


    sentiment_empirical =""
    if sentiment<0:
        sentiment_empirical="negative"
    elif sentiment>0:
        sentiment_empirical="positive"
    else:
        sentiment_empirical="neutral"


    overall = "The overall sentiment is: " + str(sentiment) + " which is " + sentiment_empirical

    #generation of WordCloud
    wordcloud = WordCloud(background_color="white",max_words=200, contour_width=3, contour_color='firebrick', collocations=False).generate(list_of_info)
    plt.figure(figsize=[20,10])
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig('static/test.png')

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
    
