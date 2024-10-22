#Makefile

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
		
format:
	black src/*.py tests/*.py
	
lint:
	pylint --disable=R,C src/*.py tests/*.py

test:
	pytest -vv tests/ 

all: install lint test