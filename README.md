# **VioLibrary**

## **About**
VioLibrary is a web tool that makes it easy to search for violin recital repertoire and brainstorm and build recital programs.
Apply a range of search filters to find works that fit your interests and needs; add works to your favorites page; get 
personalized recommendations for new works to explore; and create custom libraries to group works together.

By: Joey Bejjani and Enoch Li

# **How to Run**

The `api.db` database file already contains the relevant data for the project which we have retrieved from the [OpenOpus](https://openopus.org) API. No setup is necessary to run and test our project.

Use the project by installing the dependencies in `requirements.txt` and running flask (via `flask run`) within the project directory. Then, open the provided link to the local server in your browser.

The user can then register for a new account by entering a username (that has not already been taken) and a password. The password must be at least 8 characters long, have at least 1 lowercase, 1 uppercase, and 1 special symbol or number.


# **Using VioLibrary**

While logged in, the user can perform the following tasks:


## **Search**
On the homepage of the site, the user can search for violin works using the search tool. After applying one or more filters, the user can hit search to see a table listing the works that match the data entered in the filters. A work must satisfy each of the filters to be displayed in the table. For example, selecting “Violin and Piano” in the “Form” filter and “Romantic” in the “Epoch” filter and clicking search will show works written in the romantic period for violin and piano. As another example, entering “partita no. 2” in the “Title” filter and clicking search will show works that have “partita,” “no.,” and “2” in their name, in any order. Selecting “Bach” in the “Composer” filter and “post-war” in the “Epoch” filter and clicking search will show no works as expected, since Bach is not a post-war composer. Note that the user only needs to type in a single value for birthyear and deathyear (i.e. the user need not type in a year range for the filter to work.)


## **Favorite**
The user can add a work to their favorites using the dropdown bar under the results table. The dropdown lists all of the works shown in the search results table. The user can then select a work and click confirm to favorite it. Errors are displayed if the work has already been favorited or if no work was selected before clicking confirm. Once favorited, a work appears in the favorites page, which the user can access through the nav-bar at the top of the site. On the favorites page, the user can unfavorite a work by clicking its `-` button, removing it from the favorites table.


## **Libraries**
The user can access the libraries page by clicking “Libraries” on the nav-bar. On the libraries page, the user can create a library. Clicking the “Create Library” button triggers a modal, which prompts for the name of the new library. If this name has not been taken by another library, clicking “Confirm” will create a new library with that name. Works can be added to a library using the dropdown bars under the results table back on the homepage. The user just has to select a work and a library to add it to. Back on the libraries page, the user can see this work in the library by clicking the name of the library to show its contents. Each work in the library can then be clicked to show more details. The name of the library can then be clicked again to collapse its contents. A dropdown in each library lets the user remove a work from that library. Another dropdown under the libraries can be used to delete an entire library.


## **Recommender**
On the favorites page, the user receives a list of 5 recommended works based on their current favorites. The recommendations change dynamically as favorites are added and removed. Recommendations are determined via similarity scores that are calculated using a combination of similarity metrics that capture the distance between favorited works and works that the user has not favorited thus far. This recommender system is implemented in the `work_similarity` directory. The `collaborative_filtering` directory contains my experimentation with the collaborative filtering recommendation algorithm, which relies on the basic assumption that users will enjoy works that have been favorited by users who are similar to them. So, user A might receive recommendations based on the interests of a similar user B. This recommendation system becomes powerful when the user and favorites data are rich, allowing for similarities to be computed across many users and works simultaneously. VioLibrary uses the `work_similarity` recommender system as a placeholder until the number of users is sufficiently large to make collaborative filtering valuable.

The user also receives recommended works for any libraries that they create. Recommended additions to each library are based on similarity metrics to works currently in that library.


## **Other Actions**
The user can click the button displaying their username in the top right corner of the site to show two more actions: Change Password and Log Out. Clicking Change Password brings the user to a page where they can change their password. Clicking Log Out will immediately log the user out and bring them to the log in page. Clicking the info button in the top right will display a modal with information about the site.
