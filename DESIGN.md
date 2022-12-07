# **Design**

The program makes use of the [OpenOpus](https://openopus.org) API, but does not make active requests everytime the user searches for a work, as the API is formatted in a rather messy way, and in the context of classical music information there is no need for real-time data retrieval. Instead, we have downloaded relevant data from OpenOpus onto `api.db`, which is the database used by our web application.

## **/static**
The static directory contains the .css file that styles the templates in our web application. It also contains the favicon.ico file, which is a violin icon used to style the website head. We chose to consolidate all the styling into a separate css file (rather than styling within the html templates) to make editing the appearance of the website more efficient.

## **/templates**
The templates directory contains all the .html files necessary.
- `change.html` deals with a password change.
- `favorites.html` shows the user all the works he/she favorited previously and allows the user to delete favorites.
- `layout.html` is the layout for the entire web application, inherited by the other html files to give them a shared style.
- `login.html` and `register.html` deals with a user login and registration respectively.
- `search.html` allows the user to search for pieces, shows search results, and allows the user to favorite works and add them to libraries.
- `libraries.html` shows the user all the libraries he/she created, and also allows for creating new libraries, deleting libraries, and deleting works in libraries.

## HTML and CSS
Here we note some choices we made in the layout and styling of the site:
- As inspired by Finance, `layout.html` gives the site a `nav-bar` through which the user can navigage to the different pages on the site.
- We utilized bootstrap classes to style our templates. Bootstrap was used to design the modals for Create Library on the libraries page and for the info modal on the top right corner of the site. We also used Bootstrap to design the username dropdown right by the info modal, which expands to show the Change Password and Log Out options. Finally, we used Bootstrap collapsible classes in the libraries page to display each library as a collapsible container that shows the works inside upon clicking.
- We used the icon library from fontawesome.com to make the info modal appear as an info circle icon.
- Also inspired by Finance, we used a table on the search page to list the search results, and also on the favorites page to list the favorited works.
- One other noteable design choice reflected in `styles.css` is the classes `row`, `column`, `left`, and `right`. These classes are used in `search.html` to group the search tool (i.e. the list of filters) into a column on the left and the search results (i.e. the table of works and the dropdowns with "adding" functionality) into a column on the right.
    - This was possible by wrapping the left and right columns in a `<div>` with `class = row` and styling `row` with `display: flex;`.
    - Then, in the `left` and `right` classes, we specified that we want the left column to take up a total of 25% of the row and the right column to fill out the remaining 75%, using the `flex` attribute. Overall, this design choice allowed us to keep the search tool and the results on the same page, while splitting them up visually.
- Inside each library, we used the `<details>` HTML tag to list each work. Clicking each work reveals further details about the work.
- Throughout the site, we made the choice of using dropdown lists whenever the user needs to add or remove a work from favorites or from a library, or remove an entire library. Ideally, we would have improved the user experience by having some sort of icon, say a heart, after each work in the results table allowing the user to favorite or unfavorite the work with one click, and something similar for editing libaries and their contents. The dropdown lists still provide this core functionality, but aren't as user friendly, we realized, as other options we will explore for future projects.
- Finally, in deciding how to display errors, we at first considered adopting `apology` from Finance. But rather than directing the user to a separate error page, we decided on showing error messages within the template where the error was made. We did this as follows:
    - In the case of user input errors, we rendered a template in the Python code, passing in a boolean set to `True`.
    - Then in the corresponding template, we used Jinja such that the relevant error message is displayed if the boolean passed to `render_template` is `True`. In other words, under normal circumstances, the boolean would not be passed upon calling `render_template`, and would thus not show up.
    - We then styled the errors, making them red, using the `error` class in `styles.css`.


## **api.sql, api.db**
`api.sql` details the schema of the `api.db` database.
- The `composers` and `works` table have information of these respective items.
- The `users` table records username and password.
- The `favorites` table records the works a user favorited by taking their user ID and the work ID. This allows for multiple users to favorite the same work at the same time.
- The `libraries` table keeps track of the libraries each user has. When it displays the tables for a particular user, the SQL query is done not by setting conditions on the primary key (ID), but rather on both the user ID and the library name. Users are not allowed to have two libraries of the same name. Even if two users happen to have a library with the same name, the user ID condition prevents showing both libraries; it only shows the libraries for the current user. Note how the date/time and work ID in the table, unlike `favorites`, are not listed as `NOT NULL`. This is because when the user creates a library, they are no works in it by default. Therefore, all entries other than user ID and library name are set to `NULL`.

## **app.py**

### **/login, /register, /changepassword, /logout**
These routes are rather straightforward, so I will not go into them here. Worth noting is the use of `pw_req` within `/register` and `/changepassword`, the functionality of which is explained in `helpers.py`.

### **/**
This route is the heart of the entire program, consisting of the search function. To make a query with potentially multiple filters, a long SQL query consisting of multiple `SELECT` queries is connected together with the keyword `INTERSECT`. To do this there are two lists, `queries` and `placeholders`. For every search filter, if the user inputs anything, a SQL query for the relevant filter is generated and added to the `queries` list as a string, and the contents of the user's actual input is stored in the `placeholders` list. The program then iterates through every item in the two lists and creates the final SQL query.

The title filter is worth noting. Since works of the same form may have different names (e.g. 'Solo Violin Sonata' or 'Sonata for Violin Solo' or 'Solo Sonata for Violin'), it is a bit restricting to return works with the exact order of words that the user typed in. Instead, the `split()` function is used to iterate through each word in the search term, and a SQL query is run for each word (case-insensitive and allowing for one or more characters before and after each word, using %), connected using `INTERSECT`.


### **/favorites**
This route returns all works the users favorited in a list of dictionaries, each dictionary being the relevant information of a particular work. The favorites table has a `user_id` column, which ensures the query doesn't return a work that's favorited by another user.

### **/addfavorite**
This route adds a work to the `favorites` table. It also records the date/time at which the work was favorited, so as to allow for some kind of ordering when `/favorites` is called.

### **/removefavorite**
This route removes a work from the `favorites` table using the `DELETE FROM` keyword.

### **/libraries**
This route returns all libraries the user created. It uses the `libraries_list` function, the functionality of which is explained in `helpers.py`.

### **/createlibrary**
This route allows the user to create a new library. Since a newly created library is empty, only the user ID and library name is added to the `libraries` table in SQL; the work ID and date/time columns are left blank.

### **/addtolibrary**
This route allows the user to add a work to a library. It checks whether the library is empty by querying for work IDs and checking if the length of the list of dictionaries returned is 0. If so, instead of adding a new row, it just updates the row using the keyword `UPDATE`. Otherwise, it adds a new row using the keyword `INSERT INTO`.

### **/removework**
This route allows the user to remove a work from a library using the keyword `DELETE FROM`. Similar to `/addtolibrary`, it checks whether the library is empty by querying for work IDs and checking if the length of the list of dictionaries returned is 1. If so, instead of adding a new row, it just updates the row, setting the work ID and all date/time columns to `NULL`. Otherwise, it deletes the entire row.

### **/removelibrary**
This route deletes the entire library using the keyword `DELETE FROM`, selecting the user ID and library name as its conditions.

## **helpers.py**
The `helpers.py` file has a series of global variables and 3 helper functions.

- The global variables are for the implementation of dropdown lists in `search.htm`l. Since the search.html template will be rendered in various scenarios (e.g. potential errors, when search results are returned), this can return the dropdown list without copy and pasting the same lines of code.

- `login_required`, as adapted by finance, is a decorator that requires the user to be logged in in order to access certain functions.

- `pw_req` checks if a password meets the following requirements:
    1. The password is at least 8 characters long;
    2. The password contains at least 1 uppercase letter;
    3. The password contains at least 1 capital letter; and
    4. The password contains at least 1 number/special symbol.
    Instead of returning a boolean depending on whether the password is appropriate or not, it returns a list of errors, which the HTML file then prints out whenever appropriate; we figured it would be better to inform the user what exactly is missing from their password.

- `libraries_list` shows all the libraries a user has, including the corresponding works and their information. Each item in the list 'libraries' is a library itself, and each 'library' is a list of dictionaries, each dictionary containing relevant information about each work.

## links.py and links.txt
`links.py` is a simple program that creates `links.txt`, a file that has a URL query for each composer's works.

## retrieve_data.py
`retrieve_data.py` gets the data from the API, filters the data such that only works for solo violin or violin+piano remain, then inserts it into `api.db`.
- For each link in the `links.txt` file, the program does an API query with that link, and uses the `urllib.request` and `json` library to make the data fit for manipulation on Python.
- The request returns a dictionary with many different items, so the program chooses the relevant data and inserts them into the SQL table.
- Composer names and their relevant information (e.g. epoch, birthyear, deathyear) are added to the `composers` table. If a composer is still alive, their deathyear is defaulted to 2099.
- The program then iterates over each composer, and selects all their works.
- The `unwanted_instruments` list at the beginning of the program is to filter out works that involve more than a violin or piano. If the work title has one or more words in that list, it will be skipped over and will not be added to the database. This is checked using the `search` function from the `re` library.
- The relevant information of appropriate works (e.g. form, instrumentation) are then inserted into the `works` library
- The links in `links.txt` search for the chamber works of a composer. Although all violin recital works appear as chamber works, the converse is not true. Since the composers are added to the database before the works, there is a chance that the composer doesn't actually have any violin recital works as a part of his chamber music compositions. The last lines of code deal with this, removing the composer from the `composers` table entirely if there are no works associated with this composer.