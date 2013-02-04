from flask import Flask, request, render_template
from parser import parse_csv_file
from charts import expenses_pie_chart
import yaml

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def upload_form():
    pie_data = None
    if request.method == 'POST':
        categories = yaml.load(open('categories.yml', 'r'))
        parsed_data = parse_csv_file(request.files['csv_file'], categories)
        pie_data = expenses_pie_chart(parsed_data)
    return render_template('upload_form.html', pie_data=pie_data)


if __name__ == '__main__':
    app.debug = True
    app.run()
