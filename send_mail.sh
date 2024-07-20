#!/bin/sh

WORKON_HOME=/root/djangoapps/
PROJECT_ROOT=/root/djangoapps/mmiradio
# activate virtual environment
#. $WORKON_HOMEenv/mmiradio/bin/activate

cd $PROJECT_ROOT
/root/djangoapps/env/mmiradio/bin/python manage.py send_mail
/root/djangoapps/env/mmiradio/bin/python manage.py retry_deferred