# Development environment for VideoJS player

Simply Django Application for improving VideoJS player. Edx doesn't needed. 

## Setup and run
 
 ```shell
 pip install -r test_requirements
 cd videjs_dev_app/
 python manage.py runserver 0.0.0.0:8000
```


Follow to index page to see list of available players.

All the data for Players is available on settings (`PLAYER_DATA`).
 You can override it in `local_settings.py`.

## Run tests

This Application contains `bok choy` tests also.


TODO
