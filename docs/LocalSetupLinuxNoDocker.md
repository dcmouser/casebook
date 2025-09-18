# Local setup (Linux, no Docker)


__*Note:*__
- This document assumes that Django projects are kept in a local `django` directory. However, this is a personal choice, and not required.
- The setup described here has been primarily adapted from the casebook repository's standalone Docker setup (see the [Dockerfile](https://github.com/dcmouser/casebook/blob/main/hldjango/docker/hlweb_standalone/Dockerfile)).


## 1.
Clone (or fork and clone) the repository, for example:
```
cd ~/django
git clone https://github.com/dcmouser/casebook.git
```

Result:
```
Receiving objects: 100% (14016/14016), 286.38 MiB

cd ~/django/casebook
491M    hldjango/

cd ~/django/casebook/.git/objects
287M    pack/
```

## 2.
If necessary, install [Poetry](https://python-poetry.org/docs/#installation).


## 3.
Edit `~/django/casebook/hldjango/pyproject.toml` and:

### i.
Change:
```
readme = "README.md"
```
to:
```
readme = "../README.md"
```

### ii.
Add (at the end of the `[tool.poetry]` section):
```
package-mode = false
```

__*Note:*__ without these changes a message is displayed when running `poetry install`:
```
Installing the current project: hldjango (0.1.0)
Error: The current project could not be installed: Readme path `~/django/casebook/hldjango/README.md` does not exist.
If you do not want to install the current project use --no-root.
If you want to use Poetry only for dependency management but not for packaging, you can disable package mode by setting package-mode = false in your pyproject.toml file.
If you did intend to install the current project, you may need to set `packages` in your pyproject.toml file.
```

## 4.
Install packages:
```
cd ~/django/casebook/hldjango
poetry install
```

Result:
```
Creating virtualenv hldjango-4NrtnqJf-py3.12 in ~/.cache/pypoetry/virtualenvs
Package operations: 85 installs, 0 updates, 0 removals

144M    hldjango-4NrtnqJf-py3.12/
```

## 5.
Create a directory for database files:
```
mkdir ~/django/casebook/hldjango/db
```

## 6.
Make database migrations:
```
cd ~/django/casebook/hldjango/code
poetry run python manage.py migrate --settings=hldjango.settingsdir.standalone_docker
```

__*Note:*__
- the repository contains various custom settings files, which are located in
`~/django/casebook/hldjango/code/hldjango/settingsdir`.
- The default `settings.py` file is located at `~/django/casebook/hldjango/code/hldjango/settings.py`.
However, this is not used. Instead, as `settings.py` says, "you need to overrirde and specify which settings/file to use when invoking manage.py". Here I choose `standalone_docker.py` because, despite the filename and not actually using Docker locally, this file provides the settings needed. It:
  - Sets `JR_DJANGO_DEBUG`
  - Imports all from `settings_base.py`
  - Adds a couple of bits
  - Imports all from `settings_insecure_publicsafe.py`

__*Note 2:*__
- For local testing, to remove the need to always add `--settings=hldjango.settingsdir.standalone_docker` to a command, the default settings file option (`hldjango.settingsdir.jrlocal_win10`) can be changed.
- One option is to edit `manage.py` and change the value. If needed, also change this value in `~/django/casebook/hldjango/.vscode/launch.json`.
- A second option is to use an environment variable.

For clarity, commands written henceforth will continue to append the `standalone_docker` settings string.

## 7.
Setup permissions etc. and a superuser (username/password = admin/admin):
```
cd ~/django/casebook/hldjango/code
poetry run python manage.py initGameGroupAndPermission --settings=hldjango.settingsdir.standalone_docker
poetry run python manage.py initSiteGadminGroupAndPermission --settings=hldjango.settingsdir.standalone_docker
poetry run python manage.py verifyOrAddInsecureTestingSuperuser --settings=hldjango.settingsdir.standalone_docker
```

## 8.
Runserver and test:
```
cd ~/django/casebook/hldjango/code
poetry run python manage.py runserver --settings=hldjango.settingsdir.standalone_docker
```

At this point, the local development server should run and the website will be available at http://127.0.0.1:8000/. PDF generation will not yet work but everything else (logging in/out, creating games, etc.) should.

Test that it all works. Then stop the server and continue with these instructions.

## 9.
If necessary, install [Tex Live](https://www.tug.org/texlive).

Useful links:
- https://tug.org/texlive/doc.html
- https://www.tug.org/texlive/doc/texlive-en/texlive-en.html
- https://www.tug.org/texlive/doc/install-tl.html
- https://www.tug.org/texlive/quickinstall.html

### Download the install files
```
cd /tmp
wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
```

Result:
```
5.5M [application/gzip]
Saving to: ‘install-tl-unx.tar.gz’
```

### Extract
```
zcat < install-tl-unx.tar.gz | tar xf -
```

### Now do __*one*__ of the following:
- Install from a profile
- Install manually


### Install (from a profile):
The `casebook` repository contains a `texlive.profile` file which can be passed to the Tex Live install command (see [Command-line install-tl options](https://www.tug.org/texlive/doc/texlive-en/texlive-en.html#x1-270003.3)).
```
cd install-tl-2*
./install-tl --profile=~/django/casebook/hldjango/install_scripts/texlive.profile
```

### Install (manually):
```
cd install-tl-2*
./install-tl
```

This will start the __*TeX Live installation procedure*__ config.

From here, do the following:
- **S** (scheme): change the installation scheme to `basic scheme (plain and latex)`
- **D** (directories): change the main TeX directory to: `~/texlive/2025`.

__*Note:*__ The location of the main TeX directory is a personal choice. By default, the main directory is set to `/usr/local/texlive/2025`, but, in my case, the installer says that this is "not writable or not allowed". Rather than modifying permissions, the [documentation](https://www.tug.org/texlive/doc/texlive-en/texlive-en.html#x1-250003.2.3) notes:
> A reasonable alternative destination is a directory under your home, especially if you will be the sole user. Use ‘\~’ to indicate this, as in ‘~/texlive/2025’.
- **O** (options): remove `install font/macro doc tree` and `install font/macro source tree`.

__*Note:*__ The config should now show that the install size will be ~116 MB. See [Appendix A](#appendix-a) for the full output.
- **I** (install): install to hard disk

### Post-install
As the [documentation](https://tug.org/texlive/doc/texlive-en/texlive-en.html#x1-290003.4) notes:
> the directory of the binaries for your platform must be added to the search path

Also, at the end of the install output, a message is displayed explaining:
```
Add ~/texlive/2025/texmf-dist/doc/man to MANPATH.
Add ~/texlive/2025/texmf-dist/doc/info to INFOPATH.
Most importantly, add ~/texlive/2025/bin/x86_64-linux
to your PATH for current and future sessions.
```

[opensource.com](https://opensource.com/article/17/6/set-path-linux) suggests, for bash, adding the `PATH` to `~/.bashrc`. So, edit `~/.bashrc` and append:
```
# Tex Live
export PATH=$PATH:~/texlive/2025/bin/x86_64-linux
```

### Test
https://tug.org/texlive/doc/texlive-en/texlive-en.html#x1-370003.5

Reload the terminal and enter:
```
tex --version
```

Result:
```
TeX 3.141592653 (TeX Live 2025)
kpathsea version 6.4.1
Copyright 2025 D.E. Knuth.
...
```

Now try generating a PDF:
```
pdflatex sample2e.tex
```
This should create a PDF at `~/sample2e.pdf`.

## 10.
Now that Tex Live is installed and working, use [tlmgr](https://tug.org/texlive/doc/tlmgr.html) (which is installed as part of Tex Live) to install any collections and/or individual packages.

### i.
Check for, and if necessary apply, updates to tlmgr itself:
```
tlmgr update --self
```

Result:
```
tlmgr: package repository https://gb.mirrors.cicku.me/ctan/systems/texlive/tlnet (verified)
tlmgr: saving backups to ~/texlive/2025/tlpkg/backups
tlmgr: no self-updates for tlmgr available
```

### ii.
Install a collection of recommended fonts:
```
tlmgr install collection-fontsrecommended
```

Result:
```
tlmgr: package repository https://gb.mirrors.cicku.me/ctan/systems/texlive/tlnet (verified)
[1/30, ??:??/??:??] install: avantgar [236k]
[2/30, 00:01/05:26] install: bookman [273k]
...
```

### iii.
Install individual packages (using the 'Edited' packages list as shown in [Tex Live packages](https://docs.google.com/spreadsheets/d/1gp4lruCdjECokg_wQOyf2mja3K_6LxTt0bW2ts2IQxk/edit?gid=0#gid=0)):
```
tlmgr install adjustbox amsfonts amsmath aurical babel baskervillef caption censor clock csquotes ellipse enumitem eso-pic etoolbox fancybox fira float fontawesome5 fontaxes latex fontspec graphics hyperref ifsym koma-script lastpage lettrine librebaskerville lipsum listings listingsutf8 lm longfbox marginnote mdwtools mnsymbol tools needspace ninecolors options parskip pbox pdfcol pdflscape pdfpages pgf pgfopts pgfornament picinpar pict2e printlen refcount setspace soul tabularray tcolorbox pgf tikzfill tocloft tokcycle ulem wrapfig xcolor xetex xkeyval yfonts
```

__*Note:*__
- To test what the install command will do, but without actually running it, append the `--dry-run` flag.
- The packages listed in the command above are partially different from those defined in the casebook repository's `texlive_install.sh` file. The differences and the reasons for any changes are documented in [Tex Live packages](https://docs.google.com/spreadsheets/d/1gp4lruCdjECokg_wQOyf2mja3K_6LxTt0bW2ts2IQxk/edit?gid=0#gid=0).
- When running the install command, some packages are reported as "already present". This does not seem to be an issue, so I've left them for now whilst testing is ongoing.

### iv.
Deactivate automatic generation of backups:
```
tlmgr option -- autobackup 0
```

Result:
```
tlmgr: setting option autobackup to 0.
tlmgr: updating ~/texlive/2025/tlpkg/texlive.tlpdb
```

### v.
Update all installed packages except for tlmgr itself:
```
tlmgr update --all --no-auto-install
```

Result:
```
tlmgr: package repository https://gb.mirrors.cicku.me/ctan/systems/texlive/tlnet (verified)
tlmgr: no updates available
```

## 11.
If necessary, install [Graphviz](https://graphviz.org/) and [Poppler](https://poppler.freedesktop.org/) ([poppler-utils](https://packages.debian.org/sid/poppler-utils)):
```
sudo apt install graphviz poppler-utils
```

These are required when generating debug and draft files.


## 12.
Everything should now be ready to generate PDFs via the website.

### i.
Runserver:
```
cd ~/django/casebook/hldjango/code
poetry run python manage.py runserver --settings=hldjango.settingsdir.standalone_docker
```

### ii.
Run [Huey](https://huey.readthedocs.io/en/latest/index.html) (which is a task queue that the website uses to handle PDF processing requests):
```
cd ~/django/casebook/hldjango/code/
poetry run python manage.py run_huey --settings=hldjango.settingsdir.standalone_docker
```

### iii.
- Log in to the local website
- Go to the 'New Game' page (`/games/game/new/`)
- create a new game (perhaps using the [Casebook: Blank Starting Case](https://docs.google.com/document/d/1am1HNjGZhSgjJKIvRkTmadlxXIiuXZxycIfxuhEV-lo/edit?tab=t.0), as mentioned in [The Casebook Handbook and Cookbook](https://docs.google.com/document/d/16OFk0jbn0IvgO8ZnRPFXaMtxzwND9cln-9LjG83Xpjg/edit?tab=t.0#heading=h.p4vgna48owwn))

__*Note:*__ creating a new game creates the individual game page but does not yet generate any PDFs.
- Go to the game's individual page, for example `/games/game/test-game-name/`
- Click the `Generated files` button, which takes you to, for example, the 'Generated game files for "Test Game Name"' page
- Click one of the generation buttons

The generated PDFs etc. are stored in: `~/django/casebook/hldjango/media/games/<gameid-[a-z][0-9]>`


## Appendix A
### TeX Live installation configuration (after custom changes)
```
==> TeX Live installation procedure <==
==> Letters/digits in <angle brackets> indicate <==
==> menu items for actions or customizations <==
== help> https://tug.org/texlive/doc/install-tl.html <==

Detected platform: GNU/Linux on x86_64

<B> set binary platforms: 1 out of 15

<S> set installation scheme: scheme-basic

<C> set installation collections:
    2 collections out of 41, disk space required: 116 MB

<D> set directories:
    TEXDIR (the main TeX directory):
    /home/laurence/texlive/2025
    TEXMFLOCAL (directory for site-wide local files):
    /home/laurence/texlive/texmf-local
    TEXMFSYSVAR (directory for variable and automatically generated data):
    /home/laurence/texlive/2025/texmf-var
    TEXMFSYSCONFIG (directory for local config):
    /home/laurence/texlive/2025/texmf-config
    TEXMFVAR (personal directory for variable and automatically generated data):
    ~/.texlive2025/texmf-var
    TEXMFCONFIG (personal directory for local config):
    ~/.texlive2025/texmf-config
    TEXMFHOME (directory for user-specific files):
    ~/texmf

<O> options:
    [ ] use letter size instead of A4 by default
    [X] allow execution of restricted list of programs via \write18
    [X] create all format files
    [ ] install macro/font doc tree
    [ ] install macro/font source tree
    [ ] create symlinks to standard directories
```
