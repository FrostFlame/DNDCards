echo "BUILD START"

# create a virtual environment named 'venv' if it doesn't already exist
python3.12 -m venv venv

# activate the virtual environment
source venv/bin/activate

# build_files.sh
pip install setuptools
pip install -r requirements.txt

# make migrations
python3.12 manage.py migrate
python3.12 manage.py collectstatic

echo cd

echo "BUILD END"