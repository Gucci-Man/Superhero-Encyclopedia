# Superhero Encyclopdedia

## Created by Adel Ngo

**API:** https://superheroapi.com/

**Deployed link:** https://superhero-encyclopedia.onrender.com

This is a web app that functions as a superhero encyclopedia for registered users. Users will be able to select from any of the displayed superheros and retrieve information about them. They are also able to select and deselect their favorite superheros. 

## Features

- **Editng User Profiles:** Once registered, users will be able to update their bio and location and change their username if they like. This showcases the web app's ability to *create* and *update* existing information. 

- **Adding/Removing Favorites:** Users will be able to add and remove any favorited superheros. This adds more of a personal touch for each user. 

- **Viewing Superhero Info:** Users may click on any displayed superhero and are able to *read* information fetched from an external API. 

- **Deleting a User's Profile:** Users may *delete* their profiles and their information along with any favorites will be removed, ensuring complete deletion of data. 

## Standard User Flow

1. If a user doesn't have a account created they will have to register by clicking on the "register" button where it will take them to a registration form.

2. After creating an account the user will be taken to the homepage where a table of superheros will be on display.

3. The user may click on any of those displayed superheros and it will take them to an information page about the selected superhero.

4. They may add the superhero as a favorite.

5. The "Profile" navbar link allows the user to view their profile and update it or delete it.

6. The "Favorites" navbar link takes the user to view any favorited superheros. They may click on them thus redirecting to the superhero's info page. 

7. The "Logout" navbar link logs out the user from the app.

8. If a user still has a registered account, they may log back in. 

## Technology Stack

- Python, HTML and CSS

- Flask 

- WTForms

- Bcrypt

- SQLAlchemy

- PostgreSQL 

- Jinja 

