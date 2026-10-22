.PHONY: build start

build:
	docker build -t app .

start:
	docker run --rm -p 80:8501 app:latest