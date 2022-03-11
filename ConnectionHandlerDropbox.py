import ConnectionHandler
import dropbox
from dropbox import files
import os
import random

"""
globals for the mvp
"""

INITIAL_FOLDER = ''
BUILD_PATHS = ('/stitch-new/', '/stitching/', '/stitched/', '/stitch-failed/')
ALIGN_PATHS = ('/align-new/', '/aligning/', '/aligned/', '/align-failed/')
MAX_SINGLE_UPLOAD_SIZE = 100000000  # 100MB
CHUNK_SIZE = 100000000  # 100MB


class ConnectionHandlerDropbox(ConnectionHandler.ConnectionHandler):
    def __init__(self, credentials):
        super().__init__()
        self.credentials = credentials
        self.path_projects  = INITIAL_FOLDER
        self.path_new_build = BUILD_PATHS[0]
        self.path_building  = BUILD_PATHS[1]
        self.path_built     = BUILD_PATHS[2]
        self.path_build_failed = BUILD_PATHS[3]
        self.path_new_align = ALIGN_PATHS[0]
        self.path_aligning  = ALIGN_PATHS[1]
        self.path_aligned   = ALIGN_PATHS[2]
        self.path_align_failed = ALIGN_PATHS[3]
        self.dropbox = self._connect_to_cloud_storage()
        self.local_zip = None

    def _connect_to_cloud_storage(self):
        return dropbox.Dropbox(self.credentials)

    def _check_for_new_project(self, path, min_images, max_images):
        """
        to improve race conditions, it grabs random project instead of first project from list of projects
        :param path: (in this usage, it comes from BUILD_PATHS[0] or ALIGN_PATHS[0])
        :param min_images:
        :param max_images:
        :return bool:
        """
        path = self.fix_path_end(path)
        available_projects = self.dropbox.files_list_folder(path, recursive=False).entries
        if len(available_projects) == 0:
            return False
        random_project_number = random.randint(0, len(available_projects) - 1)
        for _ in available_projects:
            random_project_number = divmod(random_project_number + 1, len(available_projects))
            folder_contents = self.dropbox.files_list_folder(self.fix_path_end(path) +
                                                             available_projects[random_project_number]).entries
            if max_images > self.count_images_in_folder(folder_contents) >= min_images:
                self.project_name = available_projects[random_project_number]._name_value
                self.project_path_cloud = path + self.project_name
                return True
        return False

    def download_project(self):
        self.local_zip = self.project_name + '.zip'
        self.dropbox.files_download_zip_to_file(self.local_zip, self.project_path_cloud)
        return self.local_zip

    def _move_project(self, path):
        return self.dropbox.files_move_v2(self.project_path_cloud, self.fix_path_end(path) + self.project_name)

    def _upload_handler(self, local_path, cloud_path):
        with open(local_path, "rb") as f:
            filename = local_path.split('/')[-1]
            dest_path = self.fix_path_end(cloud_path) + filename
            file_size = os.stat(local_path).st_size
            if file_size < MAX_SINGLE_UPLOAD_SIZE:
                return self.dropbox.files_upload(f.read(), dest_path, mode=files.WriteMode.overwrite)  # autorename=True
            else:
                upload_session_start_result = self.dropbox.files_upload_session_start(f.read(CHUNK_SIZE))
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=f.tell())
                commit = dropbox.files.CommitInfo(path=dest_path, mode=files.WriteMode.overwrite)
                while f.tell() < file_size:
                    if file_size - f.tell() <= CHUNK_SIZE:
                        print('uploading the last one!')
                        return self.dropbox.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                    else:
                        print('uploading a thing!')
                        self.dropbox.files_upload_session_append_v2(f.read(CHUNK_SIZE), cursor, False)
                        cursor.offset = f.tell()
