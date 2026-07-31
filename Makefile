# https://github.com/honkit/honkit
setup:
	npm install honkit --save-dev

build:
	npx honkit build .  --log=debug

pdf:
	npx honkit pdf . .pdf

epub:
	npx honkit epub . .epub

serve:
	npx honkit serve
