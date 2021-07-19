mkdir -p package
pip3 install --target package -r requirements-runtime.txt
cd package
zip -r ../deployment.zip .
cd ..
zip -g deployment.zip app.py
zip -g deployment.zip views/index.html
zip -g deployment.zip static/tna-horizontal-white-logo.svg
zip -g deployment.zip static/main.css
