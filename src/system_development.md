### &#x09;			**Interactive Music Info Chatbot**





##### **Problem Context:**

**Who is the user:** User is the person who is music lover who wants to stay updated with the recent industry updates and also wants to explore history behind the interesting fun facts of music industry. (It helps in understanding the expectations of the user from the product.)

**What is the environment of the user:** User is supposed to do this activity in the leisure time, when user wants to know more about the music industry. (It helps understand how the user would want the system to serve.)

**Why is this problem important for the user:** User wants to stay well informed about the areas of his interest. User wants to stay in touch with what is going on and what has happened in music industry.(It tells us what user want to feel about the problem after getting the solution.)



##### **Problem Statement:**

In the context of the nature of user and its environment, an app that brings the information about the recently occurred major events, upcoming music events near by, newly emerging things, and surprising and shocking events in the music industry along with the ability to bring the relevant interesting fun fact about the music industry history that user would want to explore, such that it helps user to spend his leisure time with satisfaction of being able to explore area of his interest.



##### **Business nuances that need to be addressed in a solution:**

1. Because user is going to use it in leisure time, so, app should be interactive and handle Q/A's type conversations. App also needs to ensure that information is shared with the user in interesting and fun manner so, that user find it easier to spend his free time on exploring his interest. It should provide user a sense of the satisfaction.
2. At a time, only one fun fact will be shared with the user on his request however, the hint to explore the other related fun facts will also be shared with the user so, that it can find it easier to stay in flow of exploring things. It will be shared in a way that it is easy for the user to remember the stuff.
3. About the upcoming events, app should be able to come up with the event details like date, place, name of participants, link to the details of event, etc. It should prioritize near by events, short time events, on weekends, relevant to the taste of the user that we can guess from the fun fact which user wants to explore. 
4. App should be able to remember the conversations of the user so, that user can review its previous chats.
5. It should also allow user to search the fun fact it has explored in past so, that it does not have to ask about it again.



##### **MUST TO HAVES:**

1. User should not feel bored, and information should be precise and easy to remember. That's the final output requirement we have received from the user.



##### **Technical requirement:**

1. No specific technical requirement was provided by the user.

&#x09;							

### &#x09;			**Product Features Specifications**

###### 

#### **Features:**

1. **Conversation with Chatbot:**

   1. **How it works:**
   2. It takes the user query, call the LLM to respond to it. 
   3. LLM generates the response and if required to use any Web-Search tool then it should allow LLM to do that.
   4. It should be stateful management conversation style. It should respond to every succeeding question of the user in the context of the past conversation of that chat.
   5. The conversation should be stored in the system.
   6. The conversation ends when user stays inactive for some time, starts a new session or closes the app.
2. **Search over past chats:**

   1. **How it works:**
   2. Search Option to search the content of the past conversations.
   3. User must be able to see the list of the past chats.
   4. User is allowed to provide the keyword for the search. Keyword must be related to fun-fact of that conversation.
   5. Keyword is used to search over the past conversations.
   6. Brings the top 3 relevant conversations.
   7. User can select one of those conversations.
   8. User can continue exploring that fun fact by resuming the conversation.





### &#x09;			**Product System Architecture** 



**Microservices:**

Considering the philosophy of single responsibility principle for the development implementation, we are moving forward with the microservices architecture. Although, we only have two services however, considering the rapid demand of the users and aggressive feedback loop which we want to run after the launch, we would want the teams to aggressively work on different features separately while ensuring the scalability.



1. For now, our services do not interact with each other. However, we will assign them separate resources.
2. To ensure the reliability of the services (especially speed response \& logging conversation in real-time without loosing upon any crash) we will use AWS SQS for queuing the task.
3. Docker containerization for running the stable runtime environment of application.
4. Integrating Kubernetes for the reliability of the docker initialization.
5. Deployment on the Cloud platform. (AWS/AZURE)



### &#x09;			**Deployment Protocol**



**Trunk Based Development:**

1. CI/CD Pipeline using GitLab.
2. Unit tests \& integration tests in placed.
3. Git actions for version control deployment using tags.
4. Code release in staging environment
5. After Q/A, then code goes to the production environment.
6. Monitor performance of deployment using Grafana \& Prometheus.





**Why CI/CD Pipeline:** For the development of this particular product, I want to ensure that I push the feature changes or feature on daily basis \& develop the end-to-end changes such that their impact could be seen on the product. For this, CI/CD is more efficient as compared to the feature-branching. In short, I want to continuously integrate and deploy code.





### &#x09;			**Feature Development Methodology (End-to-End)**



**Development of the feature from scratch:**

1. Define the Backend endpoint for the feature. 
2. Create the dummy data that it can return when endpoint is called.
3. Develop the frontend that can call the feature backend endpoint.
4. It calls the endpoint and gets the data from the backend endpoint of the feature and shows the output on the frontend.



**Development of the feature from dummy to real data:**

1. Now that we have the frontend in place for that particular endpoint we can implement the real functionality on the backend.
2. Now, we will add the business nuances and more nuanced functionality for that feature on daily basis. At this stage, because we have the end-to-end pipeline for the endpoint of the feature in place, we will be able to find out the impact and robustness of the feature on the front end immediately.
3. Now, keep improving \& adding more functionality to the feature using CI/CD pipeline and check its impact on the product.







### &#x09;			**Feature level Implementation**

##### &#x09;					

##### &#x09;					**Create Account / Login Page**



###### **Backend Development:**



**Problem:** In this problem, we are supposed to define an endpoint that will accept the user credentials for account creation, perform some validation tests before storing into the database, and then open a connection to store credentials in the database.

**Components of the process:**

1. Create database \& define model for it.
2. Define the Program that can accept the user credentials and invoke the process to store them and return the response for the user

   1. Program should include some validation rules for the user credentials
   2. Program should ensure user credentials follows the database model
   3. program returns understandable user response
3. Define an endpoint that can accept the user credentials and invoke the program and return the valid response to the frontend.







**Frontend Development:**

**Problem:** In this problem, we need to display the create account / Login Page to the user and then accept the user credentials for either of them, manage the app-state properly for this activity, and send the server request to relevant endpoint securely. Accept the response from the server, and update the app-state accordingly and then display the response.









































