# About
Create nice json logs in stdout, easily to agregate and track under distributed systems with a simple automatic header X-Air-Trace-id!

Just pip install, and you are ready to write some nice logs!

## Get Started

```
pip install https://github.com/airfluencers/airlogger.git
```

### Install in Flask
```
from flask import Flask
from airlogger import flask, airutis

app = Flask(__name__)
app.config['APP_NAME'] = 'MY NICE APP'

flask.init_app(app)

@app.route('/')
def hello_world():
    airutis.airlogger.info('some extra logs,included in my trace id stack', {'some': 'serializable meta'})
    return 'Hello, World!'

```

The module is going to log the basic of your requests and responses. If you need to log more information about the requests or responses, like headers or body, register a hook in your app config:

```
def include_more_request_data(request):
    # do the work
    return serializable_dict


def include_more_response_data(response):
    # do the work
    return serializable_dict

app = Flask(__name__)
app.config['APP_NAME'] = 'MY NICE APP'
app.config['AIR_HOOK_LOG_REQUEST'] = include_more_request_data
app.config['AIR_HOOK_LOG_RESPONSE'] = include_more_response_data

```

If you need to track requests across other microsservices, please use the <strong>requests</strong> module.
The header X-Air-Trace-Id will be injected automatically in your next requests.

## TODO:
 - Docs;
 - Integration with Celery;
 - Integration with FastAPI;