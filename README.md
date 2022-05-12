## TDR Service Unavailable Page

This is the repository for the service unavailable page and the Jenkins files to deploy it. It's split into the following sections.

`css-src/` The sass files used to build the css. This is copied from the front end

`static/` The two images we need and also holds the css file once built.

`test/` The python tests

`views/` The html for the service unavailable page

`app.py` The bottle code for running the web server in lambda.

`.github/workflows/build.yml` The GitHub actions job to build the css, create a zip file and upload it to S3.

`.github/workflows/deploy.yml` The GitHub actions job to deploy the zip file to lambda.

`.github/workflows/test.yml` Runs the tests for branch builds.

`.github/workflows/run.yml` Switches the load balancer listener to either the front end target group or the service unavailable target group depending on the parameters.

### Running it locally
1. You need to be running python 3

Linux:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_locally.py
```
Mac:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run_locally.py
```

2. Run `npm install`

3. then `npm run build` or `npm run build-css` (to build the css specifically)

The page will be available on `http://localhost:8080`

