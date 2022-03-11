import os
import zipfile
import glob

import ConnectionHandlerDropbox

"""
Possible improvements:
1. return link to what was just made in dropbox
"""


DEFAULT_CONNECTION_TYPE = 'DROPBOX'
SUPPORTED_CONNECTION_TYPES = ('DROPBOX',)
# LOCAL_PROJECTS_PATH = os.path.expanduser('~/hugin-automator')
LOCAL_PROJECTS_PATH = '/hugau/'


FILE_TYPE = '.tiff'
TASK_TYPES = ('stitch', 'align')
TASK_STAGES = ['new', 'in-progress', 'built']


class HuginAutomator:
    def __init__(self, credentials, min_stitch, max_stitch, min_align, max_align, connection_type=DEFAULT_CONNECTION_TYPE,
                 project_root=LOCAL_PROJECTS_PATH, filetype=FILE_TYPE):
        self.connection_type = connection_type
        assert connection_type in SUPPORTED_CONNECTION_TYPES
        self.credentials = credentials
        self.min_stitch = min_stitch
        self.max_stitch = max_stitch
        self.min_align = min_align
        self.max_align = max_align
        self.conn = ConnectionHandlerDropbox.ConnectionHandlerDropbox(self.credentials) \
            if self.connection_type.lower() == SUPPORTED_CONNECTION_TYPES[0].lower() else None

        self.project_root = project_root
        self.filetype = filetype
        self.curdir = None
        self.stages = None
        self.stage = None
        self.task_type = None
        self.reset()

    def reset(self):
        """
        reconnects to conn in case of timeouts
        """
        os.chdir(self.project_root)
        self.curdir = os.getcwd()
        if self.connection_type.lower() == SUPPORTED_CONNECTION_TYPES[0].lower():
            self.conn = ConnectionHandlerDropbox.ConnectionHandlerDropbox(self.credentials)
        self.stages = TASK_STAGES
        self.stage = self.stages[0]
        self.task_type = None

    def get_project(self):
        self.iterate_stage()
        zip_name = self.conn.download_project()
        with zipfile.ZipFile(zip_name, "r") as z:
            z.extractall()
        os.chdir(zip_name[:-4])
        self.tif_to_tiff()

    def check_for_stitch(self):
        return self.conn.check_for_new_build(self.min_stitch, self.max_stitch)

    def check_for_align(self):
        return self.conn.check_for_new_align(self.min_align, self.max_align)

    def iterate_stage(self):
        self.stage = self.stages[self.stages.index(self.stage) + 1]
        if self.task_type == TASK_TYPES[0]:
            if self.stage == self.stages[1]:
                self.conn.move_project_build_in_progress()
            else:
                self.conn.move_project_built()
        elif self.task_type == TASK_TYPES[1]:
            if self.stage == self.stages[1]:
                self.conn.move_project_align_in_progress()
            else:
                self.conn.move_project_aligned()

    def build(self):
        self.task_type = TASK_TYPES[0]
        self.get_project()
        try:
            self.stitch_pano(self.conn.project_name)
            upload_local_path = self.conn.project_name + self.filetype
            '''the following commented code will be re-added when time allows'''
            # if stitch_result:
            #     upload_local_path = self.conn.project_name + self.filetype
            # else:
            #     upload_local_path = 'output/{}'.format(self.zip_for_upload(self.find_failure_logs()))
            self.conn.upload_build_outputs(upload_local_path)
            self.iterate_stage()
            output = 'output {} to {}'.format(self.conn.project_name, self.conn.project_path_cloud)
            self.reset()
            return output
        except Exception as e:
            self.conn.move_project_build_failed()
            print(e)
            return str(e)

    def stitch_pano(self, output_prefix):
        pto_name = "\"" + self.find_the_pto() + "\""
        output_prefix = "\"" + output_prefix + "\""
        command = "hugin_executor -s -p=%s %s" % (output_prefix, pto_name)
        os.system(command)
        self.tif_to_tiff()
        return os.path.isfile(output_prefix + self.filetype)

    def align(self):
        self.task_type = TASK_TYPES[1]
        self.get_project()
        # align
        try:
            try:
                pto = self.find_the_pto()
                if pto != self.conn.project_name + ".pto":
                    new_pto_name = self.conn.project_name + ".pto"
                    os.rename(pto, new_pto_name)
                    pto = new_pto_name
            except FileNotFoundError:
                pto = self.conn.project_name + ".pto"
                os.system("pto_gen *%s --output=%s" % (self.filetype, pto))
                try:
                    self.find_the_pto()
                except FileNotFoundError:
                    raise Exception("pto failed to be generated")

            os.system("hugin_executor --assistant %s" % pto)

            logs = self.find_failure_logs()
            if logs is None:
                self.conn.upload_align_results(self.find_the_pto())
            else:
                zipped = self.zip_for_upload(logs + [self.find_the_pto()])
                self.conn.upload_align_results('output/' + zipped)
            self.conn.move_project_aligned()
            self.reset()
        except Exception as e:
            self.conn.move_project_align_failed()
            print(e)
            return str(e)

    def zip_for_upload(self, files):
        os.mkdir('output')
        zip_name = self.conn.project_name + '.zip'
        [os.rename(file, 'output/' + file) for file in files]
        ziph = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk('output/'):
            for file in files:
                ziph.write(os.path.join(root, file))
        if os.path.isfile(self.conn.project_name + '.zip'):
            return zip_name
        raise Exception('zip failed to be generated')

    def update_curdir(self):
        self.curdir = os.getcwd()

    @staticmethod
    def find_the_pto(folder=""):
        """
        searches current directory for a file ending in .pto
        """
        for file in glob.iglob(folder + '*.pto'):
            return file
        raise FileNotFoundError
        # make a new pto, unless it is building, then fail

    @staticmethod
    def find_failure_logs():
        logs = [file for file in glob.iglob('*.log')]
        if len(logs) == 0:
            return None
        return logs

    @staticmethod
    def tif_to_tiff():
        for file in glob.iglob('*.tif'):
            os.rename(file, file + 'f')
