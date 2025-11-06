FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PORT=8080

WORKDIR /app

RUN apt-get update \
	&& apt-get install --no-install-recommends -y build-essential curl \
	&& curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.dev.txt ./
RUN pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt \
	&& pip install --no-cache-dir -r requirements.dev.txt

COPY app ./app
COPY scripts ./scripts
COPY models ./models
EXPOSE 8080

CMD ["bash", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]