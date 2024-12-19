# General Instructions
## Running the application
- The configuration file will be used only if `app.py` is executed by
    ```shell
    python3 run.py
    ```
    not by
    ```shell
    flask run
    ```
    However the latter can be used to run the application if the configuration file is not needed.
- Since `instance_relative_config` is set to True, the configuration file(`config.py`) is expected to be in the instance folder.
- If instance folder does not exist, it will be created during execution. But no configuration file is created in the instance folder.
- The `instance/config.py` will only be used if it exists, otherwise, the default configuration will be used.
- Secret keys and other sensitive information should be stored in the configuration file & should not be committed to the repository.
## User Interface
- Bootstrap is used for the UI design in the form of compiled minified version of CSS and JS. Refer for more info 👉 [Bootstrap](https://getbootstrap.com/)
- Bootstrap Icons is used as Icon Fonts. Refer for more info 👉 [Bootstrap Icons](https://icons.getbootstrap.com/)
- When experimenting with CSS, it is important to disable CSS caching in the browser.


## Manually creating DB
1. The app will create DB if .db file does not exist in `src/instance` folder and add admin user.
2. If you want to manually create the DB, navigate to instance folder and follow the steps below:
    ```shell
    flask shell
    ```
3. Run the following commands in flask shell:
    ```shell
    from app.models import db
    db.drop_all()
    db.create_all()
    ```

## App Demo


# References
- [Flask Documentation](https://flask.palletsprojects.com/en/3.0.x/)
- [Flask Configuration Handling](https://flask.palletsprojects.com/en/3.0.x/config/#configuration-basics)
- [Flask Error Handling](https://flask.palletsprojects.com/en/3.0.x/errorhandling/#custom-error-pages)
- [Flask Message Flashing](https://flask.palletsprojects.com/en/3.0.x/patterns/flashing/)
- [Template Inheritance](https://flask.palletsprojects.com/en/2.3.x/patterns/templateinheritance/)
- [Flask SQL-Alchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/)
- [SQL Alchemy Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQL-Alchemy handling One-to-Many Relationship](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many)
- [Flask WTForms Documentation](https://wtforms.readthedocs.io/en/2.3.x/)
- [A guide to bringing JavaScript's Power to your Flask app](https://medium.com/@crawftv/javascript-jinja-flask-b0ebfdb406b3)
- [Javascript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- [Javascript in Flask](https://flask.palletsprojects.com/en/3.0.x/patterns/javascript/)