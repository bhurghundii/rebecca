from flask import Flask, request, jsonify

app = Flask(__name__)
items = {}

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(list(items.values()))

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = items.get(item_id)
    if item:
        return jsonify(item)
    return jsonify({'error': 'Item not found'}), 404

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    item_id = len(items) + 1
    item = {'id': item_id, 'name': data.get('name')}
    items[item_id] = item
    return jsonify(item), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    item = items.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    item['name'] = data.get('name', item['name'])
    items[item_id] = item
    return jsonify(item)

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if item_id in items:
        del items[item_id]
        return jsonify({'result': 'Item deleted'})
    return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

