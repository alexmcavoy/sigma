# sigma

Supporting code for the paper "Evaluating the structure coefficient theorem of evolutionary game theory" by Alex McAvoy and John Wakeley, available at [https://arxiv.org/abs/2010.14566](https://arxiv.org/abs/2010.14566).

## Instructions

Dependencies can be installed by typing

	make init
	
To reproduce the figures in the paper, with the same structures, use


	python3 -m examples.figure_2 True
	python3 -m examples.figure_si2 True
	python3 -m examples.figure_si3
	
or just

	make paper_examples
	
Note that `figure_si3.py` uses data produced by `figure_si2.py`, which, by default, is the same data depicted in the paper. Otherwise, to generate new figures like those in the paper (but with randomly-generated graphs), use

	python3 -m examples.figure_2
	python3 -m examples.figure_si2
	
or just

	make new_examples
	
Parameters may be adjusted as needed in `examples/figure_2.py` and `examples/figure_si2.py`. Note that Figure SI1 can be generated using the code for Figure 2 with `selection_intensity = 0.05` replaced by `selection_intensity = 0.01`.
	
## Contact information

Please direct questions to Alex McAvoy (`alexmcavoy@gmail.com`).
