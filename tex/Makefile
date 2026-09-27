MAIN 	= main
DRAFT 	= draft
BIB  	= bachelors.bib

LATEXMK = latexmk
FLAGS   = -pdf -lualatex -shell-escape -use-make

all: full

draft:
	$(LATEXMK) -pdf -jobname=$(DRAFT) $(DRAFT).tex

full:
	$(LATEXMK) -pdf -jobname=$(MAIN) $(MAIN).tex

clean:
	$(LATEXMK) -c
	rm -f *.bbl *.run.xml *.bcf

distclean:
	$(LATEXMK) -C
	rm -f *.bbl *.run.xml *.bcf

watch:
	$(LATEXMK) $(FLAGS) -pvc $(MAIN).tex

.PHONY: all clean distclean watch