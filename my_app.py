#!flask/bin/python
from flask import Flask, jsonify

app = Flask(__name__)

tasks = [

{'id': 1,'titulo': u'EC2 - T2 Large','descricao': u'MEM:64MB PROC:24Vcpu HD:500GB NFS','done': False},
{'id': 2,'titulo': u'EC2 - T2 Medium','descricao':u'MEM:32MB PROC:12Vcpu HD:250GB NFS','done': False}

]

@app.route('/todo/api/v1/tasks/', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


from flask import abort
@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


from flask import make_response
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


from flask import request
@app.route('/todo/api/v1/tasks/', methods=['POST'])
def create_task():
    if not request.json or not 'titulo' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'titulo': request.json['titulo'],
        'descricao': request.json.get('descricao', ""),
        'done': False
   	   }
    tasks.append(task)
    return jsonify({'task': task}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    app.run(debug=True)
