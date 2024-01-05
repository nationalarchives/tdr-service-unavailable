if [ $# -eq 0 ]; then
  echo "Please provide an argument (either 'default' or 'xmas')"
  exit 1
fi

mkdir -p package
pip3 install --target package -r requirements-runtime.txt
cd package
zip -r ../deployment.zip .
cd ..

if [ "$1" = "default" ]; then
  zip -g deployment.zip views/index.html
elif [ "$1" = "xmas" ]; then
  cp views/xmas/index.html views/index.html
  zip -g deployment.zip views/index.html
else
  echo "Invalid argument. Please use 'default' or 'xmas'"
  exit 1
fi

zip -g deployment.zip app.py
zip -g deployment.zip static/tna-horizontal-white-logo.svg
zip -g deployment.zip static/main.css
