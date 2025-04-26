ngrok:
	ngrok http --url=admittedly-adequate-scorpion.ngrok-free.app 3000

dev:
	uvicorn main:app --host 0.0.0.0 --port 3000 --reload

minify:
	npm run minify

css:
	npx tailwindcss -i ./static/input.css -o ./static/style.css --minify

push:
	npx @tailwindcss/cli -i ./static/input.css -o ./static/style.css --minify \
	&& npm run minify