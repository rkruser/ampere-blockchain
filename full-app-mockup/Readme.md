# This is a mockup of a full cloud app

Project structure:

Each major app component has its own separate environment setup scripts, git ignores, docker files, docs, etc.

Need to have a "licenses" folder as well for all the software used in the project. Your code license should be placed at the tops of each file.

Python 3.12? with virtual envs
Also, node.js for some of it, and maybe electron


app/
> core
>> docs
>> src
>>> core
> servers
> sites
> Licenses



TODO list:

- Add automated documentation process
- Add environment setup scripts for windows, linux, etc. (python venv, etc)
  (e.g.: "pip install -e ." when run in core directory)