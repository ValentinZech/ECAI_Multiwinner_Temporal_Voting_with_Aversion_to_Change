from Cython.Build import cythonize
from setuptools import setup

setup(
    ext_modules=cythonize("marginal_thiele_scores_cython.pyx")
)
