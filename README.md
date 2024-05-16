Activate the python environment
`.\.venv\Scripts\activate`

Install the requirement
`pip install -r requirements.txt`
`npm install`

Change this file name .flaskenv.tmp to  .flaskenv


Run the following command to compile and watch for changes for the Tailwind CSS file:  
`npx tailwindcss -i ./app/static/src/input.css -o ./app/static/dist/css/output.css --watch`

Migrate db
`flask db migrate`

Run flask
`flask run`

Generate admin
``` python
from app import app, db
from app.models import User
import sqlalchemy as sa
app.app_context().push()
u = User(username='admin')
u.set_password('admin')
db.session.add(u)
db.session.commit()
```


Add the documents you want


