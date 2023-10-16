# CareerHub: Building a Mini Job Portal with MongoDB and Flask!

## I. Purpose
The purpose of this project is to create a Flask application called CareerHub that allows users to manage job postings and query job data from a MongoDB database. This README provides a comprehensive guide to setting up and using the CareerHub application.

## II. Tasks
### Step 1. Schema Design
Initially, I had five separate CSV files: 'companies.csv', 'education_and_skills.csv', 'employment_details.csv', 'industry_info.csv', and 'jobs.csv'. However, before I proceed with importing this data into MongoDB, it's essential to meticulously craft a suitable schema for our dataset. This schema should account for storing key job-related information, including job titles, descriptions, industries, average salaries, locations, and other pertinent fields. To optimize our schema structure for efficiency, I have reorganized the data into three distinct categories: Jobs, Companies, and Industries. The new schema design is structured as follows:

<img width="733" alt="schema" src="https://github.com/minu803/careerhub/assets/111295624/038af60a-d401-4b6f-82c1-e612e48d711d">

### Step 2. Data Transformation and Import
I read all the CSV files and created a consolidated table by performing a join using the primary key 'id'. Next, I extracted the essential columns as defined in the schema design, and these were used to create separate dataframes. Subsequently, I transformed all the entries within the dataframes into JSON format to prepare them for import into the MongoDB environment. These JSON files were also saved for reference. Finally, the data was imported into the Pymongo environment using the following procedure:

```python
# connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["careerhub"]


# define collections
jobs = db["jobs"] 
companies = db["companies"]
industries = db["industries"]

# loop through industries.json rows and insert into MongoDB
with open('industries.json', 'r') as file:
  data = json.load(file)
  for row in data['industries']:
    print(row)
    industries.insert_one(row)

# loop through companies.json rows and insert into MongoDB
with open('companies.json', 'r') as file:
  data = json.load(file)
  for row in data['companies']:
    print(row)
    companies.insert_one(row)


# loop through jobs.json rows and insert into MongoDB
with open('jobs.json', 'r') as file:
  data = json.load(file)
  for row in data['jobs']:
    print(row)
    jobs.insert_one(row)
```
We can verify the successful upload of all entries as follows:

<img width="659" alt="Screenshot 2023-10-15 at 7 37 48 PM" src="https://github.com/minu803/careerhub/assets/111295624/b5df131f-14ac-40ca-bf4a-18e7c667e347">

### Step 3. Flask App
#### Homepage
The project's homepage sets the stage for a user-friendly experience. When users access the default root URL path (/ or http://localhost:5000/), they're greeted with a welcome message. This welcoming message doesn't require complex HTML rendering; instead, it's delivered through a straightforward JSON response.

<img width="820" alt="welcome" src="https://github.com/minu803/careerhub/assets/111295624/a171d49a-0479-4935-a51a-7778e1fd0b5b">

#### Create a Job Post
Empowering users to create new job postings, the system allows input of job details, including title, description, industry, average salary, and location, at http://localhost:5000/create/jobPost. The validation checks have been implemented within the corresponding view function to ensure that essential fields like job titles and industry are never left empty. Once data passes validation, it's inserted into our MongoDB collection, ready for use.

<img width="817" alt="create_job" src="https://github.com/minu803/careerhub/assets/111295624/82ebef33-653f-4eee-bd10-2f75230eb20b">

In our MongoDB backend, we can observe the successful addition of the data.

<img width="532" alt="create_job back" src="https://github.com/minu803/careerhub/assets/111295624/98eefbe1-9ce8-47ce-87ed-d71e12277291">

To verify this, we can execute a search query using the corresponding job_id.

<img width="635" alt="create_job mongo" src="https://github.com/minu803/careerhub/assets/111295624/fe074c11-bfa5-4985-add1-50d58e8c03c2">


#### View Job Details
Users have the ability to explore job details with ease. When they navigate to http://localhost:5000/search_by_job_id/<job_id>, they can effortlessly search for a specific job using its unique job ID.

<img width="815" alt="search_by_job_id" src="https://github.com/minu803/careerhub/assets/111295624/b3812e49-b6f3-486c-87b2-1fadd9c8a5f9">

