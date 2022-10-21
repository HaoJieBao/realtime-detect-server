# Backend Server for Realtime Detect

## Production

```
docker-compose up
```

## Development

### Install dependencies

- Using [`pdm`](https://pdm.fming.dev/latest/)

  ```sh
  pdm install
  ```

- Using `pip`

  ```sh
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

### Active Redis

```sh
docker-compose -f db/docker-compose.dev.yml up
```

### Start Redis Queue worker

- Using `pdm`

  ```sh
  pdm run worker
  ```

- Using `pip`

  ```sh
  source .venv/bin/activate
  rq worker --with-scheduler
  ```
