#!/usr/bin/python

import argparse
import json
import os
import random
import subprocess
import sys
import shutil
import errno

'''
Docker client wrapper for Coursera Labs. This script simulates
Coursera Labs docker build and run procedures configured by the manifest.json file.

Examples:

# Build an image:
coursera-lab build [build path]

# Build a Jupyter notebook image with submit button:
coursera-lab build [build path] --add-submit-button

# Run an instance of your built image:
coursera-lab run [build path]

'''

LAB_DEFAULTS_FILE_PATH = os.path.expanduser('~/.coursera/lab_defaults.json')

class Manifest(object):
    def __init__(self, data):
        self.name = data.get('name')
        self.version = data.get('version', None)
        self.http_port = data.get('httpPort')
        self.mounts = [ManifestMount(mountData) for mountData in data.get('mounts', [])]
        self.environment_vars = [ManifestEnvVariable(mountData) for mountData in data.get('environmentVars', [])]

    @property
    def image_tag(self):
        image_tag = self.name
        if self.version:
            image_tag = image_tag + ':' + self.version
        return image_tag


class ManifestMount(object):
    def __init__(self, data):
        self.path = data.get('path')


class ManifestEnvVariable(object):
    def __init__(self, data):
        self.name = data.get('name')
        self.value = str(data.get('value'))


def read_manifest(path):
    '''
    Look for and read the manifest.json file under provided path.

    Return the directory that contains the manifest file, along with its contents.
    '''
    if not path.endswith('manifest.json'):
        return read_manifest(os.path.join(path, 'manifest.json'))
    if not os.path.exists(path):
        raise 'There manifest file at {} does not exist'.format(path)

    with open(path) as manifest_json:
        try:
            manifest_json = json.load(manifest_json)
        except ValueError as e:
            raise ValueError('Error parsing {}: {}'.format(path, e.message)) 

    manifest = Manifest(manifest_json)

    build_dir = os.path.dirname(os.path.abspath(path))

    return (build_dir, manifest)


def build_image(build_dir, image_tag):
    command_parts = [
        ['docker', 'build'],
        ['--platform', 'linux/amd64'],
        ['-t', image_tag],
        [build_dir],
    ]

    print('')
    print(' \\\n    '.join([' '.join(map(str, args)) for args in command_parts]))
    print('')

    command = [arg for arg_group in command_parts for arg in arg_group]
    subprocess.call(command)

def copy_directory(src, dst, ignore=None):
    try:
        shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def execute_build(build_dir, manifest, add_submit_button):
    '''
    Build lab-compatible docker image with build_dir as build context.
    '''
    print('*'*30)
    print('*')
    print('*    Building {} (with submit button: {})...'.format(manifest.image_tag, add_submit_button))
    print('*')
    print('*'*30)

    image_tag = manifest.image_tag
    if add_submit_button:

        share_build_dir = os.path.join(build_dir, 'share')
        # Copy other files from build_dir to build_dir/share, excluding Dockerfile and manifest.json
        copy_directory(build_dir, share_build_dir, ignore=shutil.ignore_patterns('*Dockerfile',
                                                                                 '*manifest.json'))
        # Copy files for adding submit button to share folder under build_dir
        copy_directory('share', share_build_dir)

        build_dir_dockerfile = os.path.join(build_dir, 'Dockerfile')
        tmp_share_build_dir_dockerfile = os.path.join(share_build_dir, 'tmp-Dockerfile')
        share_build_dir_dockerfile = os.path.join(share_build_dir, 'Dockerfile')

        os.rename(src=share_build_dir_dockerfile, dst=tmp_share_build_dir_dockerfile)

        # Create a new Dockerfile with instructions from build_dir and build_dir/share Dockerfile
        with open(share_build_dir_dockerfile, "w") as wf:
            with open(build_dir_dockerfile, "r") as base_rf:
                wf.write(base_rf.read())
            with open(tmp_share_build_dir_dockerfile, "r") as share_rf:
                wf.write("\n")
                wf.write(share_rf.read())


        # Build an image in build_dir/share
        build_image(share_build_dir, image_tag)

        generated_build_dir = os.path.join(build_dir, 'generated')
        if not os.path.exists(generated_build_dir):
            os.mkdir(generated_build_dir)
        generated_dockerfile=os.path.join(generated_build_dir, 'Dockerfile')
        shutil.copy2(src = share_build_dir_dockerfile, dst=generated_dockerfile)

        # Clean up tmp files in build_dir/share
        shutil.rmtree(share_build_dir)
    else:
        # Build an image in build_dir
        build_image(build_dir, image_tag)

