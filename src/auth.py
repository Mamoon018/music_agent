

"""
Problem: 
In this problem, we are supposed to define an endpoint that will accept the user credentials for account creation, perform some validation tests 
before storing into the database, and then open a connection to store credentials in the database.


1. How the feature is supposed to work in terms of the process flow.

    General guidelines:
    (a) we need to ensure the logging of the crucial steps completions of the program

    Model for database:
    (a) We need to define the model for the user database usnig Pydantic model. We need to ensure that we include conditions for the fields in that model using the validater.
    (b) Database is supposed to store the user credentials and therefore, we need to define the model that will check if the user credentials that we have received
        are meeting the requirements of database or what we were expecting. 
        (1) username should be string, less than 20 words, must required
        (2) password should be alphanumeric and should contain at least one special characterc, password must not contain username
        (3) email must be required from the user, and it should contain @gmail.com in it, email local part must be correct


    Program that will take user_credentials & process the request:
    (a) We are supposed to write the program for the create account.
    (b) The program is going to be linked with the single endpoint (not creating as of now), such that it will allow user to create the account.
    (c) The program should validate the user crendetials using the pydantic UserCredentialsModel defined in users.py
    (d)if any of the requirement of datapoint is not met, then it needs to throw the relevant error.
    (e) we need to ensure that program returns the correct and guiding error for the cases where conditions are not met, pydantic is already throwing well readable errors. In case, more than one validation error occurred then we need to ensure
    that we return all of those error at once.
    (f) If the user crendetials are validated by pydantic model then It must search in the database to check if user name or email already used to create an account. If yes, then it should return error "user_name or email already taken". (to avoid enumeration error we will not leak exact info)
    (g) If there is no account with credentials, then it should hash-the-password because we will store the hashed-version of the passwords in the database.
    (i) we need to ensure that unique user_id gets generated everytime we store new user credentials.
    (j) On the successful creation of the account, we need to provide clear confirmation for account creation.

    This is going to be the process flow: Request → Pydantic Validation → DB Duplicate Check → Hash Password → Store → Return Response

    Defining Database fetching (for duplicate check) and insertion method:
    (a) We will be using Supabase database for the data storage
    (b) we will be using supabase fetch command to filter on the column email column, user name column to check the duplicate entiries.
    (b) we will use insert command of supabase to insert the user crendetials into the table "users" 
    (c) we will use "insert a record" command of the supabase database for the insertion of the user credentials in the database.    


"""

