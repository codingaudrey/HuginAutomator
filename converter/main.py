import os
from ConnectionHandlerDropbox import ConnectionHandlerDropbox
from flask import Flask
import zipfile
import glob

"""
Possible improvements
1. return link to what was just made
"""

app = Flask(__name__)

CONV_PATHS = ('/convert-new/', '/converting/', '/align-new/', '/converts-old/')


"""
1. check to see if there are new converts
2. download
3. convert
4. upload
"""
@app.route('/')
def main():
    token = os.getenv('DROPBOX_TOKEN')
    tiffs = '/tiffs/'
    dbx = ConnectionHandlerDropbox(token)
    if not dbx._check_for_new_project(CONV_PATHS[0]):
        return "no projects"
    dbx._move_project(CONV_PATHS[1])
    dbx.project_path_cloud = dbx.fix_path_end(CONV_PATHS[1] + dbx.project_name)
    with zipfile.ZipFile(dbx.download_project(), "r") as z: 
        z.extractall()
    os.system('rawtherapee-cli -t -o {} -c {}'.format(tiffs, dbx.project_name))
    for file in glob.iglob(tiffs + '*.tif'):
        os.rename(file, file + 'f')
    dbx.project_path_cloud = CONV_PATHS[1] + dbx.project_name + '/' + dbx.project_name
    # dbx.dropbox.files_create_folder_v2("/converting/" + dbx.project_name + "/" + dbx.project_name)
    dbx.dropbox.files_create_folder_v2(dbx.project_path_cloud)
    for root, dirs, files in os.walk(tiffs):
        for filename in files:
            # construct the full local path
            local_path = os.path.join(root, filename)
            dbx._upload_handler(local_path, dbx.project_path_cloud)
    dbx._move_project(CONV_PATHS[2])
    dbx.dropbox.files_move_v2(CONV_PATHS[1] + dbx.project_name, CONV_PATHS[3] + dbx.project_name)
    return "completed"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
