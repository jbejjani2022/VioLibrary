from flask import redirect, session
from functools import wraps
from cs50 import SQL

db = SQL("sqlite:///api.db")

"""Global variables: dropdown boxes for search page"""
# Possible search filters
composers_list = []
epochs_list = []
forms_list= ["Sonata", "Suite", "Misc."]
instr_list = ["Violin Solo", "Violin and Piano"]

# Adding composers to list using SQL query
composer_query = db.execute("SELECT name FROM composers ORDER BY name")
for i in range(len(composer_query)):
    composers_list.append(composer_query[i]["name"])

# Adding epochs to list using SQL query
epoch_query = db.execute("SELECT DISTINCT epoch FROM composers")
for i in range(len(epoch_query)):
        epochs_list.append(epoch_query[i]["epoch"])

# List of libraries
library_list = []

# Adding library names to list using SQL query


"""Helper functions"""
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def pw_req(s):
    """ Check if password is:
            at least 8 characters long,
            has a number/special symbol in it,
            and has either at least 1 capital or lowercase letter.
    """

    # Errors are stored in a list, which will be printed out
    errors = []

    # Length of password
    if len(s) < 8:
        errors.append('Password must be at least 8 characters long.')

    # Capital, lowercase, symbol
    capital = 0
    lowercase = 0
    symbol = 0
    for i in range(len(s)):
        if s[i].isupper():
            capital += 1
        elif s[i].islower():
            lowercase += 1
        else:
            symbol += 1

    if capital == 0:
        errors.append('Password must have at least 1 capital letter.')
    if lowercase == 0:
        errors.append('Password must have at least 1 lowercase letter.')
    if symbol == 0:
        errors.append('Password must have at least 1 special symbol or number.')

    return errors

def libraries_list():
    """Returns a list of libraries, which is a list of list of dicts"""

    libraries = []

    # Getting user info
    current = session["user_id"]

    # Get names for all libraries and store in dict
    names = db.execute("SELECT DISTINCT lib_name FROM libraries WHERE user_id = ?", current)

    # Number of libraries
    count = len(names)

    # For each library
    for i in range(count):

        # Every work is a dict; one library is a list of dicts; all libraries in one list (i.e. list of list of dicts)
        library = []

        # Iterate by name
        lib_query = db.execute("SELECT work_id FROM libraries WHERE user_id = ? AND lib_name = ? ORDER BY lib_name", current, names[i]["lib_name"])

        # For every piece
        for j in range(len(lib_query)):

            work_id = lib_query[j]["work_id"]
            # For empty library
            if not work_id:
                continue

            # Adding necessary info to dict
            work = {}
            work["id"] = int(work_id)
            work_query = db.execute("SELECT * FROM works WHERE id = ?", work["id"])
            composer_query = db.execute("SELECT * FROM composers WHERE id = ?", work_query[0]["composer_id"])
            work["name"] = work_query[0]["name"]
            work["composer"] = composer_query[0]["name"]
            work["birth"] = composer_query[0]["birthyear"]
            work["death"] = composer_query[0]["deathyear"]
            work["epoch"] = composer_query[0]["epoch"]
            work["fullname"] = composer_query[0]["fullname"]

            # Add work to list
            library.append(work)

        # Add library to bigger list of all libraries
        libraries.append(library)
    return libraries, names