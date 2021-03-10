import time
import os
import re
import deploymentutils as du


from ipydex import IPS, activate_ips_on_exception

# simplify debugging
activate_ips_on_exception()


"""
This script serves to deploy and maintain the django app on an uberspace account.
It is largely based on this tutorial: <https://lab.uberspace.de/guide_django.html>.
"""


# call this before running the script:
# eval $(ssh-agent); ssh-add -t 10m


# -------------------------- Begin Essential Config section  ------------------------

# this file must be changed according to your uberspace accound details (machine name and user name)

cfg = du.get_nearest_config("config.ini")

remote = cfg("remote")
user = cfg("user")

# -------------------------- Begin Optional Config section -------------------------

app_name = cfg("django_app_name")
django_project_name = cfg("django_project_name")

# name of the directory for the virtual environment:
venv = cfg("venv")

# it should not be necessary to change the data below, but it might be interesting what happens.
# (After all, this code runs on your computer/server under your responsibility).

# because uberspace offers many pip_commands:
pip_cmd = "pip3.7"

# -------------------------- </Config section> -------------------------------------------------------------------------
# -------------------------- <Argument Parsing> ------------------------------------------------------------------------

du.argparser.add_argument("-o", "--omit-tests", help="omit test execution (e.g. for dev branches)", action="store_true")
du.argparser.add_argument("-d", "--omit-database",
                          help="omit database-related-stuff (and requirements)", action="store_true")
du.argparser.add_argument("-s", "--omit-static", help="omit static file handling", action="store_true")
du.argparser.add_argument("-x", "--omit-backup",
                          help="omit db-backup (avoid problems with changed models)", action="store_true")
du.argparser.add_argument("-p", "--purge", help="purge target directory before deploying", action="store_true")
du.argparser.add_argument("-r", "--omit-requirements", help="omit installation of requirements", action="store_true")

args = du.parse_args()

# -------------------------- </Argument Parsing> -----------------------------------------------------------------------
# --------------------------- <Path Generation> ------------------------------------------------------------------------

# this is only relevant if you maintain more than one instance

if args.target == "remote":
    # this is where the code will live after deployment
    target_deployment_path = cfg("remote_deployment_path_base")
    target_deployment_path_django = cfg("django_basedir").replace("__PROJECT_BASEDIR__", target_deployment_path)
    static_root_dir = cfg("STATIC_ROOT").replace("__PROJECT_BASEDIR__", target_deployment_path)
    debug_mode = False
    pip_user_flag = ""  # this might be dropped if we use a virtualenv on the remote target
    venv_dir = f"/home/{user}/{venv}"  # this must be absolute path
else:
    # settings for local deployment
    raise NotImplemented
    static_root_dir = ""
    target_deployment_path = os.path.join(local_deployment_workdir, cfg("deployment_dir_name"))
    debug_mode = True
    pip_user_flag = ""  # assume activated virtualenv on local target

    venv_dir = os.path.abspath(os.path.join(local_deployment_workdir, venv))


src_deployment_dir_path = du.get_dir_of_this_file()
src_project_path = du.get_dir_of_this_file(upcount_dir=1)

# this is the root dir of the django sub project (where manage.py lies)
src_django_subdir_path = os.path.join(src_project_path, "django")
src_app_path = os.path.join(src_django_subdir_path, app_name)  # relevant for symlink use case

# base directory for local testing deployment
local_deployment_workdir = os.path.abspath(f"{src_project_path}/../local_testing")

furthter_upload_paths = cfg("furthter_upload_paths", cast=cfg.Csv())

src_instance_specific_path = os.path.join(du.get_dir_of_this_file(), "specific")
target_init_fixture_path = cfg("init_fixture_path").replace("__PROJECT_BASEDIR__", target_deployment_path)

# --------------------------- </Path Generation> -----------------------------------------------------------------------

final_msg = f"Deployment script {du.bgreen('done')}."

