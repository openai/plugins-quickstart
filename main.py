# json 模块，用于 json 数据的序列化和反序列化
import json
# os 模块，用于获取第三方天气平台 API_KEY
import os
# requests 模块，用于访问第三方天气平台
import requests
# quart 模块，用于搭建异步 Web 服务
import quart
# quart_cors 模块，用于解决跨域问题
import quart_cors
# 从 quart 模块导入 request 对象，用于处理 HTTP 请求
from quart import request

# 实例化一个支持 CORS 的 Quart 应用实例，允许来自 https://chat.openai.com 的跨域请求
app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_citycode(city):
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "city": city,
        "key": WEATHER_API_KEY,
        "address": city
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        # 从 response 中获取 citycode
        data = response.json()
        citycode = data["geocodes"][0]["adcode"]
        print(f"{city}: {citycode}")
        return citycode
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during GET request: {e}")
        return None

def _get_current_weather(city):
    citycode = get_citycode(city)

    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "city": citycode,
        "key": WEATHER_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # 从 response 中获取天气信息
        w = data["lives"][0]
        weather = f"今天{w['province']}{w['city']}天气{w['weather']}, 温度{w['temperature']}°C, 湿度{w['humidity']}%，风向{w['winddirection']}, 风力{w['windpower']}级。"
        return weather
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during GET request: {e}")
        return None
    
def _get_n_day_weather_forecast(city, num_days):
    if num_days > 3 or num_days < 0:
        return "最多查询未来3天的预报"
    
    citycode = get_citycode(city)

    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "city": citycode,
        "key": WEATHER_API_KEY,
        "extensions": "all"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # 从 response 中获取天气信息
        forecast = data["forecasts"][0]["casts"][num_days]
        date = forecast["date"]
        day_weather = forecast["dayweather"]
        night_weather = forecast["nightweather"]
        day_temp = forecast["daytemp"]
        night_temp = forecast["nighttemp"]
        day_wind = forecast["daywind"]
        night_wind = forecast["nightwind"]
        day_power = forecast["daypower"]
        night_power = forecast["nightpower"]

        weather = f"{date}，白天天气{day_weather}，夜晚天气{night_weather}，白天温度{day_temp}°C，夜晚温度{night_temp}°C，白天风向{day_wind}，夜晚风向{night_wind}，白天风力{day_power}级，夜晚风力{night_power}级。"
        return weather
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during GET request: {e}")
        return None

# 定义一个路由处理器，处理 GET 请求，路由为 "/weather/current"
@app.post("/weather/current")
async def get_current_weather():
    # 从请求参数中获取城市名
    city = request.args.get("city")
    response = _get_current_weather(city)
    # 创建并返回一个 Quart 响应对象，状态码为 200，响应体为 response 的 json 形式
    return quart.Response(json.dumps(response), status=200)

# 定义一个路由处理器，处理 GET 请求，路由为 "/weather/forecast"
@app.get("/weather/forecast")
async def get_n_day_weather_forecast():
    # 从请求参数中获取城市名和预报天数
    city = request.args.get("city")
    num_days = int(request.args.get("num_days"))
    response = _get_n_day_weather_forecast(city, num_days)
    # 创建并返回一个 Quart 响应对象，状态码为 200，响应体为 response 的 json 形式
    return quart.Response(json.dumps(response), status=200)

# 定义一个路由处理器，处理 GET 请求，路由为 "/logo.png"
@app.get("/logo.png")
async def plugin_logo():
    # 文件名为 'logo.png'
    filename = 'logo.png'
    # 使用 quart.send_file 方法发送文件，并指定 MIME 类型为 'image/png'
    return quart.send_file(filename, mimetype='image/png')

# 定义一个路由处理器，处理 GET 请求，路由为 "/.well-known/ai-plugin.json"
@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    # 从请求头中获取主机名
    host = request.headers['Host']
    # 打开并读取 ai-plugin.json 文件
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
    # 返回一个 Quart 响应对象，响应体为 text，MIME 类型为 "text/json"
    return quart.Response(text, mimetype="text/json")

# 定义一个路由处理器，处理 GET 请求，路由为 "/openapi.yaml"
@app.get("/openapi.yaml")
async def openapi_spec():
    # 从请求头中获取主机名
    host = request.headers['Host']
    # 打开并读取 openapi.yaml 文件
    with open("openapi.yaml") as f:
        text = f.read()
    # 返回一个 Quart 响应对象，响应体为 text，MIME 类型为 "text/ymal"
    return quart.Response(text, mimetype="text/yaml")

# 定义 main 函数，运行 Quart 应用
def main():
    # 启动 Quart 服务器，开启 debug 模式，监听所有 IP 地址，端口为 5003
    app.run(debug=True, host="0.0.0.0", port=5003)

def test():
    city = "上海"
    num_days = 2
    weather_info = _get_current_weather(city)
    print(weather_info)

    weather_forecast = _get_n_day_weather_forecast(city, num_days)
    print(weather_forecast)

# 如果该文件是直接运行的，而不是作为模块导入的，则调用 main 函数
if __name__ == "__main__":
    test()
    main()
