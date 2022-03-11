IMAGE_TYPES = ('.cr2', '.tiff', '.tif', '.jpg', '.png')


class ConnectionHandler:
    def __init__(self):
        self.path_all_projects = None
        self.path_new_build = None
        self.path_building = None
        self.path_built = None
        self.path_build_failed = None
        self.path_new_align = None
        self.path_aligning = None
        self.path_aligned = None
        self.path_align_failed = None
        self.project_path_cloud = None
        self.project_name = None
        self.credentials = None
        self.init()

    def reset(self):
        pass

    def _connect_to_cloud_storage(self):
        pass

    def _check_for_new_project(self, path, min_images, max_images):
        pass

    def check_for_new_align(self, min_images, max_images):
        return self._check_for_new_project(self.path_new_align, min_images, max_images)

    def check_for_new_build(self, min_images, max_images):
        return self._check_for_new_project(self.path_new_build, min_images, max_images)

    def download_project(self):
        pass

    def _move_project(self, new_path):
        pass

    def move_project_build_in_progress(self):
        result = self._move_project(self.path_building)
        self.project_path_cloud = self.path_building + self.project_name
        return result

    def move_project_built(self):
        result = self._move_project(self.path_built)
        self.project_path_cloud = self.path_built + self.project_name
        return result

    def move_project_align_in_progress(self):
        result = self._move_project(self.path_aligning)
        self.project_path_cloud = self.path_aligning + self.project_name
        return result

    def move_project_aligned(self):
        result = self._move_project(self.path_aligned)
        self.project_path_cloud = self.path_aligned + self.project_name
        return result

    def move_project_align_failed(self):
        result = self._move_project(self.path_align_failed)
        self.project_path_cloud = self.path_align_failed + self.project_name
        return result

    def move_project_build_failed(self):
        result = self._move_project(self.path_new_build)
        self.project_path_cloud = self.path_build_failed + self.project_name
        return result

    def _upload_handler(self, local_path, cloud_path):
        pass

    def upload_align_results(self, local_path):
        return self._upload_handler(local_path, self.fix_path_end(self.path_aligning) + self.project_name)

    def upload_build_outputs(self, local_path):
        return self._upload_handler(local_path, self.fix_path_end(self.path_building) + self.project_name)

    def get_project_name(self):
        return self.project_name

    def get_project_path_cloud(self):
        return self.project_path_cloud

    @staticmethod
    def fix_path_end(path):
        return path if path[-1] == '/' else path + '/'

    @staticmethod
    def count_images_in_folder(filenames):
        image_count = 0
        for file in filenames:
            if file[:-3].lower() in IMAGE_TYPES or file[:-4].lower() in IMAGE_TYPES:
                image_count += 1
        return image_count

    def init(self):
        pass
