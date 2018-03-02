# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXAUTO    = sphinx-autogen
SPHINXPROJ    = pcdsdaq
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: help clean html

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"

clean:
	-rm -rf $(BUILDDIR)
	-rm -rf $(SOURCEDIR)/generated

html:
	$(SPHINXAUTO) -o $(SOURCEDIR)/generated $(SOURCEDIR)/*.rst
	$(SPHINXBUILD) -b html $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."
