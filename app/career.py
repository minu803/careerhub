'''Module for serving API requests'''

from app import app
from bson.json_util import dumps, loads
from flask import request, jsonify
import json
import ast # helper library for parsing data from string
from importlib.machinery import SourceFileLoader
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# 1. Connect to the client
client = MongoClient(host="localhost", port=27017)

# Import the utils module
utils = SourceFileLoader('*', './app/utils.py').load_module()

# 2. Select the database
db = client.careerhub

# Select the collection: jobs
jobs = db.jobs

# Select the collection: companies
companies = db.companies

# Select the collection: industries
industries = db.industries


# Route decorator that defines which routes should be navigated to this function
@app.route("/") # '/' for directing all default traffic to this function get_initial_response()
def get_initial_response():
    '''
    Endpoint to get the initial response.
    ---
    Purpose: 
    - Provides a welcome message to the users.
    '''
    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': '200',
        'message': 'Welcome to class on CareerHub MongoDB'
    }
    resp = jsonify(message)
    # Returning the object
    return resp



@app.route("/create/jobPost", methods=['POST'])
def create_job_post():
    '''
    Function to create new job post(s)
    ---
    Purpose: 
    - Creates new job post(s) in the MongoDB.
    Accepted Parameters:
    - JSON request body containing job post data.
    Potential Responses:
    - 201: Successful creation with a list of IDs.
    - 400: Bad request if the request body is missing or invalid.
    - 500: Server error in case of an exception.
    
    '''
    try:
        # Create new job post
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as request body is not available
            # Add message for debugging purpose
            return "", 400
        
        # Validate the job post data
        required_fields = ['job_id','title']
        missing_fields = [field for field in required_fields if field not in body or not body[field]]

        if missing_fields:
            return f"Bad request: Missing or empty fields: {', '.join(missing_fields)}", 400

        # Insert many field into the body
        record_created = jobs.insert_many(body)

        if record_created:
            inserted_id = record_created.inserted_ids
            # Prepare the response
            if isinstance(inserted_id, list):
                # Return list of Id of the newly created item
                ids = []
                for _id in inserted_id:
                    ids.append(str(_id))
                return jsonify(ids), 201
            else:
                # Return Id of the newly created item
                return jsonify(str(inserted_id)), 201
    except Exception as e:
        # Error while trying to create customers
        # Add message for debugging purpose
        print(e)
        return 'Server error', 500



