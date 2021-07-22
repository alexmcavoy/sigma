# sigma

Supporting code for the paper "Evaluating the structure coefficient theorem of evolutionary game theory" by Alex McAvoy and John Wakeley, available at [https://arxiv.org/abs/2010.14566](https://arxiv.org/abs/2010.14566).

## Instructions

Dependencies can be installed by typing

	make init
	
To reproduce the figures in the main text, with the same structures, use


	python3 -m examples.figure_1 True
	python3 -m examples.figure_2 True
	
or just

	make paper_examples
	
Otherwise, to generate new figures like those in the main text (but with randomly-generated graphs), use

	python3 -m examples.figure_1
	python3 -m examples.figure_2
	
or just

	make new_examples
	
Parameters may be adjusted as needed in `examples/figure_1.py` and `examples/figure_2.py`.
	
## Contact information

Please direct questions to Alex McAvoy (`alexmcavoy@gmail.com`).
