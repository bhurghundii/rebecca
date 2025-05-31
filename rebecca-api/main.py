from flask import Flask, request, jsonify
from openfga_sdk import ClientConfiguration, OpenFgaClient
import asyncio

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

if __name__ == '__main__':
    app.run(debug=True)