@app.route("/search_by_job_id/<job_id>", methods=['GET'])
def get_by_job_id(job_id):
    '''
    Endpoint to retrieve job details by job ID.
    ---
    Purpose: 
    - Retrieves job details from MongoDB by job ID.
    Accepted Parameters:
    - job_id: The job ID to search for.
    Potential Responses:
    - 200: Successful retrieval of job details.
    - 404: Job not found.
    - 400: Bad request in case of an exception.
    '''
    try:
        # Convert string to int
        job_id_int = int(job_id)
        
        # Query the document
        result = jobs.find_one({"job_id": job_id_int})
        
        # If document not found
        if not result:
            return jsonify({"message": "Document not found"}), 404
        
        # Convert ObjectId to string for JSON serialization
        result['_id'] = str(result['_id'])
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route('/update_by_job_title', methods=['POST'])
def update_job_by_title():
    '''
    Endpoint to update job details by job title.
    ---
    Purpose: 
    - Updates job details in MongoDB by job title.
    Accepted Parameters:
    - Form data containing job title, description, average_salary, and location.
    Potential Responses:
    - 200: Successful update with the current job info.
    - 404: Job not found.
    - 500: Server error in case of an exception.
    '''    
    try:
        # Fetch the job title from the POST request's form data.
        job_title = request.form.get('title')
        # Query the database to find the job by title
        job = jobs.find_one({"title": job_title})
        # Return a response if the job is not found in the database
        if job is None:
            return jsonify({"message": "Job not found"}), 404
        
        # Fetch new description, average_salary and location from the POST request's form data.
        description = request.form.get('description')
        salary = request.form.get('average_salary')
        location = request.form.get('location')
        
        # Show job's existing details
        current_job_info = {
            "title": job['title'],
            "description": job.get('description', ''),
            "average_salary": job.get('average_salary', ''),
            "location": job.get('location', '')
        }
        # Update fields if new information is provided
        if description:
            job['description'] = description
        if salary:
            job['average_salary'] = int(salary)
        if location:
            job['location'] = location

        # Modify the job data in the database
        jobs.update_one({"title": job_title}, {"$set": job})
        return jsonify({"message": "Job details updated successfully",
                        "current_job_info": current_job_info}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/jobs_experience', methods=['GET'])
def get_jobs_experience():
    '''
    Endpoint to retrieve jobs by experience level.
    ---
    Purpose: 
    - Retrieves jobs from MongoDB based on experience level.
    Accepted Parameters:
    - job_experience: The experience level to filter by.
    Potential Responses:
    - 200: Successful retrieval of jobs.
    - 400: Bad request if experience parameter is missing.
    '''    
    experience = request.form.get('job_experience')
    
    if not experience:
        return jsonify({"error": "Experience parameter is required"}), 400

    job_results = jobs.find({
        "experience_level": experience
           
    }) 

    # Convert ObjectId to string for each document
    results = []
    for document in job_results:
        document["_id"] = str(document["_id"])
        results.append(document)

    return jsonify(list(results))


@app.route("/delete_by_job_title", methods=['GET','DELETE'])
def remove_job():
    '''
    Endpoint to delete a job by job title.
    ---
    Purpose: 
    - Deletes a job from MongoDB by job title.
    Accepted Parameters:
    - job_title: The job title to delete.
    - confirmation: Confirmation for deletion (required for DELETE request).
    Potential Responses:
    - GET:
      - 200: Confirmation message if job found.
      - 404: Job not found.
    - DELETE:
      - 204: Successful deletion.
      - 404: Job not found.
      - 400: Bad request if confirmation is missing or incorrect.
      - 500: Server error in case of an exception.
    '''
    try:
        if request.method == 'GET':
            # Get the job title from the request
            job_title = request.form.get('job_title')

            # Query the database to find the job by title
            job = jobs.find_one({"title": job_title})
            
            # Return a response if the job is not found in the database
            if job is None:
                return jsonify({"message": "Job not found"}), 404
            
            # Convert ObjectId to string for JSON serialization
            job['_id'] = str(job['_id'])
    
            # Fetch confirmation from the POST request's form data.
            message = {
                "msg": "If you want to delete this item, please confirm!!",
                "job": job
            }

            return jsonify(message)  

        elif request.method == 'DELETE':            
            # Get the job title from the request
            job_title = request.form.get('job_title')

            # Query the database to find the job by title
            job = jobs.find_one({"title": job_title})
            
            # Return a response if the job is not found in the database
            if job is None:
                return jsonify({"message": "Job not found"}), 404
            
            # Fetch confirmation from the POST request's form data.
            description = request.form.get('confirmation')

            if not description:
                return jsonify({"error": "Confirmation is required"}), 400

            if description == "yes":
                # Delete the job
                delete_job = jobs.delete_one({"title": job_title})
                if delete_job.deleted_count > 0 :
                    # Return a success message
                    return jsonify({"message": f"Job '{job_title}' has been successfully deleted"}), 204
                else:
                    # Resource not found
                    return jsonify({"message": "Job not found"}), 404
            else:
                return jsonify({"message": "Job not deleted"}), 200
        
    except Exception as e:
        # Error while trying to delete the resource
        # Add message for debugging purpose
        print(e)
        return "", 500

@app.route('/jobs_by_salary_range', methods=['GET'])
def get_jobs_by_salary_range():
    '''
    Endpoint to retrieve jobs by salary range.
    ---
    Purpose: 
    - Retrieves jobs from MongoDB based on salary range.
    Accepted Parameters:
    - min_salary: The minimum salary in the range.
    - max_salary: The maximum salary in the range.
    Potential Responses:
    - 200: Successful retrieval of jobs.
    - 400: Bad request if min_salary or max_salary parameters are missing.
    '''
    min_salary = request.form.get('min_salary')
    max_salary = request.form.get('max_salary')

    if not min_salary or not max_salary:
        return jsonify({"error": "Both min_salary and max_salary parameters are required"}), 400

    job_results = jobs.find({
        "average_salary": {
            "$gte": int(min_salary),
            "$lte": int(max_salary)
        }
    }, projection={"_id": 1, "title": 1})  # Only return the _id and title fields

    # Convert ObjectId to string for each document
    results = []
    for document in job_results:
        document["_id"] = str(document["_id"])
        results.append(document)

    return jsonify(list(results))


@app.route('/top_companies', methods=['GET'])
def get_top_companies():
    '''
    Endpoint to retrieve top companies in an industry.
    ---
    Purpose: 
    - Retrieves top companies based on industry from MongoDB.
    Accepted Parameters:
    - industry: The industry to filter by.
    Potential Responses:
    - 200: Successful retrieval of top companies.
    - 400: Bad request if the industry parameter is missing.
    '''
    # Extract the 'industry' parameter from the request's form data
    industry = request.form.get('industry')

    # Check if 'industry' parameter is missing or empty
    if not industry:
        # Return a JSON response with an error message and a status code 400 (Bad Request)
        return jsonify({"error": "The industry parameter is required"}), 400

    # Define a MongoDB aggregation pipeline to retrieve top companies in the specified industry
    pipeline = [
        # Match documents that have a matching 'industry_name' field
        {"$match": {"industry_name": industry}},
        # Group documents by 'name' and calculate the count of documents in each group
        {"$group": {"_id": "$name", "job_count": {"$sum": 1}}},
        # Sort the results in descending order based on the 'job_count'
        {"$sort": {"job_count": -1}}
    ]
    # Execute the aggregation pipeline on the 'jobs' collection and store the results
    results = list(jobs.aggregate(pipeline))
    
    # Return a JSON response with the results of the aggregation
    return jsonify(results)