def run_lab(manifest):
    exposed_port = str(random.randint(10000, 20000))
    image_tag = manifest.image_tag
    name = manifest.name.replace('/', '_') + '-' + str(exposed_port)
    mount_commands = prompt_for_mounts(manifest)

    print('*'*80)
    print('*')
    print('*    Starting instance of {} listening on localhost:{}'.format(image_tag, exposed_port))
    print('*')
    print('*'*80)

    command_parts = \
        [['docker', 'run']] + \
        [['--name', name]] + \
        [['-p', exposed_port + ':' + str(manifest.http_port)]] + \
        [['-e', var.name + '=' + var.value] for var in manifest.environment_vars] + \
        mount_commands + \
        [[image_tag]]

    print('')
    print(' \\\n    '.join([' '.join(map(str, args)) for args in command_parts]))
    print('')
    
    command = [arg for arg_group in command_parts for arg in arg_group]
    
    try:
        subprocess.call(command)
    except KeyboardInterrupt as e:
        subprocess.call(['docker', 'stop', name])


def prompt_for_mounts(manifest):
    '''
    Prompt the user for file system mount sources. Save choices as lab default
    for convenience. 

    Returns a list of mount commands
    '''
    if len(manifest.mounts) == 0:
        return []
    else:
        print('Tell me which volumes to mount for the following container volumes:')
        lab_defaults = load_lab_defaults(manifest.name)
        if 'mounts_paths' not in lab_defaults:
            lab_defaults['mounts_paths'] = {}
        mount_paths = lab_defaults.get('mounts_paths')
        mount_commands = []
        for mount in manifest.mounts:
            default_path = mount_paths.get(mount.path, None)
            if default_path is None:
                input_path = prompt_user('     {} :\n'.format(mount.path))
            else:
                input_path = prompt_user('        {} (press enter for {}):\n'.format(mount.path, default_path))
            if not input_path:
                local_path = default_path
            else:
                local_path = os.path.expanduser(input_path)
            mount_paths[mount.path] = local_path
            mount_commands.append(['-v', '{}:{}'.format(local_path, mount.path)])

        save_lab_defaults(manifest.name, lab_defaults)
        return mount_commands


def prompt_user(message):
    '''
    Wrapper for `input` (python 3) and `raw_input` (python 2)
    '''
    if sys.version_info.major < 3:
      result = raw_input(message)
    else:
      result = input(message)
    return result


def load_lab_defaults(name):
    if os.path.exists(LAB_DEFAULTS_FILE_PATH):
        with open(LAB_DEFAULTS_FILE_PATH) as file:
            all_lab_defaults = json.load(file)
    else:
        all_lab_defaults = {}

    return all_lab_defaults.get(name, {})


def save_lab_defaults(name, value):
    if os.path.exists(LAB_DEFAULTS_FILE_PATH):
        with open(LAB_DEFAULTS_FILE_PATH) as file:
            try:
                all_lab_defaults = json.load(file)
            except:
                all_lab_defaults = {}
    else:
        all_lab_defaults = {}

    all_lab_defaults[name] = value
    coursera_dir = os.path.expanduser('~/.coursera/')
    if not os.path.exists(coursera_dir):
        os.makedirs(coursera_dir)

    with open(LAB_DEFAULTS_FILE_PATH, 'w') as file:
        json.dump(all_lab_defaults, file)

def run_test(manifest):
    image = manifest.image_tag

    # Rewrite the manifest for unit testing
    unit_test_manifest = manifest

    # Set WORKSPACE_TYPE environment variable to "test"
    workspace_type_set = False
    for e in unit_test_manifest.environment_vars:
        if e.name == 'WORKSPACE_TYPE':
            e.value = 'test'
            workspace_type_set = True
    
    if not workspace_type_set:
        unit_test_manifest.environment_vars.append(ManifestEnvVariable({'name': 'WORKSPACE_TYPE', 'value': 'test'}))

    # Set mount paths to grader and submission
    unit_test_manifest.mounts = [
        ManifestMount({'path': '/shared'})
    ]

    # Only unit tests for nbgrader at this moment
    if image == 'nbgrader':
        # lab handles the rest
        run_lab(unit_test_manifest)
        pass

def main():
    parser = argparse.ArgumentParser(
        description='Docker client wrapper to simulate Coursera Labs build and run procedures.')
    parser.add_argument('action', type=str, help='Either \'build\', \'run\', or \'test\'')
    parser.add_argument('build_path', type=str, help='Path to docker build directory or manifest file')
    parser.add_argument("--add-submit-button", help="Add submit button to when building jupyter notebook image", action="store_true")
    
    args = parser.parse_args()

    (build_dir, manifest) = read_manifest(args.build_path)
    if args.action == 'build':
        execute_build(build_dir, manifest, args.add_submit_button)
    elif args.action == 'run':
        run_lab(manifest)
    elif args.action == 'test':
        run_test(manifest)

if __name__ == '__main__':
    main()
