---
layout: post
title: A free, Python proxy server on AWS lambda
comments: true
---

Amazon Web Services' (AWS) serverless offering, [AWS Lambda](https://aws.amazon.com/lambda/), is part of their "always free tier". What that means is you get 1 million requests per month, or 3.2 million seconds of compute time per month, for free. Forever. 

You can deploy a simple flask app on lambda, which will make your web requests for you from within AWS. The deployment is seamlessly handled by [Zappa](https://github.com/Miserlou/Zappa), a framework for managing serverless Python applications.

<p align="center">
    <img src="{{ site.baseurl }}{% link images/free-proxy-server/architecture.png %}" height="400px">
</p>

## How does it work?

We start with a simple [Flask](https://palletsprojects.com/p/flask/) application, `proxy.py`, which takes in a POST request containing a URL. The app will make a GET request to that URL, and return the pickled response object.

```python
import io
import pickle

from flask import Flask, request, send_file
import requests

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    data = request.form
    r = requests.get(data["url"])
    pickled_response = pickle.dumps(r)
    return send_file(io.BytesIO(pickled_response), mimetype="application/octet-stream")


if __name__ == "__main__":
    app.run(debug=True)
```

Instead of your process making requests directly to a URL, it now does so through the proxy server URL.

```python
import pickle
import requests

proxy_response = requests.post(
    '<proxy_server_url', # Your proxy server URL
    data={'url': 'https://ianwhitestone.work'} # URL you want to request
)
response = pickle.loads(proxy_response.content)
```

You can now interact with the requests response object as you would normally:

```python
>>> response
<Response [200]>
>>> response.text
'<!DOCTYPE html>\n<html>\n  <head>\n    <title>Ian Whitestone</title>\n\n ...
...
```

Here's a demo of running the proxy server locally, with `python proxy.py`:

<img src="{{ site.baseurl }}{% link images/free-proxy-server/local_demo.gif %}">

Now of course, we don't want to run this thing locally. That defeats the whole purpose of a proxy. To get this app running on the cloud, we leverage the Python serverless framework, [Zappa](https://github.com/Miserlou/Zappa). Zappa takes a config file, `zappa_settings.json`, and automatically creates lambda functions which serve your Flask application.

Here, I tell Zappa to create two lambda functions, one in the `us-east-1` region and another in the `us-west-1` region.

```json
{
    "proxy_us_east_1": {
        "app_function": "proxy.app",
        "aws_region": "us-east-1",
        "project_name": "proxy",
        "runtime": "python3.8"
    },
    "proxy_us_west_1": {
        "app_function": "proxy.app",
        "aws_region": "us-west-1",
        "project_name": "proxy",
        "runtime": "python3.8"
    }
}
```

The deployment is a simple Zappa cli call, `zappa deploy --all`. As you can see, it takes just over a minute to deploy two lambda functions and all the associated AWS configurations (API gateway, IAM roles, etc..)

<img src="{{ site.baseurl }}{% link images/free-proxy-server/zappa_deploy_all.png %}">

Now, we can grab the URL for the proxy we want to use and make a post request against it:

<img src="{{ site.baseurl }}{% link images/free-proxy-server/deployed_demo.gif %}">

If you're interested in trying this out, head over to this [repo](https://github.com/ian-whitestone/python-proxy-server) for full setup instructions.