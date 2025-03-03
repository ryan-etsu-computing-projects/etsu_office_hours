#! /bin/bash -

if [ -f ".venv/bin/activate" ]
  then source .venv/bin/activate; echo "Activated venv"
elif [ -f ".venv/Scripts/activate" ]
  then source .venv/Scripts/activate; echo "Activated venv"
else
  echo "Unable to activate venv."
  echo "Please create a Python virtual environment named `.venv` in this directory"
fi

python manage.py runserver 0.0.0.0:8000 --settings=etsu_office_hours.settings_dev
