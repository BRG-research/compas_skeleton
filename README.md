# compas_skeleton

Topologically generating mesh from a set of lines and allowing interactive editing.

## install requirement

Anaconda/conda and COMPAS >= 0.15.5 is required.

1. Set up a dedicated `conda` environment.

   On Windows.

   ```bash
   conda create -n yourenv python=3.7
   ```

   On Mac, also install Python as a framework (add ``python.app``).

   ```bash
   conda create -n yourenv python=3.7 python.app
   ```

   Activate the environment

   ```bash
   conda activate yourenv
   ```

2. Install COMPAS.

   navigate to the root of the `compas` repo, and do

   ```bash
   pip install -e .
   ```
   more about installing compas: [COMPAS](https://compas-dev.github.io/main/gettingstarted/installation.html)

3. Install Skeleton.

   navigate to the root of the `compas_skeleton` repo, and do

   ```bash
   pip install -e .
   ```

   To verify, open an interactive Python prompt and import the installed packages.

   ```python
   >>> import compas
   >>> import compas_skeleton
   >>> exit()
   ```

4. Install packages for Rhino.

   From the root of `compas_skeleton`, do

   ```bash
   python -m compas_rhino.install -p compas compas_skeleton
   ```