from flask import Flask, request, jsonify
from openfga_sdk import ClientConfiguration, OpenFgaClient
from openfga_sdk.client.models import ClientTuple, ClientWriteRequest, ClientCheckRequest
import asyncio
import uuid

app = Flask(__name__)

FGA_API_URL = 'http://localhost:8080'  # Replace with your OpenFGA API URL
FGA_STORE_ID = '01JWKXM6H4KWD0TAZC9FSQYCSN'  # Replace with your OpenFGA store ID

# Create a user management API
@app.route('/test', methods=['GET'])
def test_connection():
    async def main():
        configuration = ClientConfiguration(
            api_url=FGA_API_URL,  # required
            store_id=FGA_STORE_ID,  # optional, not needed when calling `CreateStore` or `ListStores`
            # authorization_model_id=FGA_MODEL_ID,  # Optional, can be overridden per request
        )
        # Enter a context with an instance of the OpenFgaClient
        async with OpenFgaClient(configuration) as fga_client:
            api_response = await fga_client.read_authorization_models()
            await fga_client.close()
            return api_response
    result = asyncio.run(main())
    print(result)
    return {'status': 'success'}, 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user_id = str(uuid.uuid4())
    user_object = f"user:{user_id}"

    async def main():
        configuration = ClientConfiguration(
            api_url=FGA_API_URL,
            store_id=FGA_STORE_ID,
        )
        async with OpenFgaClient(configuration) as fga_client:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user="user:" + user_id,
                        relation="viewer",
                        object="doc:1",
                    ),
                ]
            )
            response = await fga_client.write(body)
            return {"id": user_id, "name": data.get("name"), "email": data.get("email")}
    result = asyncio.run(main())
    return jsonify(result), 201

@app.route('/check', methods=['POST'])
def check_relationship():
    data = request.json
    user_id = data.get("user_id")
    relation = data.get("relation")
    object_id = data.get("object")

    if not user_id or not relation or not object_id:
        return jsonify({"error": "Missing user_id, relation, or object"}), 400

    async def main():
        configuration = ClientConfiguration(
            api_url=FGA_API_URL,
            store_id=FGA_STORE_ID,
        )

        print(f"Checking relationship for user: {user_id}, relation: {relation}, object: {object_id}")

        async with OpenFgaClient(configuration) as fga_client:
            check_body = ClientCheckRequest(
                user="user:" + user_id,
                relation=relation,
                object=object_id,
                context=dict(
                    ViewCount=100
                ),
            )
            response = await fga_client.check(check_body)
            
            return {"allowed": response.allowed}
    result = asyncio.run(main())
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)

