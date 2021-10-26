from flask import Flask, render_template, request
from xer_parse import Xer, parse_xer_file
from variance import find_task_changes, find_relationship_changes, find_resource_changes
from data.data import changes, projects

app = Flask(__name__)
CODEC = 'cp1252'

curr_xer = None
prev_xer = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template('index.html')
    if request.method == "POST":
        if (curr := request.files.get('current')) and (prev := request.files.get('previous')):
            curr_xer = Xer(**parse_xer_file(curr.read().decode(CODEC).splitlines()))
            prev_xer = Xer(**parse_xer_file(prev.read().decode(CODEC).splitlines()))
            find_task_changes(curr_xer, prev_xer)
            find_relationship_changes(curr_xer, prev_xer)
            find_resource_changes(curr_xer, prev_xer)
            projects['current'] = list(curr_xer.projects.values())[0]
            projects['previous'] = list(prev_xer.projects.values())[0]
    
            return render_template('results.html', changes=changes, projects=projects)

# @app.route('/results', methods=['POST'])
# def results():
#     if (curr := request.files.get('current')) and (prev := request.files.get('previous')):
#         curr_xer = Xer(**parse_xer_file(curr.read().decode(CODEC).splitlines()))
#         prev_xer = Xer(**parse_xer_file(prev.read().decode(CODEC).splitlines()))
#         find_task_changes(curr_xer, prev_xer)
#         find_relationship_changes(curr_xer, prev_xer)
#         find_resource_changes(curr_xer, prev_xer)
#         projects['current'] = list(curr_xer.projects.values())[0]
#         projects['previous'] = list(prev_xer.projects.values())[0]
    
#         return render_template('results.html', changes=changes, projects=projects)

#     return render_template('index.html')


# if __name__ == '__main__':
#     app.run()