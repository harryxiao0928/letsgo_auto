
import os
from time import localtime, strftime
import shutil
import re
import zipfile


class Pack:
    """Zip an uitrace project for UDT

    The class Pack can zip the current uitrace project in order to upload UDT, the zip includes the followings:
    - images(.jpg) that used in all .py files, exclude code comment lines
    - all .py files
    - other files/folders, exclude .codecc, .vscode, log, .gitignore, .zip and .DS_Store
    """
    def __init__(self):
        self.cached_imgs = []
        self.current_dir = os.getcwd()
        self.all_py = self.find_py()
        self.all_img = self.find_img()
        self.dir_name = self.mkdir()


    def find_py(self) -> list:
        """Get all .py files under current dir"""
        pattern = re.compile(
            ".codecc|(?!login)(?!log_)(?!jlogcat)log|.vscode|             .git|.history|.pytest_cache|.idea|__pycache__"
            )
        py_files = []
        for root, _, filename in os.walk(self.current_dir):
            for file in filename:
                file_path = os.path.join(root, file)
                if file.endswith(r".py") and file not in ['pack_ct.py', 'pack_udt.py'] and not re.search(pattern, file_path):
                    py_files.append(os.path.join(root[len(self.current_dir)+1:], file))
        return py_files


    def get_img_name(slef, line: str) -> list:
        """Get all project img files"""

        pattern = re.compile(r'[a-zA-Z0-9_-]+.jpg')
        if not line.lstrip().startswith('#'):
            img_name = pattern.findall(line)
            return img_name
        return None


    def check_img(self, img_names: list, file_name: str, lineno: int) -> list:
        """check img file is under project"""
        if not img_names:
            return None
        imgs_path = []
        for img_name in img_names:
            if os.path.exists(os.path.join(self.current_dir, img_name)):
                img_name = os.path.join(self.current_dir, img_name)
            elif os.path.exists(os.path.join(self.current_dir, 'data', 'img', img_name)):
                img_name = os.path.join(self.current_dir, 'data', 'img', img_name)
            else:
                dir = os.path.abspath(file_name)
                dir = os.path.dirname(dir)
                if os.path.exists(os.path.join(dir, img_name)):
                    img_name = os.path.join(dir, img_name)
                elif os.path.exists(os.path.join(dir, 'data', 'img', img_name)):
                    img_name = os.path.join(dir, 'data', 'img', img_name)
                else:
                    img_name = None
                    print(f'checkout your img path in {file_name} - {lineno}, img_name: {img_name}')
            if img_name:
                imgs_path.append(img_name)
        return imgs_path
                

    def find_img(self) -> list:
        """Get all absolute paths of .jpg that are used in code lines"""

        imgs_path = []
        for file in os.listdir(self.current_dir):
            if file.rstrip().endswith('.jpg'):
                img_name = os.path.join(self.current_dir, file)
                self.cached_imgs.append(img_name)
        if os.path.exists(os.path.join(self.current_dir, 'data', 'img')):
            for file in os.listdir(os.path.join(self.current_dir, 'data', 'img')):
                if file.rstrip().endswith('.jpg'):
                    img_name = os.path.join(self.current_dir, 'data', 'img', file)
                    self.cached_imgs.append(img_name)
        for py_file in self.all_py:
            with open(py_file, 'r', encoding='utf-8') as f:
                lineno = 0
                lines = f.readlines()
                for line in lines:
                    lineno += 1
                    img_name = self.get_img_name(line=line)
                    img_path = self.check_img(img_names=img_name, file_name=py_file, lineno=lineno)
                    if not img_path:
                        continue
                    for img in img_path:
                        if img not in imgs_path:
                            imgs_path.append(img)
        for img in imgs_path:
            if img in self.cached_imgs:
                self.cached_imgs.remove(img)
        return self.cached_imgs


    def mkdir(self) -> str:
        """make a dir to store all files under current project for zipping"""
        dir_path = strftime('%Y%m%d%H%M%S', localtime())
        os.makedirs(dir_path)
        return dir_path


    def copy_file(self):
        """Copy all useful files to the specified directory"""

        pattern = re.compile(
            f"{self.dir_name}|.codecc|(?!login)(?!log_)(?!jlogcat)log|.vscode|.gitignore|             .git|.DS_Store|.zip|.history|.pytest_cache|.idea|__pycache__"
            )
        for root, _, filename in os.walk(self.current_dir):
            for file in filename:
                from_path = os.path.join(root, file)
                if from_path in self.cached_imgs:
                    continue
                if not re.search(pattern, from_path):
                    dir_name = os.path.join(self.dir_name, os.path.dirname(from_path)[len(self.current_dir)+1:])
                    # dir_name = self.dir_name + os.path.dirname(from_path)[len(self.current_dir):]
                    to_path = os.path.join(dir_name, file)
                    if not os.path.isdir(dir_name):
                        os.makedirs(dir_name)
                    shutil.copy(from_path, to_path)


    def mkzip(self) -> bool:
        """Zip the specified directory"""

        self.copy_file()
        zip = zipfile.ZipFile(self.dir_name+'.zip', 'w', zipfile.ZIP_DEFLATED)
        for path, _, filenames in os.walk(self.dir_name):
            fpath = path.replace(self.dir_name, '')
            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()
        shutil.rmtree(os.path.join(self.current_dir, self.dir_name))


if __name__ == '__main__':
    p = Pack()
    p.mkzip()

