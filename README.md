## TDR Service Unavailable Page

This is the repository for the service unavailable page and the Jenkins files to deploy it. It's split into the following sections.

`css-src/` The sass files used to build the css. This is copied from the front end

`static/` The two images we need and also holds the css file once built.

`test/` The python tests

`views/` The html for the service unavailable page

`app.py` The bottle code for running the web server in lambda.

`Jenkinsfile-deploy` The deploy Jenkins job for a lambda.

`Jenkinsfile-test` Runs the tests for branch builds. For the main branch, it builds the css and then creates a zip file and uploads it to S3.

`Jenkinsfile-service-unavailable` Switches the load balancer listener to either the front end target group or the service unavailable target group depending on the parameters.

### Running it locally
You need to be running python 3
```bash
python -m venv venv
source venv/bin/activate
pip install requirements.txt
python run_locally.py
```
The page will be available on `http://localhost:8080`

