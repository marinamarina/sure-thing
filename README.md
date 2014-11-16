Every time I upgrade database, run the following:
db migrate
db update
if new model class added, expose it to shell in the manage.py
insert roles in the shell Role.insert_roles(), check: Role.query_all()