if args.target == "remote":

    # generate config-files from templates from some settings

    # generate the uwsgi config file
    tmpl_path = os.path.join("uberspace", "uwsgi", "apps-enabled", "template_mainapp.ini")
    du.render_template(tmpl_path, context=dict(user=user, deployment_dir=target_deployment_path_django,
                                               venv_dir=venv_dir, django_project_name=django_project_name))

    # generate the uwsgi ini-file
    tmpl_path = os.path.join("uberspace", "etc", "services.d", "template_uwsgi.ini")
    du.render_template(tmpl_path, context=dict(venv_abs_bin_path=f"{venv_dir}/bin/"))


# TODO: make a backup of the remote-data
# print a warning for data destruction
du.warn_user(app_name, args.target, args.unsafe, deployment_path=target_deployment_path)


c = du.StateConnection(remote, user=user, target=args.target)

if 1 and args.initial:
    if not args.target == "remote":
        print("\n", du.bred("  The `--initial` option explicitly requires the target==`remote`"), "\n")
        exit()

    # install virtualenv
    c.run(f"{pip_cmd} install --user virtualenv")

    print("create and activate a virtual environment inside $HOME")
    c.chdir("~")

    c.run(f"rm -rf {venv}")
    c.run(f"virtualenv -p python3.7 {venv}")
    c.activate_venv(f"{venv_dir}/bin/activate")

    # this was necessary to prevent errors on uberspace
    c.run(f"pip install --upgrade pip")
    c.run(f"pip install --upgrade setuptools")

    # ensure that the same version of deploymentutils like on the controller-pc is also in the server
    c.deploy_this_package()

    print("\n", "install uwsgi", "\n")
    c.run(f'pip install uwsgi', target_spec="remote")

    print("\n", "upload config files for initial deployment", "\n")

    srcpath1 = os.path.join(src_deployment_dir_path, "uberspace")
    srcpath2 = os.path.join(src_deployment_dir_path, "general")

    # upload config files to $HOME
    filters = "--exclude='README.md' --exclude='*/template_*'"
    c.rsync_upload(srcpath1 + "/", "~", filters=filters, target_spec="remote")
    c.rsync_upload(srcpath2 + "/", "~", filters=filters, target_spec="remote")

    c.run('supervisorctl reread', target_spec="remote")
    c.run('supervisorctl update', target_spec="remote")

    print("waiting 10s for uwsgi to start")
    time.sleep(10)

    res1 = c.run('supervisorctl status', target_spec="remote")

    assert "uwsgi" in res1.stdout
    assert "RUNNING" in res1.stdout

    c.run('uberspace web backend set / --http --port 8000', target_spec="remote")

    # configuring apache to serve /static
    c.run('uberspace web backend set /static --apache', target_spec="remote")

    c.deactivate_venv()

if args.purge:
    if not args.omit_backup:
        print("\n", du.bred("  The `--purge` option explicitly requires the `--omit-backup` option. Quit."), "\n")
        exit()
    elif args.omit_database:
        print("\n", du.bred("  The `--purge` option conflicts  `--omit-database` option. Quit."), "\n")
        exit()
    else:
        answer = input(f"purging <{args.target}>/{target_deployment_path} (y/N)")
        if answer != "y":
            print(du.bred("Aborted."))
            exit()
        c.run(f"rm -r {target_deployment_path}", target_spec="both")

print("\n", "ensure that deployment path exists", "\n")
c.run(f"mkdir -p {target_deployment_path}", target_spec="both")


print("\n", "upload config file", "\n")
c.rsync_upload(cfg.path, target_deployment_path, target_spec="remote")

print("\n", "upload current application files for deployment", "\n")
# omit irrelevant files (like .git)
# TODO: this should be done more elegantly
filters = \
    f"--exclude='.git/' " \
    f"--exclude='.idea/' " \
    f"--exclude='django/django_project/__pycache__/*' " \
    f"--exclude='django/{app_name}/__pycache__/*' " \
    f"--exclude='__pycache__/' " \
    f"--exclude='deployment/' " \
    f"--exclude='_gitignore-docker-test/' " \
    f"--exclude='django/db.sqlite3' " \
    f"--exclude='README.md' " \
    ""

