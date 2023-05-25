
# aws-lambda-pytest-moto-async

## Folder Structure

Here is how I structured my lambda project in python, I use monorepo that makes context grouping. (This works great for small teams, a post on monorepo vs multirepo will follow shortly).


* AWS : This folder is responsible for having AWS SAM cloud formation and configuration information. When we build our CI/CD process on services like GitLab, Bitbucket or Github, the configuration files contained here help us to load our infrastructure for any aws region with different configurations.


* BUILD : The build folder is where we have our scripts to run our unit tests, cyclomatic complexity tests, and create configurations to deploy our cloudformation. I like this folder because everything related to the scripts that will run in our deploy mat is here.


* SRC: Last but not least is the src folder where we put our lambda, example test events that we will use both for development and later for deployment.


* SETUP.CFG: This file is also very relevant since it contains all the pytest rules that will be loaded, as shown below.


## Documentation

[Documentation](https://medium.com/@sant1/creating-async-unit-tests-with-python-aws-lambda-pytest-moto-part-1-bd93f6ed74f9)
