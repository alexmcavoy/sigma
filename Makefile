init:
	pip3 install -r requirements.txt

.PHONY:	clean
clean:
	rm -rf results/
	rm -rf **/__pycache__/

.PHONY: test
test:
	python3 -m unittest tests.test_exact
	python3 -m unittest tests.test_simulation

.PHONY: paper_examples
paper_examples:
	python3 -m examples.figure_2 True
	python3 -m examples.figure_si2 True

.PHONY: new_examples
new_examples:
	python3 -m examples.figure_2
	python3 -m examples.figure_si2
