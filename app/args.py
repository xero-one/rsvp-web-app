import argparse


# This module is used to accept arguments from the cli and process them. 
parser = argparse.ArgumentParser(prog = "my-portfolio cli", description = "The file used to run all facets of the application.")
parser.add_argument(
    "-env", 
    "--env", 
    type = str,
    default = "development",
    choices = ["development", "production"],
    dest = "env", # this sets the name of the Namespace variable so you can access the values of the argument i.e. args.env
    help = "the environment to run run.py (the environment to run the backend and frontend in). Choices are {'development', 'production'}"
)

args = parser.parse_args()
env = args.env
if env:
    print(f"********** Running my-portflio fast_api server in {env} mode 👨🏽‍💻. **********")

