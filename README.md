# Thesis Radloff Ba



## Installation

A Makefile is provided for convenience. The commands

```
make virtualenv
make frontend
```

will install all required backend and frontend dependencies.
A running instance of postgresql with access as defined in fmexp/{config,config2}.py is required.
Installed versions of python, python-virtualenv, nodejs and yarn are expected.

## Websites

The two different frontends can be launched by running the following commands:
```
make fmexp-layout1-frontend (or fmexp-layout2-frontend)
make uwsgi-run (or uwsgi-run-fmexp2)
```

## Experiment Data

The live experiments data can be found in the data folder as compressed database dumps. They can be loaded by running:

```
./load_db.sh data/<file> <database_name>
```

## Tools

The Python scripts bot_runner.py (running automated bots on running website), classify.py (train and test ML model), viz_runner.py (visualizations) are provided for convenience.
