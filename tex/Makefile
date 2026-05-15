# Name of your main LaTeX file without the extension
MAIN = main
BIB  = bachelors.bib

# Commands
LATEXMK = latexmk
FLAGS   = -pdf -lualatex -shell-escape -use-make

# Default target
all: $(MAIN).pdf

# Core build rule
$(MAIN).pdf: $(MAIN).tex $(BIB)
	$(LATEXMK) $(FLAGS) $(MAIN).tex

# Clean target: removes intermediate files but keeps the PDF
clean:
	$(LATEXMK) -c
	rm -f *.bbl *.run.xml *.bcf

# Full clean: removes intermediate files AND the PDF
distclean:
	$(LATEXMK) -C
	rm -f *.bbl *.run.xml *.bcf

# Watch mode: automatically recompiles when you save a file
watch:
	$(LATEXMK) $(FLAGS) -pvc $(MAIN).tex

.PHONY: all clean distclean watch