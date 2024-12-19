"""
- Since instance_relative_config is set to True, the configuration file(config.py) is expected to be in the instance folder.
- If instance folder does not exist, it will be created during execution. But no configuration file is created in the instance folder.
- The `instance/config.py` will only be used if it exists, otherwise, the default configuration will be used.
- Secret keys and other sensitive information should be stored in the configuration file & should not be committed to the repository.
"""

import os
from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=True)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = False
    # app.config['TESTING'] = False

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Error Handlers
    from app.routes import page_not_found, internal_server_error
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    # Pass app instance during Flask Extension Initialization
    # SQLAlchemy Extension Initialization
    from app.models import db
    db.init_app(app)

    # Bcrypt Extension Initialization
    from app.routes import bcrypt
    bcrypt.init_app(app)

    # Login Manager Extension Initialization
    from app.routes import login_manager
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes import main, auth, user, admin, professional, customer
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(user)
    app.register_blueprint(admin)
    app.register_blueprint(professional)
    app.register_blueprint(customer)

    # for rule in app.url_map.iter_rules():
    #     meth = list(rule.methods)
    #     if 'HEAD' in meth:
    #         meth.remove('HEAD')
    #     if 'OPTIONS' in meth:
    #         meth.remove('OPTIONS')
    #     print(f"@app.route('{rule.rule}', methods = {meth})")

    return app