c.rsync_upload(src_django_subdir_path + "/", target_deployment_path_django, filters=filters, target_spec="both")

# rsync instance-specific data (this might overwrite generic data from the project)
c.rsync_upload(src_instance_specific_path + "/", target_deployment_path_django, filters=filters, target_spec="both")

for fup in furthter_upload_paths:
    src_path = fup.replace("__PROJECT_BASEDIR__", src_project_path)
    c.rsync_upload(src_path, target_deployment_path, filters=filters, target_spec="both")

src_path = cfg("PATH_KNOWLEDGEBASE").replace("__PROJECT_BASEDIR__", src_project_path)
c.rsync_upload(src_path, target_deployment_path, filters=filters, target_spec="both")


# ......................................................................................................................

c.activate_venv(f"{venv_dir}/bin/activate", venv_target="both")

x = c.run('python -c "import sys; print(sys.path)"', target_spec="both")


if not args.omit_requirements:
    # scra-specific
    c.chdir(target_deployment_path+"/yamlpyowl")
    c.run(f'pip install -e .', target_spec="remote")

    c.chdir(target_deployment_path+"/scra-backend")
    c.run(f'pip install -e .', target_spec="remote")

    # install django project requirements
    c.chdir(target_deployment_path_django)
    c.run(f'pip install -r requirements.txt', target_spec="both")
    print("\n", "install dependencies", "\n")
    res = c.run(f'pip show django', target_spec="both", warn=False)
    loc = re.findall("Location:.*", res.stdout)
    if args.target == "local" and len(loc) == 0:
        msg = f"{du.bred('Caution:')} django seems not to be installed on local system.\n" \
              f"This might indicate some problem with pip or the virtualenv not activated.\n"
        print(msg)

        cmd = 'python -c "import sys; print(sys.path)"'
        syspath = c.run(cmd, target_spec="local").stdout

        print("This is your current python-path:\n\n", syspath)

        res = input("Continue and install django in that path (N/y)? ")
        if res.lower() != "y":
            print(du.bred("Aborted."))
            exit()

if args.symlink:
    assert args.target == "local"
    c.run(["rm", "-r", os.path.join(target_deployment_path, app_name)], target_spec="local")
    c.run(["ln", "-s", src_app_path, os.path.join(target_deployment_path, app_name)], target_spec="local")

if False and not args.initial and not args.omit_backup:
    # not yet relevant

    print("\n", "backup old database", "\n")
    res = c.run('python manage.py savefixtures', target_spec="both")


if not args.omit_database:
    print("\n", "prepare and create new database", "\n")

    c.chdir(target_deployment_path_django)
    c.run('python manage.py makemigrations', target_spec="both")

    # delete old db
    c.run('rm -f db.sqlite3', target_spec="both")

    # this creates the new database
    c.run('python manage.py migrate', target_spec="both")

    print("\n", "install initial data", "\n")
    c.run(f"python manage.py loaddata {target_init_fixture_path}", target_spec="both")
    c.run(f"python manage.py populate_db_from_ontology --flush", target_spec="both")

if not args.omit_static:
    print("\n", "copy static files to final location", "\n")
    c.run('python manage.py collectstatic --no-input', target_spec="remote")

    if args.target == "remote":
        print("\n", "copy static files to the right place", "\n")
        c.chdir(f"/var/www/virtual/{user}/html")
        c.run('rm -rf static')
        c.run(f'cp -r {static_root_dir} static')

c.chdir(target_deployment_path_django)

if not args.omit_tests:
    print("\n", "run tests", "\n")
    c.run(f'python manage.py test {app_name}', target_spec="both")

if args.target == "local":
    print("\n", f"now you can go to {target_deployment_path} and run `python manage.py runserver", "\n")
else:
    print("\n", "restart uwsgi service", "\n")
    c.run(f"supervisorctl restart uwsgi", target_spec="remote")

print(final_msg)
