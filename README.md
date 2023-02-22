# Fast API
```bash
python -m uvicorn main:app --reload

```

[Interactive API docs](http://127.0.0.1:8000/docs)

[Alternative API docs](http://127.0.0.1:8000/redoc)

# Setup
```bash 
python -m pip install --user virtualenv
python -m virtualenv venv
source venv/scripts/activate
pip install pymongo
pip3 install starlette
pip3 install uvicorn
pip install pydantic
pip install fastapi
pip install uvicorn
pip install "uvicorn[standard]"
pip install "strawberry-graphql[debug-server]"
pip install requests
pip install datetime
pip install odmantic
```

# Strawberry Demo
```bash
python -m strawberry server strawberryApp
```

[Server](http://localhost:8000/graphql)