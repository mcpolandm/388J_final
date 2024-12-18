Spotify Album and Artist Database

Writeup:
mchun@terpmail.umd.edu
hchava@terpmail.umd.edu
wchan2@terpmail.umd.edu
mmcpolan@terpmail.umd.edu

Description of your final project idea:

Unfortunately, Spotify API only allows us to authorize specific Spotify accounts, but given a full rollout of our application, thus getting approval to exit Development Mode, we can fetch data from any logged in Spotify user.
As a result, the graders may not be able to access portions of our site, so a video demonstrating functionality can be found here: https://streamable.com/n8a5ec

We are creating a review site for music on Spotify, where users can also see their own stats relating to the music that they've listened to over a certain period of time. They can also browse through artists and albums, viewing reviews and ratings left on these, as well as functionality to post their own reviews and ratings. We will get the data from Spotify API, and will store the data in MongoDB. We will use Flask to implement functionality.

Describe what functionality will only be available to logged-in users:
Logged in users will be able to see their own stats page
Logged in users will be able to make reviews 
Logged in users will be able to give ratings to songs
Non-logged in users can only view pages for different songs, but not users, and cannot leave reviews or ratings.

List and describe at least 4 forms:
Registration Form-for users wanting to sign up/create an account and connect their spotify account to their website account. 
This saves the user’s Spotify credentials in MongoDB.
Login Form-allows users to be validated so they can make reviews, etc
Review Form-allows users to submit a text review for a specific album or artist
Search Form-allows users to search for an album or artist by name

List and describe your routes/blueprints (don’t need to list all routes/blueprints you may have–just enough for the requirement):
/register: displays registration form
/login: displays login form
/{albumId}: display reviews for a song as well as the review/rating form for the user
/{userId}: displays user stats, ratings, and reviews
/top-songs: shows the user’s most played songs


Describe what will be stored/retrieved from MongoDB:

MongoDB will store user data, including login information and the different reviews and ratings they’ve posted. Reviews and ratings for albums 
and artists will be retrieved when viewing the page, and user reviews and ratings will be retrieved when viewing the user stat page.

Describe what Python package or API you will use and how it will affect the user experience:
https://developer.spotify.com/documentation/web-api

We will use the Spotify web API to fetch data from albums and artists. It will also be able to get user data which will be displayed in different forms so they can see different stats.

It is able to affect user experience due to its real-time updates of data and how it can be personalized to the individual user. 
It will also allow the website to provide information on everything listed on Spotify, so it can provide a high quantity of data.
