all: readme | demo.ansi

readme:
	ansiimg/ansi.py --help > README

demo.ansi:
	ansiimg/ansi.py memes/fry_shut_up.jpg --width 80 -p 16 -p 216 -p 256 -p bw -p greyscale -t "SHUT UP" > demo.ansi

clean:
	rm README
	rm demo.ansi

.PHONY: all clean
