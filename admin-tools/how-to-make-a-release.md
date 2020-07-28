<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Get latest sources:](#get-latest-sources)
- [Change version in xpython/version.py.](#change-version-in-xpythonversionpy)
- [Update ChangeLog:](#update-changelog)
- [Update NEWS.md from ChangeLog. Then:](#update-newsmd-from-changelog-then)
- [Update NEWS.md from master branch](#update-newsmd-from-master-branch)
- [Make packages and check](#make-packages-and-check)
- [Release on Github](#release-on-github)
- [Get on PyPI](#get-on-pypi)
- [Move dist files to uploaded](#move-dist-files-to-uploaded)

<!-- markdown-toc end -->

# Get latest sources:

    $ git pull

# Change version in xpython/version.py.

    $ emacs xpython/version.py
    $ source xpython/version.py
    $ echo $VERSION
    $ git commit -m"Get ready for release $VERSION" .


# Update ChangeLog:

    $ make ChangeLog

#  Update NEWS.md from ChangeLog. Then:

    $ emacs NEWS.md
    $ remake -c check
    $ git commit --amend .
    $ git push   # get CI testing going early
    $ remake -c check-full

# Make packages and check

    $ remake -c dist
	$ twine check dist/x[-_]python-$VERSION*

# Check package on github

Todo: turn this into a script in `admin-tools`

	$ [[ ! -d /tmp/gittest ]] && mkdir /tmp/gittest; pushd /tmp/gittest
	$ pyenv local 3.7.5
	$ pip install -e git://github.com/rocky/x-python.git#egg=x-python
	$ xpython -V # see that new version appears
	$ pip uninstall x-pythons
	$ popd

# Release on Github

Goto https://github.com/rocky/x-python/releases/new

Now check the *tagged* release. (Checking the untagged release was previously done).

Todo: turn this into a script in `admin-tools`

	$ git pull # to pull down new tag
    $ pushd /tmp/gittest
	$ pyenv local 3.7.5
	$ pip install -e git://github.com/rocky/x-python.git@${VERSION}#egg=x-python
	$ xpython -V # see that new version appears
	$ pip uninstall x-python
	$ popd

# Get on PyPI

	$ twine upload dist/x[-_]python-${VERSION}*

Check on https://pypi.org/project/x-python/

# Move dist files to uploaded

	$ mv -v dist/x[_-]python-${VERSION}* dist/uploaded
