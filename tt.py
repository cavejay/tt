#!/usr/bin/env python3
# This is a script intended to track your project activities.
# It is really simple and I got the idea when using todolist on the command
# line. tymetracker (tt) is written entirely in Python 3 and stores the
# records in a json data structure in the user's home directory.
#
datafile = "~/.tymetracker.json"

### Here be dragons
# Sanity check: only proceed if we are in a python3 environment
import sys
if not str(sys.version).startswith("3"):
    print("Python 3 is required to run tymetracker/tt.")
    sys.exit(1)

# Import stuff we need
import json
import os
import time

# Set variables we need
n = "tymetracker/tt"
f = os.path.abspath(os.path.expanduser(datafile))

class bcolors:
    """Define some colors that can be used in the terminal.
    """
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def init():
    '''Initialize a new datafile.
    '''
    if os.path.isfile(f):
        print("Data file {} already exists".format(f))
        sys.exit(2)
    else:
        print("Initializing new data file {}".format(f))

        # Initialize new data dict
        data = {
                "meta": {
                    "last_id": 0,
                    "file_version": 1,
                    },
                "tracking": {
                    "active": False,
                    "project": None,
                    "started": None,
                    },
                "projects": {
                    # id:    {
                        # "name": Projektname,
                        # "history": [] # tuples (start, stop, mins)
                    # }
                    },
                }

        # ... and write it to data file
        save(data)

def status():
    """Display some information about the current status of te software
    """
    data = load()
    if not data["tracking"]["active"]:
        print("No active time tracking")
    else:
        since = data["tracking"]["started"]
        project_id = data["tracking"]["project"]
        project_name = data["projects"][project_id]["name"]
        print("Tracking time in project {name} since {date}".format(name=project_name, date=since))

def load():
    try:
        fp = open(f, "r")
        data = json.load(fp)
        fp.close()
    except FileNotFoundError as e:
        print("Could not load data file. Please run", bcolors.YELLOW, "init", bcolors.END, "first.")
        sys.exit(3)
    except Exception as e:
        print(e)
        sys.exit(4)

    if data is None:
        print("Read corrupt data from", f)
        sys.exit(6)

    return data

def save(data):
    if data is not None:
        try:
            fp = open(f, "w")
            json.dump(data, fp)
            fp.flush()
            fp.close()
        except Exception as e:
            print(e)
            sys.exit(5)
    else:
        print("No data to write")

def usage():
    """Print the list of commands that are supported. This function is
    called if the users calls tt with no or too few arguments.
    """
    group = {
            "Generic commands": {
                "init": "Initialize new data file",
                "status": "Display status information",
                },
            "Projects": {
                #"DESC": "Projects are needed for time tracking",
                "ap project name": "Add new project with name \"project name\"",
                "dp 23": "Delete project with id 23",
                "lp": "List projects and their ids",
                },
            "Tracking": {
                #"DESC": "Time tracking is about time tracking",
                "start 23": "Starts time tracking for project id 23",
                "stop": "Stops active time tracking",
                "show 23": "Show tracked times for project 23",
                "rep 23": "Show a report for project 23",
                }
            }

    # Display the commands/dicts
    for group, commands in sorted(group.items()):
        print(bcolors.PURPLE, "\n{group}".format(group=group), bcolors.END)

        # print the DESC if needed
        if "DESC" in commands:
            print("{desc}".format(desc=commands["DESC"]))

        # print all commands (and not DESC)
        for command, description in sorted(commands.items()):
            if command is not "DESC":
                print(bcolors.YELLOW, "    {cmd:20s}".format(cmd=command), bcolors.END, description)

def list_projects():
    data = load()
    p = data.get("projects", {})

    if len(p) == 0:
        print("No projects found.")
    else:
        for project_id, project_data in sorted(p.items()):
            print("    {i:>3}   {n}".format(i=project_id, n=project_data["name"]))

def add_project():
    if len(sys.argv) < 3:
        print("You must specify a project name")
        sys.exit(10)

    name = " ".join(sys.argv[2:]).strip()

    data = load()

    project = {}
    project_id = int(data["meta"].get("last_id", 0)) + 1
    project["name"] = name
    project["history"] = []

    projects = data.get("projects", {})
    projects[project_id] = project

    data["meta"]["last_id"] = project_id
    data["projects"] = projects

    save(data)

    print("Created project \"{name}\" with id {i}".format(name=name, i=project_id))

def del_project():
    if len(sys.argv) < 3:
        print("You must specify a project id")
        sys.exit(11)

    project_id = sys.argv[2]

    data = load()
    if project_id not in data.get("projects", {}):
        print("Project {pid} not found".format(pid=project_id))
        sys.exit(12)
    else:
        del data["projects"][project_id]
        save(data)
        print("Project {name} deleted".format(name=_get_project_name(data, project_id)))

def _get_project_name(data, project_id):
    try:
        return data["projects"][project_id]["name"]
    except:
        return None

def start_tracking():
    if len(sys.argv) < 3:
        print("You must specify a project id")
        sys.exit(20)

    project_id = sys.argv[2]

    data = load()
    if data["tracking"]["active"]:
        print("Tracker already started")
        sys.exit(21)

    data["tracking"]["active"] = True
    data["tracking"]["project"] = project_id
    # TODO: Use better time format
    data["tracking"]["started"] = time.time()

    save(data)
    print("Tracker started for project {name}".format(name=_get_project_name(data, project_id)))


def stop_tracking():
    data = load()
    if not data["tracking"]["active"]:
        print("Tracker not active")
        sys.exit(22)

    project_id = data["tracking"]["project"]
    started = data["tracking"]["started"]
    stopped = time.time()
    diff = stopped - started

    # add tuple to history
    history = data["projects"][project_id]["history"]
    history.append( (started, stopped, diff) )
    data["projects"][project_id]["history"] = history

    # reset tracking settings
    data["tracking"]["active"] = False
    data["tracking"]["project"] = None
    data["tracking"]["started"] = None

    save(data)
    print("Tracker stopped for project {name} after {duration}".format(name=_get_project_name(data, project_id), duration=diff))


def show():
    pass

def report():
    pass

def main():
    """Main function that handles the run of tymetracker.
    Parses the arguments and calls the appropriate functions.
    """
    if len(sys.argv) <= 1:
        usage()
    elif sys.argv[1].lower() == "init":
        init()
    elif sys.argv[1].lower() == "status":
        status()
    elif sys.argv[1].lower() == "lp":
        list_projects()
    elif sys.argv[1].lower() == "ap":
        add_project()
    elif sys.argv[1].lower() == "dp":
        del_project()
    elif sys.argv[1].lower() == "start":
        start_tracking()
    elif sys.argv[1].lower() == "stop":
        stop_tracking()
    else:
        usage()


# Starting here
main()