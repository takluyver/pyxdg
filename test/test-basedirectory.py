from xdg import BaseDirectory

import os
from os import environ
import unittest
import tempfile, shutil

try:
    reload
except NameError:
    from imp import reload

class BaseDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.environ_save = environ.copy()
    
    def tearDown(self):
        # Restore environment variables
        environ.clear()
        for k, v in self.environ_save.items():
            environ[k] = v
    
    def test_save_config_path(self):
        tmpdir = tempfile.mkdtemp()
        try:
            environ['XDG_CONFIG_HOME'] = tmpdir
            reload(BaseDirectory)
            configpath = BaseDirectory.save_config_path("foo")
            self.assertEqual(configpath, os.path.join(tmpdir, "foo"))
        finally:
            shutil.rmtree(tmpdir)
    
    def test_save_data_path(self):
        tmpdir = tempfile.mkdtemp()
        try:
            environ['XDG_DATA_HOME'] = tmpdir
            reload(BaseDirectory)
            datapath = BaseDirectory.save_data_path("foo")
            self.assertEqual(datapath, os.path.join(tmpdir, "foo"))
        finally:
            shutil.rmtree(tmpdir)
    
    def test_save_cache_path(self):
        tmpdir = tempfile.mkdtemp()
        try:
            environ['XDG_CACHE_HOME'] = tmpdir
            reload(BaseDirectory)
            datapath = BaseDirectory.save_cache_path("foo")
            self.assertEqual(datapath, os.path.join(tmpdir, "foo"))
        finally:
            shutil.rmtree(tmpdir)
    
    def test_load_first_config(self):
        tmpdir = tempfile.mkdtemp()
        tmpdir2 = tempfile.mkdtemp()
        tmpdir3 = tempfile.mkdtemp()
        path = os.path.join(tmpdir3, "wpokewefketnrhruit")
        os.mkdir(path)
        try:
            environ['XDG_CONFIG_HOME'] = tmpdir
            environ['XDG_CONFIG_DIRS'] = ":".join([tmpdir2, tmpdir3])
            reload(BaseDirectory)
            configdir = BaseDirectory.load_first_config("wpokewefketnrhruit")
            self.assertEqual(configdir, path)
        finally:
            shutil.rmtree(tmpdir)
            shutil.rmtree(tmpdir2)
            shutil.rmtree(tmpdir3)
    
    def test_load_config_paths(self):
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, "wpokewefketnrhruit")
        os.mkdir(path)
        tmpdir2 = tempfile.mkdtemp()
        path2 = os.path.join(tmpdir2, "wpokewefketnrhruit")
        os.mkdir(path2)
        try:
            environ['XDG_CONFIG_HOME'] = tmpdir
            environ['XDG_CONFIG_DIRS'] = tmpdir2 + ":/etc/xdg"
            reload(BaseDirectory)
            configdirs = BaseDirectory.load_config_paths("wpokewefketnrhruit")
            self.assertEqual(list(configdirs), [path, path2])
        finally:
            shutil.rmtree(tmpdir)
            shutil.rmtree(tmpdir2)
