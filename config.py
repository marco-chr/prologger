import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET-KEY') or '123456'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'prologger_master.db')
    SQLALCHEMY_BINDS = {}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMPORT_FOLDER = os.path.join(basedir, 'app/import/')
    EXPORT_FOLDER = os.path.join(basedir, 'app/export/')
    REPORT_FOLDER = os.path.join(basedir, 'app/report/')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = ['xls','xlsx']
    DB_PATH = os.path.join(basedir, 'prologger_000.db')
    MASTER_PATH = os.path.join(basedir, 'prologger_master.db')
    BASEDIR = basedir
    APPDIR = basedir + "/app/"
    IMAGES_FOLDER = basedir + "/app/static/images/"
    LOG_FOLDER = basedir + "/app/logs/"
    REPO_FOLDER = basedir + "/app/static/repository/"
    QUERIES_FOLDER = basedir + "/app/queries/"
    ATTACHMENT_FOLDER = basedir + "/app/attachments/"
    MAIL_SCRIPT_FOLDER = basedir + "/app/mail_script/"
    JS_PATH = basedir + "/app/static/js/"
    LOCK_PATH = basedir + "/app/locks/"

    MAILSERVER = 'smtp.gmail.com'
    MAILPORT = '465'
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'prologger.sandbox@gmail.com'
    MAIL_PASSWORD = 'dongately88!'

    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
