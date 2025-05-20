import os
import shutil


def copy_install(config, **kwargs) -> None:
    site_dir = config['site_dir']
    shutil.copy('docs/assets/install.sh', os.path.join(site_dir, 'get'))