The executed command can also be observed in the backend.

<img width="579" alt="search_by_job back" src="https://github.com/minu803/careerhub/assets/111295624/5c8175f5-37b2-44f8-9969-1cc338ab2efe">


#### Update Job Details
The updates can be initiated by providing a job title via http://localhost:5000/update_by_job_title. The application then conducts a search in the database for the specified job. If found, it displays the current job details, enabling modifications to fields such as job description, average salary, and location. Following validation, the updated data is promptly reflected in the MongoDB collection.

<img width="816" alt="update" src="https://github.com/minu803/careerhub/assets/111295624/5d3037e1-ed94-4ded-9f30-692f1a73cc90">

Let's observe how the update task is executed. As shown below, we can confirm that the update has been successfully completed.

<img width="635" alt="update mongo" src="https://github.com/minu803/careerhub/assets/111295624/15f6f295-5420-4f10-b5a5-3a700faea472">

#### Remove Job Listing
For those seeking to remove a job listing, we've implemented a user-friendly process. Specifying a job title for deletion can be done via http://localhost:5000/delete_by_job_title. Input validation safeguards the process. If the job is located in the database, users are presented with the job's details and are asked for confirmation before deletion. Upon confirmation, the job is seamlessly removed from the MongoDB collection

In the example below, the specified job title and the new message are created using the GET method.

<img width="816" alt="del-get" src="https://github.com/minu803/careerhub/assets/111295624/c5569eba-9572-4767-9204-d3b97ceae1f5">

Using the delete method, users can delete the entry by setting the key, "confirmation" with the "yes" values.

<img width="824" alt="delete" src="https://github.com/minu803/careerhub/assets/111295624/0a3e1fd8-cca5-4f4a-addd-6de086c6d13c">

Let's check if the delete command has been executed successfully.

<img width="599" alt="delete db" src="https://github.com/minu803/careerhub/assets/111295624/b6c53eeb-39ff-485b-acd7-0bb151b8f078">

#### Salary Range Query
Incorporating a powerful query feature that allows for job filtering based on salary ranges, users can leverage the API by providing minimum and maximum salary values as query parameters to retrieve jobs within their desired salary bracket.

<img width="811" alt="salary" src="https://github.com/minu803/careerhub/assets/111295624/9198c970-d3fa-4982-b96e-8316cea97bbc">


#### Job Experience Level Query
Our project caters to job seekers by providing an experience-based job query. Experience levels, such as 'Entry Level,' 'Mid Level,' and 'Senior Level,' can be specified by users through the experience_level query parameter. Subsequently, the API compiles a list of jobs that align with the provided experience requirement.

<img width="818" alt="experience" src="https://github.com/minu803/careerhub/assets/111295624/75801097-a876-4c17-8274-84f7ebd7f80a">

#### Top Companies in an Industry
For an added layer of insight, a feature has been introduced to identify top companies within a given industry based on their number of job listings. Users can input an industry query parameter, and the API responds by ranking companies in that industry according to the volume of job listings they have.

<img width="818" alt="top companies" src="https://github.com/minu803/careerhub/assets/111295624/c5071a8a-e9d8-4c5d-afc5-62102e74f416">

## III. Use of GenAI
1. **Convert ObjectId:**
When I encountered an error related to JSON serialization, I used Gen AI to understand the correct format to switch. The code converts the "_id" field (an ObjectId) into a string representation, making it JSON-serializable and resolving the issue caused by ObjectId's binary nature when directly serialized to JSON.

2. **delete_by_job_title:**
While I had a general idea of how to delete entries by job_title, the requirement to display job details and request user confirmation added complexity. Gen AI provided valuable insights on tackling this task. I created an additional GET method to display job details and present the confirmation message. In the DELETE method, I focused solely on executing the deletion task.

3. **Comments:**
GenAI assisted me by offering comprehensive explanations of each function's purpose. It also helped me structure and categorize the expected responses that my code could produce, enhancing clarity and organization throughout the development process.

While GenAI was utilized in these specific areas, substantial work and thought processing were also my own contributions, ensuring a balanced and informed use of generative artificial intelligence in the development of this chatbot.


