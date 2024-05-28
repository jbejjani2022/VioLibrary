from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import *
from work_similarity.recommender import Recommender
from work_similarity.compute_similarities import compute_similarity_matrix

"""
Contents of functions:
/login
/register
/changepassword
/logout
/
/favorites
/addfavorite
/removefavorite
/libraries
/createlibrary
/addtolibrary
/removework
/removelibrary
"""

# Configure application
app = Flask(__name__)

# SQL database
db = SQL("sqlite:///api.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", no_username=True)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", no_pw=True)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", wrong_info=True)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        
        # Initialize the user's recommender system
        session["recommender"] = Recommender(5)

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # No username
        if username == "":
            return render_template("register.html", no_username=True)

        # Username already exists
        if len(db.execute("SELECT username FROM users WHERE username = ?", username)) != 0:
            return render_template("register.html", username_already_exists=True)

        # No password
        if not password or not confirmation:
            return render_template("register.html", no_pw=True)

        # Passwords do not match
        if password != confirmation:
            return render_template("register.html", pw_not_match=True)

        # Password does not meet requirements
        errors = pw_req(password)
        if len(errors) != 0:
            return render_template("register.html", errors=errors)

        # Add to database
        db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", username, generate_password_hash(password, method='pbkdf2'))

        # Get the new user's id
        id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        # Log the new user in automatically by assigning their id to session's "user_id" field
        session["user_id"] = id
        session["username"] = username
        
        # Initialize the user's recommender system
        session["recommender"] = Recommender(5)

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    """Allows user to change password"""
    if request.method == 'POST':
        current = session["user_id"]
        old_pw = request.form.get("old")

        # No old password
        if not old_pw:
            return render_template("change.html", no_old_pw=True)

        # Wrong old password
        if not check_password_hash(db.execute("SELECT hash FROM users WHERE id = ?", current)[0]["hash"], old_pw):
            return render_template("change.html", wrong_old_pw=True)

        # No new password
        new_pw = request.form.get("new")
        if not new_pw:
            return render_template("change.html", no_new_pw=True)

        # Password does not meet requirements
        errors = pw_req(new_pw)
        if len(errors) != 0:
            return render_template("change.html", errors=errors)

        # Update database
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(new_pw), current)
        return redirect("/")

    else:
        return render_template("change.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Search / Results Homepage"""

    if request.method == "POST":

        # We put together a list of strings of different SQL queries, and then concatenate them together later
        queries = []
        placeholders = []

        # Work title; split them into individual words
        piece_words = request.form.get("title").split()

        # If user typed in query for title search
        if len(piece_words) != 0:
            """words = []"""
            for i in range(len(piece_words)):
                # Search query for each word
                queries.append("SELECT * FROM works WHERE name LIKE ?")
                placeholders.append("%" + piece_words[i] + "%")

        # If user chose composer
        composer = request.form.get("composer")
        if composer:
            # Get all works by this composer
            query = "SELECT works.* FROM works JOIN composers ON works.composer_id = composers.id WHERE composer_id = (SELECT composers.id FROM composers WHERE composers.name = ?)"
            queries.append(query)
            placeholders.append(composer)

        # If user chose birth year
        min_birth = request.form.get("min_birth")
        max_birth = request.form.get("max_birth")
        if min_birth:
            query = "SELECT works.* FROM works JOIN composers ON works.composer_id = composers.id WHERE works.composer_id IN (SELECT composers.id FROM composers WHERE composers.birthyear >= ?)"
            queries.append(query)
            placeholders.append(min_birth)

        if max_birth:
            max_birth = int(max_birth)
            query = "SELECT works.* FROM works JOIN composers ON works.composer_id = composers.id WHERE works.composer_id IN (SELECT composers.id FROM composers WHERE composers.birthyear <= ?)"
            queries.append(query)
            placeholders.append(max_birth)

        # If user chose death year
        min_death = request.form.get("min_death")
        max_death = request.form.get("max_death")
        if min_death:
            min_death = int(min_death)
            query = "SELECT works.* FROM works JOIN composers ON works.composer_id = composers.id WHERE works.composer_id IN (SELECT composers.id FROM composers WHERE composers.deathyear >= ?)"
            queries.append(query)
            placeholders.append(min_death)

        if max_death:
            max_death = int(max_death)
            query = "SELECT works.* FROM works JOIN composers ON works.composer_id = composers.id WHERE works.composer_id IN (SELECT composers.id FROM composers WHERE composers.deathyear <= ?)"
            queries.append(query)
            placeholders.append(max_death)

        # If user chose instrumentation
        instr = request.form.get("instr")
        if instr == "Violin Solo":
            query = "SELECT * FROM works WHERE solo = 1"
            queries.append(query)
        if instr == "Violin and Piano":
            query = "SELECT * FROM works WHERE solo = 0"
            queries.append(query)

        # If user chose epoch
        epoch = request.form.get("epoch")
        if epoch:
            query = "SELECT works.* FROM works JOIN composers ON works.composer_id = composers.id WHERE works.composer_id IN (SELECT composers.id FROM composers WHERE composers.epoch = ?)"
            queries.append(query)
            placeholders.append(epoch)

        # If user chose form
        form = request.form.get("form")
        if form == "Sonata":
            query = "SELECT * FROM works WHERE form = 'Sonata'"
            queries.append(query)
        elif form == "Suite":
            query = "SELECT * FROM works WHERE form = 'Suite'"
            queries.append(query)
        elif form == "Misc.":
            query = "SELECT * FROM works WHERE form = 'Misc.'"
            queries.append(query)

        # Combining all queries together
        final_query = ""

        # Putting together all queries
        for i in range(len(queries)):
            final_query += queries[i]
            if i <= len(queries) - 2:
                final_query += " INTERSECT "

        list = db.execute(final_query, *(placeholders[i] for i in range(len(placeholders))))  # Adding placeholders as arguments dynamically

        # If user did not type in anything
        if len(list) == 0:
            return render_template("search.html", no_input=True, composers=composers_list, epochs=epochs_list, forms=forms_list, instr=instr_list)

        # Works library only returns composer IDs; this part retrieves their names
        composer_results = []
        for i in range(len(list)):
            composer_results.append(db.execute("SELECT fullname FROM composers WHERE id = ?", list[i]["composer_id"])[0]["fullname"])

        names = libraries_list()[1]

        return render_template("search.html", libraries=names, list=list, composer_results=composer_results, composers=composers_list, epochs=epochs_list, forms=forms_list, instr=instr_list)

    else:
        return render_template("search.html", composers=composers_list, epochs=epochs_list, forms=forms_list, instr=instr_list)


@app.route("/favorites", methods=["GET"])
@login_required
def show_favorites():
    """Shows the user a list of their 'favorited' works, with recommendations for works to add"""

    # Getting user info
    current = session["user_id"]

    # Get favorited works from user
    favorited_works = db.execute("SELECT work_id, year, month, day FROM favorites WHERE user_id = ? ORDER BY year, month, day, hour, minute, second", current)
    favorites_info = get_works_info(favorited_works, favorites=True)
    
    # Get recommendations for new works to favorite
    recommender = session["recommender"]
    recommended_works = recommender.get_user_favorites_recommendations(current)
    recs_info = get_works_info(recommended_works, favorites=False)
    # print(recs_info)
    for rec in recs_info:
        print(rec['name'])
    
    # Render template
    return render_template("favorites.html", favorites_info=favorites_info, recs_info=recs_info)


@app.route("/addfavorite", methods=["POST"])
@login_required
def addfavorite():
    """Records in database"""

    # Getting user info
    current = session["user_id"]

    # Getting work id
    work_id = request.form.get("favorite")

    # If no input
    if not work_id:
        return render_template("search.html", no_favorite_input=True, composers=composers_list, epochs=epochs_list, forms=forms_list, instr=instr_list)

    # Get time of request
    time = datetime.now()

    # If already added to favorites
    if len(db.execute("SELECT * FROM favorites WHERE work_id = ? AND user_id = ?", int(work_id), current)) != 0:
        return render_template("search.html", favorited=True, composers=composers_list, epochs=epochs_list, forms=forms_list, instr=instr_list)

    # Update SQL database
    db.execute("INSERT INTO favorites(user_id, work_id, year, month, day, hour, minute, second) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", current, work_id, time.year, time.month, time.day, time.hour, time.minute, int(time.second))

    return redirect("/")

@app.route("/removefavorite", methods=["POST"])
@login_required
def remove_favorite():
    """Removes a piece from favorites list"""

    # Getting user info
    current = session["user_id"]

    # Remove piece from list
    work_id = request.form.get("favorite")
    if not work_id:
        return redirect("/favorites")

    db.execute("DELETE FROM favorites WHERE user_id = ? AND work_id = ?", current, int(work_id))

    return redirect("/favorites")


@app.route("/libraries", methods=["GET"])
@login_required
def showlibraries():
    """Shows all existing libraries"""

    libraries = libraries_list()[0]
    names = libraries_list()[1]

    return render_template("libraries.html", libraries=libraries, names=names)


@app.route("/createlibrary", methods=["POST"])
@login_required
def createlibrary():
    """Creates new library"""

    lib_name = request.form.get("name")

    # Getting user info
    current = session["user_id"]

    # Library already exists
    if len(db.execute("SELECT * FROM libraries where lib_name = ? AND user_id = ?", lib_name, current)) != 0:
        libraries = libraries_list()[0]
        names = libraries_list()[1]

        return render_template("libraries.html", libraries=libraries, names=names, lib_exists=True)

    # Update SQL with empty table
    db.execute("INSERT INTO libraries(lib_name, user_id) VALUES(?, ?)", lib_name, current)

    return redirect("/libraries")


@app.route("/addtolibrary", methods=["POST"])
@login_required
def addtolibrary():
    """Adds work to library"""

    work_id = request.form.get("work")
    print(db.execute("SELECT name FROM works WHERE id = ?", work_id))
    lib_name = request.form.get("library")

    # Getting user info
    current = session["user_id"]

    # If missing an input
    if not work_id or not lib_name:
        return render_template("search.html", missing_input=True, composers=composers_list, epochs=epochs_list, forms=forms_list, instr=instr_list)

    # Getting time
    time = datetime.now()

    # If work already in library
    if len(db.execute("SELECT * FROM libraries WHERE user_id = ? AND lib_name = ? AND work_id = ?", current, lib_name, work_id)) != 0:
        return render_template("search.html", work_in_lib=True, composers=composers_list, epochs=epochs_list, forms=forms_list, instr=instr_list)

    # If empty library
    if db.execute("SELECT work_id FROM libraries WHERE user_id = ? AND lib_name = ?", current, lib_name)[0]["work_id"] is None:
        db.execute("UPDATE libraries SET work_id = ?, year = ?, month = ?, day = ?, hour = ?, minute = ?, second = ? WHERE user_id = ? AND lib_name = ?", work_id, time.year, time.month, time.day, time.hour, time.minute, int(time.second), current, lib_name)
    else:
        db.execute("INSERT INTO libraries(lib_name, user_id, work_id, year, month, day, hour, minute, second) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", lib_name, current, work_id, time.year, time.month, time.day, time.hour, time.minute, int(time.second))

    # Back to search page
    return redirect("/")


@app.route("/removework", methods=["POST"])
@login_required
def remove_work_from_library():
    """Removes work from library"""
    work_id = int(request.form.get("work"))
    lib_name = request.form.get("library")

    # Getting user info
    current = session["user_id"]

    # If only work in library, delete work but not entire row
    if len(db.execute("SELECT * FROM libraries WHERE user_id = ? AND lib_name = ?", current, lib_name)) == 1:
        db.execute("UPDATE libraries SET work_id = NULL, year = NULL, month = NULL, day = NULL, hour = NULL, minute = NULL, second = NULL WHERE user_id = ? AND lib_name = ?", current, lib_name)

    # Otherwise delete entire row
    else:
        db.execute("DELETE FROM libraries WHERE user_id = ? AND lib_name = ? AND work_id = ?", current, lib_name, work_id)

    return redirect("/libraries")


@app.route("/removelibrary", methods=["POST"])
@login_required
def removelibrary():
    """Removes entire library"""

    # Getting user info
    current = session["user_id"]

    # Getting the name of that library
    lib_name = request.form.get("library")

    # Deleting from database
    db.execute("DELETE FROM libraries WHERE lib_name = ? AND user_id = ?", lib_name, current)

    return redirect("/libraries")