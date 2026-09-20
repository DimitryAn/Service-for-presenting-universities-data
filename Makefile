.PHONY: build start

build:
	docker build -t app .

start:
	docker run --rm -p 8501:8501 app:latest