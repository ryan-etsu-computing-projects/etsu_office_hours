#! /bin/bash -

cd /home/haasrr/repos/etsu_office_hours

if [ -f ".venv/bin/activate" ]
  then source .venv/bin/activate; echo "Activated venv"
elif [ -f ".venv/Scripts/activate" ]
  then source .venv/Scripts/activate; echo "Activated venv"
else
  echo "Unable to activate venv."
  echo "Please create a Python virtual environment named `.venv` in this directory"
fi

# python manage.py runserver 0.0.0.0:8000 --settings=etsu_office_hours.settings_dev
python manage.py runsslserver csciauto1.etsu.edu:8001 --certificate certs/server.crt --key certs/server.key --settings=etsu_office_hours.settings_ssl_dev
