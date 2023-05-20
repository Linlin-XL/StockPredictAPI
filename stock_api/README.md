# Stock Predict API

### Parameter Configuration
A sample configure in `.env` looks like this:
```text
APP_ENV=<development|uat|production>
DEBUG=<True|False>
DJANGO_SECRET_KEY=<SOME_SECRET>
ALLOWED_HOSTS='<HOST1|HOST2|HOST3>
SQL_ENGINE='django.db.backends.postgresql'
POSTGRES_DB='<SOME_DB>'
POSTGRES_USER='<SOME_USER>'
POSTGRES_PASSWORD='<SOME_POSTWORD>'
POSTGRES_HOST='<SOME_HOST>'
POSTGRES_PORT=5432
```

### Usage

To start stock API web service, for example, run the following on the Terminal:
```sh
python manage.py runserver 0.0.0.0:8000
```

To test the Stock predicted volume using httpie, for example, run the following on the Terminal:
```sh
http POST http://127.0.0.1:8000/api/stock/volumes/ vol_moving_avg=12345 price_rolling_med:=25
```

To test the ETF predicted volume using httpie, for example, run the following on the Terminal:
```sh
http POST http://127.0.0.1:8000/api/etf/volumes/ vol_moving_avg=12345 price_rolling_med:=25
```
