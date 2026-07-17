MAIN = main
BIB  = bachelors.bib

LATEXMK = latexmk
FLAGS   = -pdf -lualatex -shell-escape -use-make

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex $(BIB)
	$(LATEXMK) $(FLAGS) $(MAIN).tex

clean:
	$(LATEXMK) -c
	rm -f *.bbl *.run.xml *.bcf

distclean:
	$(LATEXMK) -C
	rm -f *.bbl *.run.xml *.bcf

watch:
	$(LATEXMK) $(FLAGS) -pvc $(MAIN).tex

.PHONY: all clean distclean watch