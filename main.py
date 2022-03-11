from HuginAutomator import HuginAutomator
from flask import Flask
import time
import datetime
import os


CONTEXTS = ('run', 'compute')


def get_env():
    return {'credentials': os.getenv('DROPBOX_TOKEN'),
            'min_s': os.getenv('MIN_STITCH'),
            'max_s': os.getenv('MAX_STITCH'),
            'min_a': os.getenv('MIN_ALIGN'),
            'max_a': os.getenv('MAX_ALIGN')}


def main_loop_compute():
    """
    periodically check dropbox folders to see if there are new projects
    if a new project is found, download + align/build + upload it and continue with the loop
    """
    env = get_env()
    hugin = HuginAutomator(env['credentials'], env['min_s'], env['max_s'], env['min_a'], env['max_a'])
    now = datetime.datetime.now
    start_time = now()
    most_recent_job = start_time
    while now() - most_recent_job < datetime.timedelta(minutes=10):
        if hugin.check_for_stitch():
            hugin.build()
            most_recent_job = now()
        if hugin.check_for_align():
            hugin.align()
            most_recent_job = now()
        time.sleep(5)
    # go to some url to execute cloud function that turns off the instance


app = Flask(__name__)


@app.route('/')
def main():
    env = get_env()
    hugin = HuginAutomator(env['credentials'], env['min_s'], env['max_s'], env['min_a'], env['max_a'])
    if hugin.check_for_stitch():
        return hugin.build()
    elif hugin.check_for_align():
        return hugin.align()
    return "asdf"


if __name__ == "__main__":
    context = os.getenv('CONTEXT')
    if context == CONTEXTS[0]:
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    if context == CONTEXTS[1]:
        main_loop_compute()

