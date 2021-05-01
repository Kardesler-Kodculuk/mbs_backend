# MBS Backend

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![build](https://github.com/Kardesler-Kodculuk/mbs_backend/actions/workflows/python-app.yml/badge.svg)](https://github.com/Kardesler-Kodculuk/mbs_backend/actions/workflows/python-app.yml)
[![Read Documentation](https://img.shields.io/badge/Documentation-API%20Reference-informational?logo=flask)](https://mbsbackend.docs.apiary.io/#)



This is the Backend Portion of the MBS Project. It is written with the Framework, using Python3.9, you will need Python3.9 installed
and must have added the scripts to the Path, in linux, this is handled simply by:

```
sudo apt install python3.7
```

In Windows, I believe the installer takes care of this itself. If you have installed Python anytime
in the last 2-3 years, it is likely you already have at least Python 3.7, and you can
continue the installation.

## Installation

Clone the git repository using


```
git clone https://github.com/Kardesler-Kodculuk/mbs_backend.git
```

This will clone the repository to a directory called mbs_backend.

or, alternatively clone it with the GitHub Desktop Client.

Once inside this directory, you will need to set up your development environment, doing this is extremely simple.

### Using Virtual Environments (the Better Way, Optional)

Run the following command:

```
python -m venv venv
```

This will generate a virtual environment in this directory, a sandboxed python installation, you can activate this environment by running:

```
source venv/bin/activate
```

This works in Linux with bash. In Windows, go for:

```
venv\Scripts\activate.bat
```

### Installing Python modules

Simply run `pip install -r requirements.txt`.

## Running the Backend

To run the backend for everyday testing, you simply need to run:

```
flask run
```

In your directory. (Don't forget to activate your virtual environment if you have installed it!) As the project continues, the run instructions may change.

### Features to Use

Since we are using Python 3.7+, you can safely use any feature of Python that was introduced
before and up to Python 3.7, this includes `dataclasses` package and `Typing` package, but
excludes type hinting with primitive types and the walrus operator.
