web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT}
worker: python3 -m app.stream_receiver --host localhost --port ${PORT}
