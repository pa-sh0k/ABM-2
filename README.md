## Installation

Set up and acitvate **Conda Environment** with package requirements:
```
conda create --name 2D-ABM --file requirements.txt python=3.10.12
conda activate 2D-ABM
```
Install **Jupyter Notebook** and add the environment as Jupyter kernel:
```
conda install jupyter
conda install -c anaconda ipykernel
python -m ipykernel install --user --name=2D-ABM
```
