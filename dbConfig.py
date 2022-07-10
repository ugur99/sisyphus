### config.py ###
# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
# DATABASE_URI = 'postgresql://sisyphus:L59aPWqAX3@my-release-postgresql.ugur.svc.cluster.local:5432/flask_db'

CONFIG = {
   'postgresUrl':'postgresql.sisyphus.svc.cluster.local:5432',
   'postgresUser':'sisyphus',
   'postgresPass':'L59aPWqAX3',
   'postgresDb': 'sisyphus'
}