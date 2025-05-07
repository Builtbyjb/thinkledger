ngrok:
	ngrok http --url=admittedly-adequate-scorpion.ngrok-free.app 3000

dev:
	uvicorn main:app --host 0.0.0.0 --port 3000 --reload

minify:
	npm run minify

css:
	npx tailwindcss -i ./web/static/input.css -o ./web/static/style.css --minify

celery:
	celery -A core.celery worker --loglevel=info
