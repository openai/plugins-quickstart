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

    if request.get("listingType") is not None:
       if request.get("listingType") == 'rental': # default is sale
           payload["listingTypes"] = [1, 3]

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
        if len(nbhs) > 0:
            nbhs_ids = get_location_id_from_name(nbhs)
            location_ids.extend(nbhs_ids)
        if len(location_ids) > 0:
            payload["locationIds"] = location_ids

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

        address = l.get("location").get("prettyAddress")

        listingType = "unknown"
        if l.get("detailedInfo") is not None and l["detailedInfo"].get("propertyType") is not None and l["detailedInfo"]["propertyType"].get("masterType") is not None and l["detailedInfo"]["propertyType"]["masterType"].get("GLOBAL") is not None:
            listingType = l["detailedInfo"]["propertyType"]["masterType"]["GLOBAL"]
        
        price = "unknown"
        if l.get("price") is not None and l["price"].get("listed") is not None:
            price = l["price"]["listed"]
            
        bedroomsNumber = "unknown"
        if l.get("size") is not None and l["size"].get("bedrooms") is not None:
            bedroomsNumber = l["size"]["bedrooms"]
        
        totalBathrooms = "unknown"
        if l.get("size") is not None and l["size"].get("totalBathrooms") is not None:
            totalBathrooms = l["size"]["totalBathrooms"]
        
        sqft = "unknown"
        if l.get("size") is not None and l["size"].get("squareFeet") is not None:
            sqft = l["size"]["squareFeet"]
        
        imageUrl = ""
        if l.get("media") is not None and l["media"][0] is not None and l["media"][0].get("thumbnailUrl") is not None:
            imageUrl = l["media"][0]["thumbnailUrl"]
        
        listing = {"Landing URL": landing_url, "info": {"type": listingType, "price": price, "bedrooms": bedroomsNumber, "bathrooms": totalBathrooms, "square feet": sqft, "address": address}, "thumbnail": imageUrl}
        properties.append(listing)

    html = get_html(properties)

    listingType = request.get("listingType")
    if listingType is not None and listingType == 'rental':
        properties.append("More listings : https://www.compass.com/for-rent/")
    else:
        properties.append("More listings : https://www.compass.com/homes-for-sale/")

    return quart.Response(response=html, status=200, content_type="text/html")


def get_html(properties):
    html = "<!DOCTYPE html><html><head><title>Real Estate Listings - Powered by Compass</title><style>.listing {border: 1px solid #ddd;padding: 10px;margin-bottom: 10px;}.listing img {max-width: 165px;max-height: 165px;}</style></head>"
    html = html + "<body>"
    for l in properties:
        landing_url = l["Landing URL"]
        elem = "<div class=\"listing\">"
        elem = elem + "<h2><a href=\"{}\">{}</a></h2>".format(landing_url, l.get("address"))
        elem = elem + "<p>Type: " + l.get("info").get("type") + "</p>"
        elem = elem + "<p>Price: " + l.get("info").get("price") + "</p>"
        elem = elem + "<p>Bedrooms: " + l.get("info").get("bedrooms") + "</p>"
        elem = elem + "<p>Bathrooms: " + l.get("info").get("bathrooms") + "</p>"
        elem = elem + "<p>Square Feet: " + l.get("info").get("square feet") + "</p>"
        elem = elem + "<a href=\"{}\">View Listing</a>".format(l.get("thumbnail"))
        elem = elem + "</div>"
        html = html + elem
    html = html + "</body></html>"
    return html

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


def get_location_id_from_name(locations):
    ids = []
    for location in locations:
        payload = {"q": location, "sources":[2,5,3],"preferredUcGeoIdForRanking":"nyc","tokens":[],"rankerVersion":"v5.0","urlStrategy":2,"enablePrivateSchools":False,"enableSchoolsWithoutBoundaries":False,"infoFields":[2]}
        response = requests.post("https://compass.com/api/v3/omnisuggest/autocomplete", json=payload)
        print(response)
        resp_body = response.json();
        print(resp_body)
        categories = resp_body.get("categories")
        if categories is not None and len(categories) > 0:
            for cat in categories:
                if cat.get("label") is not None and cat.get("label") == "Places" and cat.get("items") is not None:
                    for place in cat.get("items"):
                        if place.get("id") is not None:
                            ids.append(int(place.get("id")))
    print(ids)
    return ids




def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
