from flask import Flask, render_template, request
from xer_parse import Xer, parse_xer_file
from variance import find_task_changes, find_relationship_changes, find_resource_changes
from data.data import changes

app = Flask(__name__)
CODEC = 'cp1252'

curr_xer = None
prev_xer = None

@app.route('/')
def index():
    # if request.method == "POST":
    #     if (curr := request.files.get('current')) and (prev := request.files.get('previous')):
    #         curr_xer = Xer(**parse_xer_file(curr.read().decode(CODEC).splitlines()))
    #         prev_xer = Xer(**parse_xer_file(prev.read().decode(CODEC).splitlines()))
    #         task_changes = find_task_changes(curr_xer, prev_xer)
    #         rel_changes = find_relationship_changes(curr_xer, prev_xer)
    #         res_changes = find_resource_changes(curr_xer, prev_xer)
        
    #     print('File Decoded')
    #     return render_template('results.html', tasks=task_changes, rels=rel_changes, rcrs=res_changes)

    return render_template('index.html')


@app.route('/results', methods=['POST'])
def results():
    if (curr := request.files.get('current')) and (prev := request.files.get('previous')):
            curr_xer = Xer(**parse_xer_file(curr.read().decode(CODEC).splitlines()))
            prev_xer = Xer(**parse_xer_file(prev.read().decode(CODEC).splitlines()))
            task_changes = find_task_changes(curr_xer, prev_xer)
            rel_changes = find_relationship_changes(curr_xer, prev_xer)
            res_changes = find_resource_changes(curr_xer, prev_xer)
        
            return render_template('results.html', changes=changes, tasks=task_changes, rels=rel_changes, rcrs=res_changes)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)