import json
import os
import requests
import quart
import quart_cors
import gis as gis
from quart import request


app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}
COMPASS_API_KEY = os.environ.get("COMPASS_API_KEY")
COMPASS_URL="https://www.compass.com"
assert COMPASS_API_KEY is not None

@app.post("/query/<string:username>")
async def query(username):
    request = await quart.request.get_json(force=True)
    print("request is {}".format(request))
    # queryResult1 = QueryResult(id="1262365637693399233",
    #         text="217-west-57th-street-unit-107-manhattan-ny-10019",
    #         url="https://www.compass.com/app/listing/217-west-57th-street-unit-107-manhattan-ny-10019/1262365637693399233",
    #         description="217-west-57th-street-unit-107-manhattan-ny-10019",
    #         score=1.0)
    # queryResult2 = QueryResult(id="1200211444829995265",
    #     text="217-west-57th-street-unit-ph-manhattan-ny-10019",
    #     url="https://www.compass.com/app/listing/217-west-57th-street-unit-ph-manhattan-ny-10019/1200211444829995265",
    #     description="217-west-57th-street-unit-ph-manhattan-ny-10019",
    #     score=2.0)
    # queryResult3 = QueryResult(id="1313115650069090185",
    #     text="432-park-avenue-unit-ph96-manhattan-ny-10022",
    #     url="https://www.compass.com/app/listing/432-park-avenue-unit-ph96-manhattan-ny-10022/1313115650069090185",
    #     description="432-park-avenue-unit-ph96-manhattan-ny-10022",
    #     score=1.0)
    # queryResult4 = QueryResult(id="1138977360987454057",
    #     text="central-west-57th-street-manhattan-ny-10019",
    #     url="https://www.compass.com/app/listing/central-west-57th-street-manhattan-ny-10019/1138977360987454057",
    #     description="central-west-57th-street-manhattan-ny-10019",
    #     score=1.0)
    payload = {"agentSearch": True,"listingTypes": [2]}
    payload["saleStatuses"] = [9, 12]

    if request.get("minPrice") is not None:
       payload["minPrice"]=request.get("minPrice")

    if request.get("maxPrice") is not None:
       payload["maxPrice"]=request.get("maxPrice")

    if request.get("minBedrooms") is not None:
       payload["minBedrooms"]=request.get("minBedrooms")

    if request.get("maxBedrooms") is not None:
       payload["maxBedrooms"]=request.get("maxBedrooms")

    if request.get("minSquareFootage") is not None:
       payload["minSquareFootage"]=request.get("minSquareFootage")

    if request.get("maxSquareFootage") is not None:
       payload["maxSquareFootage"]=request.get("maxSquareFootage")

    if request.get("num") is not None:
       payload["num"]=request.get("num")

    if request.get("locations") is not None:
        locations = request.get("locations")
        state = "NY"
        location_ids = []
        nbhs = []
        for location in locations:
            key = location.lower() + "-" + state
            if gis.locations.get(key) is not None:
                location_ids.append(gis.locations.get(key))
            else:
                nbhs.append(location.lower())
        if len(location_ids) > 0:
            payload["locationIds"] = location_ids
        else:
            payload["neighborhoods"] = nbhs

    properties=["https://www.compass.com/app/listing/217-west-57th-street-unit-107-manhattan-ny-10019/1262365637693399233",
                "https://www.compass.com/app/listing/217-west-57th-street-unit-ph-manhattan-ny-10019/1200211444829995265",
                "https://www.compass.com/app/listing/432-park-avenue-unit-ph96-manhattan-ny-10022/1313115650069090185",
                "https://www.compass.com/app/listing/central-west-57th-street-manhattan-ny-10019/1138977360987454057"]
    properties=[]
    print(payload)
    response = requests.post("https://compass.com/api/v3/search/listTranslation", json=payload, headers=get_auth_header())
    print(response)
    print(response.json())
    for l in response.json()["listings"]:
        landing_url = COMPASS_URL + l["canonicalPageLink"]
        print(landing_url)
        properties.append(landing_url)
    return quart.Response(response=json.dumps(properties), status=200)


@app.post("/todos/<string:username>")
async def add_todo(username):
    request = await quart.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request["todo"])
    return quart.Response(response='OK', status=200)

@app.get("/todos/<string:username>")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)

@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request = await quart.request.get_json(force=True)
    todo_idx = request["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response='OK', status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def get_auth_header():
    return {"Authorization": "Bearer {}".format(COMPASS_API_KEY)}

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
