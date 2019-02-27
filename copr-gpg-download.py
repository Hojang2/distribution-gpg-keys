#!/usr/bin/python3

from copr.v3 import Client
from copr import create_client2_from_params

import requests
import argparse
from argparse import RawTextHelpFormatter
import os.path


def get_gpg(project):
    url = be_url_tmpl.format(**{'username': project.owner, 'project_name': project.name})
    r = requests.get(url)
    return r.text


def gpg_out(isolate_file, file_name, project):
    if isolate_file:
        if not os.path.isfile(file_name):
            with open(file_name, "w") as f:
                f.write(get_gpg(project))

            print("Saved {0}".format(file_name))
        else:
            print("Skipping {0} - already downloaded.".format(file_name))
    elif output_file:
        output_file.write(get_gpg(project))
    else:
        print(get_gpg(project))


def main():
    kwargs = {}

    if args.user:
        kwargs['owner'] = args.user
    if args.project:
        kwargs['name'] = args.project
    _offset = 0
    _limit = 100

    while True:
        if args.api == "3":
            projects = cli.project_proxy.get_list(ownername=None)
            # TODO: Get all projects from copr
            # Now API 3 does not support thi request
        else:
            projects = cli.projects.get_list(offset=_offset, limit=_limit, **kwargs)

        if not projects:
            break

        for project in projects:
            file_name = args.path + "copr-{0}-{1}.gpg".format(project.owner, project.name)

            if "404 Not Found" in get_gpg(project):
                print("Deleting {0} - project key doesn't exist.".format(file_name))
                if os.path.isfile(file_name):
                    print("Skipping {} - already deleted.".format(file_name))
                    os.remove(file_name)
            else:
                gpg_out(args.isolate_files, file_name, project)

        _offset += _limit


parser = argparse.ArgumentParser(description='Download GPG keys for COPR projects.',
                                 formatter_class=RawTextHelpFormatter)
parser.add_argument('-f', '--file', action='store',
                    help='store keys to a file instead of printing to stdout')
parser.add_argument('--api', action='store', default='2',
                    help='version of api(2/3) you want to use.')
parser.add_argument('--feurl', action='store', default='http://copr.fedorainfracloud.org/',
                    help='use this url as baseurl to frontend instead of\nhttp://copr.fedorainfracloud.org/')
parser.add_argument('--beurl', action='store', default='https://copr-be.cloud.fedoraproject.org',
                    help='use this url as baseurl to backend instead of\nhttps://copr-be.cloud.fedoraproject.org')
parser.add_argument('--user', action='store',
                    help='only download gpg keys for projects of this user')
parser.add_argument('--project', action='store',
                    help='only download gpg keys for projects of this name')
parser.add_argument('--isolate-files', action='store_true',
                    help='Each GPG file is stored in separate file.')
parser.add_argument('--path', action='store', default='keys/copr/',
                    help='path to folder where keys are stored')

args = parser.parse_args()

be_url_tmpl = args.beurl+'/results/{username}/{project_name}/pubkey.gpg'

if args.api == "3":

    cli = Client.create_from_config_file()
else:
    cli = create_client2_from_params(root_url=args.feurl)

if args.file:
    output_file = open(args.file, 'w')
else:
    output_file = None
try:
    main()
except KeyboardInterrupt as e:
    pass
