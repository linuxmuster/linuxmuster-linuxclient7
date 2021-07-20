.PHONY: help deb docs

help:
	@echo "Options:"
	@echo "  deb    Build debian package"
	@echo "  docs   Build Sphinx documentation"
	@echo "  clean  Remove built files"

deb:
	dpkg-buildpackage -rfakeroot -tc -sa -us -uc -I".directory" -I".git" -I"buildpackage.sh"

docs:
	cd docs && sphinx-build . ../public

clean:
	rm -r public