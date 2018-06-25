### Description

eGovernment platform “Rozumne Misto” is an all-Ukrainian online platform of e-dem, e-gov and e-services for citizens, local governments, business and NGOs.
Effective tool for development partnership between state governance, citizens and business. 


### Document reference for modules used

##Design  
https://almsaeedstudio.com/themes/AdminLTE/index2.html

### Installation
```
1. Import from 'for_deploy' folder SQL-dump to your MySQL base (called 'weunion' by default)
2. If you're using the WindowsOS install Mysql connector and XMLlib firstly: pip install mysqlclient-1.3.7-cp34-none-win_amd64.whl ,
lxml-3.6.0-cp34-cp34m-win_amd64.whl
3. Than install all requirements: pip install -r requirements.txt
4. Rename mysqldb.conf.sample to mysqldb.conf. Change if you want db-name/login and pass.
That's it! If you have any question feel free to contact with us through email - evgeniy@rozumnemisto.org


##PRODUCTION SERVER
```
Then run the project 
```
#uwsgi --ini /etc/uwsgi/weunion-pub.ini
```
Stop project
```
#uwsgi --stop /tmp/master-weunion.pid
```
Log file
```
/var/log/uwsgi/weunion.log
```
Or for local instance
```
python manage.py runserver
```
sudo nginx restart
