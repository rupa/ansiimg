all: readme | demo.ansi

readme:
	./ansi.py --help > README

demo.ansi:
	./ansi.py fry-money.jpg --width 80 -p 16 -p 216 -p 256 -p bw -p greyscale > demo.ansi

clean:
	rm README
	rm demo.ansi

.PHONY: all clean
