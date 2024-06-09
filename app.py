import google.generativeai as genai
import pandas as pd
from bs4 import BeautifulSoup
from flask import Flask, request, redirect, url_for, render_template, render_template_string
from markdown import markdown

genai.configure(api_key='YOUR_KEY_HERE')  # Enter your api key here!

model = genai.GenerativeModel('gemini-1.5-pro')

app = Flask(__name__)


def md_to_text(md):
    html = markdown(md)
    text = ''.join(BeautifulSoup(html).findAll(text=True, features="html.parser"))
    return text


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form['text']
        file = request.files['file']

        df = pd.read_csv(file)
        csv = df.to_csv(index=False)
        column_headers = list(df.columns)

        response = model.generate_content(
            "Here is the CSV data as a string:\n" + csv + "\nAnd here is the prompt\n" + prompt + "\nDescribe the one singular best type of graph to represent this prompt with the given data")
        col_response = model.generate_content(
            "Here is the CSV data as a string:\n" + csv + "\nAnd here is the prompt\n" + prompt + "\nMake a list, separated by commas, of the ONLY RELEVANT HEADERS from the csv file to make a graph out of the data based on the prompt")

        response = md_to_text(response.text)
        col_response = md_to_text(col_response.text)

        # found_headers = [header for header in column_headers if header in col_response]
        # fig, ax = plt.subplots()
        # if 'bar' in response.lower():
        #     df[found_headers].plot(kind='bar', ax=ax)
        # elif 'line' in response.lower():
        #     df[found_headers].plot(kind='line', ax=ax)
        # elif 'scatter' in response.lower():
        #     df.plot(kind='scatter', x=found_headers[0], y=found_headers[1], ax=ax)
        # elif 'box' in response.lower():
        #     plt.boxplot([df[col] for col in found_headers], labels=found_headers)
        # img = io.BytesIO()
        # plt.savefig(img, format='png')
        # img.seek(0)
        # with open('graph.png', 'wb') as f:
        #     f.write(img.getbuffer())

        return redirect(url_for('results', response=response, headers=col_response))

    return render_template('index.html')


@app.route('/results')
def results():
    output = request.args.get('response')
    headers = request.args.get('headers')

    response = output + '\n' + headers

    return render_template('results.html', response=response)


@app.route('/about-us')
def aboutus():
    return render_template('about-us.html')


@app.route('/sample-graphs')
def sampleGraphs():
    return render_template('sample-graphs.html')


@app.route('/error')
def error():
    return render_template_string('An error was encountered.')


if __name__ == '__main__':
    app.run(debug=True)
