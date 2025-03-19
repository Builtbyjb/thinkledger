ngrok:
	ngrok http --url=admittedly-adequate-scorpion.ngrok-free.app 3000

templ:
	~/go/bin/templ generate

air:
	~/go/bin/air

css:
	./tailwindcss -i ./static/input.css -o ./static/style.css --watch
