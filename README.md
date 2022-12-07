# **VioLibrary**

## **About**
VioLibrary is a tool for finding violin recital repertoire and brainstorming and building recital programs.


# **How to Run**

Included in our `project.zip` is the `api.db` database, which already contains the relevant data for the project which we have retrieved from the [OpenOpus](https://openopus.org) API. So, no setup is necessary to run and test our project.

Use the project by simply running flask (with `flask run`) within the project directory and opening the link in your browser.

The user can then register for a new account by entering a username (that has not already been taken) and a password. The password must be at least 8 characters long, has at least 1 lowercase, 1 uppercase, and 1 special symbol or number.


# **Using VioLibrary**

While logged in, the user can perform the following basic tasks:


## **Search**
On the homepage of the site, the user can search for violin works using the search tool. After applying one or more filters, the user can hit search to see a table listing the works that match the data entered in the filters. A work must satisfy each of the filters to be displayed in the table. For example, selecting “Violin and Piano” in the “Form” filter and “Romantic” in the “Epoch” filter and clicking search will show works written in the romantic period for violin and piano. As another example, entering “partita no. 2” in the “Title” filter and clicking search will show works that have “partita,” “no.,” and “2” in their name, in any order. Selecting “Bach” in the “Composer” filter and “post-war” in the “Epoch” filter and clicking search will show no works as expected, since Bach is not a post-war composer. Note that the user only needs to type in a single value for birthyear and deathyear (i.e. the user need not type in a year range for the filter to work.)


## **Favorite**
The user can add a work to their favorites using the dropdown bar under the results table. The dropdown lists all of the works shown in the search results table. The user can then select a work and click confirm to favorite it. Errors are displayed if the work has already been favorited or if no work was selected before clicking confirm. Once favorited, a work appears in the favorites page, which the user can access through the nav-bar at the top of the site. On the favorites page, the user can use a dropdown to unfavorite a work, removing it from the favorites table.


## **Libraries**
The user can access the libraries page by clicking “Libraries” on the nav-bar. On the libraries page, the user can create a library. Clicking the “Create Library” button triggers a modal, which prompts for the name of the new library. If this name has not been taken by another library, clicking “Confirm” will create a new library with that name. Works can be added to a library using the dropdown bars under the results table back on the homepage. The user just has to select a work and a library to add it to. Back on the libraries page, the user can see this work in the library by clicking the name of the library to show its contents. Each work in the library can then be clicked to show more details. The name of the library can then be clicked again to collapse its contents. A dropdown in each library lets the user remove a work from that library. Another dropdown under the libraries can be used to delete an entire library.


## **Other Actions**
The user can click the button displaying their username in the top right corner of the site to show two more actions: Change Password and Log Out. Clicking Change Password brings the user to a page where they can change their password. Clicking Log Out will immediately log the user out and bring them to the log in page. Clicking the info button in the top right will display a modal with information about the site.

Video URL: [https://youtu.be/Bs6iXfBvb1s](https://youtu.be/Bs6iXfBvb1s)