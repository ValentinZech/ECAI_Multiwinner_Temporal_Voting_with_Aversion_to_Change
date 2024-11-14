# ECAI-2024: Multiwinner Temporal Voting with Aversion to Change

This repository contains the code for the experiments of the following paper:

Valentin Zech, Niclas Boehmer, Edith Elkind, and Nicholas Teh. “Multiwinner Temporal Voting with Aversion to Change”. In: Proceedings of the 27th European Conference on Artificial Intelligence (ECAI). 2024. https://ebooks.iospress.nl/doi/10.3233/FAIA240870

The full verion (including the appendix) can be found on arXiv: https://arxiv.org/abs/2408.11017


## Hardware

The experiments were run using Python 3.11.6 on a machine running macOS Ventura 13.6.6 with a 2.3 GHz 8-core Intel Core i9 processor and 32GB RAM. All used packages with their version numbers are listed in `/resilient_elections/source/requirements.txt`. Running all experiments took around 30 hours.

## Raw Data

The project already contains the raw data in the form of json files, as well as all plots shown in the paper. The raw data can be found in:

```/resilient_elections/jsons```

And the graphs can be found in:

```/resilient_elections/graphs```

## Recreating the Experiments

However, to rerun all experiments from scratch, first navigate to the `/resilient_elections/source` folder, and install the required packages with:

```pip3 install requirements.txt```

Next, clean out the existing raw data and graphs with:

```python3 clean.py```

Further, we need to compile the Cython code of this project as follows:

```python3 setup.py build_ext --inplace```

Finally, run all experiments with:

```python3 run_experiments.py```

And create the new graphs with:

```python3 generate_graphs.py```

Note that we monkey-patch the `abcvoting` library in two ways (both patches can be found near the top of the `/resilient_elections/source/run_experiments.py` file):
1. First, we exchange the method `abcvoting.abcrules.compute_seq_thiele_method` with our own version which additionally returns the order in which the committee members were added by a sequential Thiele rule. This modification is essential for experiment 3.
2. Second, we patched the method `abcvoting.scores.marginal_thiele_scores_add` with a more performant Cython version. All experiments can be run without this patch, but take around 6 times as long. For this, comment out the relevant lines in `/resilient_elections/source/run_experiments.py`, and follow the above steps, skipping the command `python3 setup.py build_ext --inplace`.
