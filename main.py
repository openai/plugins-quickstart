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
    print("Request from ChatGpt is {}".format(request))
    # Default payload
    payload = {"agentSearch": True}

    if request.get("minBedrooms") is not None:
       payload["minBedrooms"]=request.get("minBedrooms")

    if request.get("maxBedrooms") is not None:
       payload["maxBedrooms"]=request.get("maxBedrooms")

    if request.get("minSquareFootage") is not None:
       payload["minSquareFootage"]=request.get("minSquareFootage")

    if request.get("maxSquareFootage") is not None:
       payload["maxSquareFootage"]=request.get("maxSquareFootage")

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

    if request.get("listingType") is not None and request.get("listingType") == 'rental':
        payload["listingTypes"] = [0, 3]
        payload["rentalStatuses"]: [5, 7]
        if request.get("minPrice") is not None:
            payload["minRent"]=request.get("minPrice")
        if request.get("maxPrice") is not None:
            payload["maxRent"]=request.get("maxPrice")
    else:
        payload["listingTypes"] = [2]
        payload["saleStatuses"]: [9, 12]
        if request.get("minPrice") is not None:
            payload["minPrice"]=request.get("minPrice")
        if request.get("maxPrice") is not None:
            payload["maxPrice"]=request.get("maxPrice")


    if request.get("num") is not None:
       payload["num"]=request.get("num")

    if request.get("catsOk") is not None:
       payload["catsOk"]=request.get("catsOk")

    if request.get("dogsOk") is not None:
       payload["dogsOk"]=request.get("dogsOk")


    if request.get("descriptionPhrases") is not None and len(request.get("descriptionPhrases")) > 0:
       payload["descriptionPhrases"]=request.get("descriptionPhrases")

    if request.get("buildingAge") is not None and len(request.get("buildingAge")) > 0:
       payload["buildingAge"]=request.get("buildingAge")


    if request.get("hasFireplace") is not None:
       payload["hasFireplace"]=request.get("hasFireplace")

    if request.get("features") is not None and len(request.get("features")) > 0:
       payload["features"]=request.get("features")

    if request.get("buildingNames") is not None and len(request.get("buildingNames")) > 0:
       payload["buildingNames"]=request.get("buildingNames")

    if request.get("minTotalBathrooms") is not None:
       payload["minTotalBathrooms"]=request.get("minTotalBathrooms")

    if request.get("maxTotalBathrooms") is not None:
       payload["maxTotalBathrooms"]=request.get("maxTotalBathrooms")

    if request.get("minBuildingFloors") is not None:
       payload["minBuildingFloors"]=request.get("minBuildingFloors")

    if request.get("maxBuildingFloors") is not None:
       payload["maxBuildingFloors"]=request.get("maxBuildingFloors")

    if request.get("minDOM") is not None:
       payload["minDOM"]=request.get("minDOM")

    if request.get("maxDOM") is not None:
       payload["maxDOM"]=request.get("maxDOM")

    if request.get("minLastSoldPrice") is not None:
       payload["minLastSoldPrice"]=request.get("minLastSoldPrice")

    if request.get("maxLastSoldPrice") is not None:
       payload["maxLastSoldPrice"]=request.get("maxLastSoldPrice")

    if request.get("minCloseDate") is not None:
       payload["minCloseDate"]=request.get("minCloseDate")

    if request.get("maxCloseDate") is not None:
       payload["maxCloseDate"]=request.get("maxCloseDate")

    if request.get("minOpenHouseDate") is not None:
       payload["minOpenHouseDate"]=request.get("minOpenHouseDate")

    if request.get("maxOpenHouseDate") is not None:
       payload["maxOpenHouseDate"]=request.get("maxOpenHouseDate")

    if request.get("compassListingTypes") is not None and len(request.get("compassListingTypes")) > 0:
       payload["compassListingTypes"]=request.get("compassListingTypes")

    properties=[]

    print("Payload to List listTranslation API is: {}".format(json.dumps(payload)))

    # We make a call to list translation API.
    listingResponse = requests.post("https://compass.com/api/v3/search/listTranslation", json=payload)

    #print(response)
    #print(response.json())

    response = dict();
    status_code = listingResponse.status_code
    if status_code != 200:
        print("Encounterted error with status_code: {} and details: {}. Retry the API.".format(status_code, response.text))
        default_footer(request, response)
        return quart.Response(response=json.dumps(properties), status=200)


    # We will format the response now. In case there is no listing in response then skip this loop.
    for l in listingResponse.json().get("listings", []):
        landing_url = COMPASS_URL + l["canonicalPageLink"]
        print(landing_url)
        print(l.get("location"))
        print(l.get("location").get("prettyAddress"))
        address = "Property"
        if l.get("location") is not None and l.get("location").get("prettyAddress") is not None:
            address = l.get("location").get("prettyAddress")

        listingType = "unknown"
        if l.get("detailedInfo") is not None and l["detailedInfo"].get("propertyType") is not None and l["detailedInfo"]["propertyType"].get("masterType") is not None and l["detailedInfo"]["propertyType"]["masterType"].get("GLOBAL") is not None:
            globalarr = l["detailedInfo"]["propertyType"]["masterType"]["GLOBAL"]
            listingType = ",".join(globalarr)
        
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
        
        listing = {"Landing URL": landing_url, "info": {"address": address, "type": listingType, "price": price, "bedrooms": bedroomsNumber, "bathrooms": totalBathrooms, "square feet": sqft}, "thumbnail": imageUrl}
        properties.append(listing)


    # html = {"htmlContent": get_html(properties)}
    # print(html)

    response["listings"] = properties;
    default_footer(request, response);

    #return quart.Response(response=html, status=200, content_type="text/html")
    return quart.Response(response=json.dumps(response), status=200)

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

def default_footer(request, response):
    listingType = request.get("listingType")
    if listingType is not None and listingType == 'rental':
        response["moreListingsLink"] = "https://www.compass.com/for-rent/"
    else:
        response["moreListingsLink"] = "https://www.compass.com/homes-for-sale/"

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


def get_html(properties):
    html = "<!DOCTYPE html><html><head><title>Real Estate Listings - Powered by Compass</title><style>.listing {border: 1px solid #ddd;padding: 10px;margin-bottom: 10px;}.listing img {max-width: 165px;max-height: 165px;}</style></head>"
    html = html + "<body>"
    for l in properties:
        landing_url = l["Landing URL"]
        elem = "<div class=\"listing\">"
        elem = elem + "<p><h2><a href=\"{url}\">{addr}</a></h2></p>".format(url=landing_url, addr=l.get("info").get("address"))
        elem = elem + "<p>Type: " + l.get("info").get("type") + "</p>"
        elem = elem + "<p>Price: " + str(l.get("info").get("price")) + "</p>"
        elem = elem + "<p>Bedrooms: " + str(l.get("info").get("bedrooms")) + "</p>"
        elem = elem + "<p>Bathrooms: " + str(l.get("info").get("bathrooms")) + "</p>"
        elem = elem + "<p>Square Feet: " + str(l.get("info").get("square feet")) + "</p>"
        elem = elem + "<a href=\"{}\">View Listing</a>".format(l.get("thumbnail"))
        elem = elem + "</div>"
        html = html + elem
    html = html + "</body></html>"
    return html


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
