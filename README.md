# Simulation

## Disclaimer

<!-- TODO: Update this maybe -->
This is still in the **very *very* early stages of undoneness**. Hence, the code design itself is *extremely* messy and is ***not*** representative of what the final/future iterations of the program will look like.
Nonetheless, we have still uploaded this as a proof of concept/proof of work done on this topic. Do follow us on Instagram [@bozotics](https://www.instagram.com/bozotics/) to stay updated with our developmental progress.

## Setup

1. Ensure python is working (tested with python 3.8, should work with python 3.6 and above)
2. Download/Clone this repository and `cd` into the repository
3. Create and activate a virtual environment (`python3 -m venv venv` then `source venv/bin/activate` or something similar, see: https://docs.python.org/3/tutorial/venv.html)
4. Install packages from requirements.txt (`pip install -r requirements.txt`)

The [Arcade](https://arcade.academy/) library is used for drawing of the sprites in the program, while [Pymunk](http://www.pymunk.org/en/latest/) is the 2D physics library.

## Programming

To program robots in the simulation, edit the functions `attack`, `defend`, `o_attack`, and `o_defend` in the `program.py` file.
While most of code is documented through comments and docstrings, source code can be found in `tools.py` (for classes and functions used) and `simulation.py` (the actual simulation code, may not be that useful except for a few methods in `SimWin` like `line`, `dribble`, and `kick`).

An example is included in the `example.py` file, with the actual programs being split into files in the `/examples` folder.

## Running

To run the simulation, the `main` function in `simulation.py` is called with the config information and programs as arguments. This is done in the `program.py` (and `example.py`) file, so simply run those files to launch the simulation.
