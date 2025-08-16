from setuptools import setup
from Cython.Build import cythonize

setup(
    name="plagiarism_cython",
    ext_modules=cythonize(
        ["similarity.pyx"],
        compiler_directives={
            'language_level': '3'
        }
    ),
    zip_safe=False,
)
