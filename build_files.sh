echo "BUILD START"

# create a virtual environment named 'venv' if it doesn't already exist
python -m venv venv

# activate the virtual environment
source venv/bin/activate

# build_files.sh
pip install -r requirements.txt

# make migrations
python manage.py migrate
python manage.py collectstatic

echo "BUILD END"