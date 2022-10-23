web: gunicorn main:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --preload
worker: python3 -m app.stream_receiver
