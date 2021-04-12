# MBS Backend

This is the Backend Portion of the MBS Project. It is written with the Framework, using Python3.9, you will need Python3.9 installed
and must have added the scripts to the Path, in linux, this is handled simply by:

```
sudo apt install python3.9
```

In Windows, I believe the installer takes care of this itself.

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
python3.9 -m venv
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
