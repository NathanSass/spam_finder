# spam_finder



### to get started



create an .env file with:

```
HF_TOKEN=your_api_key
OPENAI_API_KEY=your_api_key
SERPER_API_KEY=your_api_key
OPENAI_MODEL_NAME=gpt-3.5-turbo
```

Install dependencies from pyproject.toml
```
pip install . 
```

Run the app
```
pip install fastapi
pip install uvicorn
uvicorn app.main:app --reload # runs the server
```

#### Run with docker

Download [docker desktop](https://www.docker.com/products/docker-desktop/)

```
docker --build-arg ENVIRONMENT=development build -t myimage .
docker run -d --name mycontainer -p 80:80 myimage
```

access at `http://0.0.0.0:80/test`

#### Deployment instructions

[here](https://fly.io/docs/languages-and-frameworks/dockerfile/)

Add secrets
`fly secrets import <.env`

`fly deploy`

[monitor](https://fly.io/apps/spam-finder/monitoring)
