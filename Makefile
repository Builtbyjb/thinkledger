ngrok:
	ngrok http --url=admittedly-adequate-scorpion.ngrok-free.app 3000

air:
	~/go/bin/air

push:
	~/go/bin/templ generate \
	&& ./tailwindcss -i ./static/input.css -o ./static/style.css --minify \
	&& npm run minify
