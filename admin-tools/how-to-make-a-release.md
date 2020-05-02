<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Get latest sources:](#get-latest-sources)
- [Change version in xdis/version.py.](#change-version-in-xdisversionpy)
- [Update ChangeLog:](#update-changelog)
- [Update NEWS.md from ChangeLog. Then:](#update-newsmd-from-changelog-then)
- [Make sure pyenv is running and check newer versions](#make-sure-pyenv-is-running-and-check-newer-versions)
- [Update NEWS.md from master branch](#update-newsmd-from-master-branch)
- [Make packages and tag](#make-packages-and-tag)
- [Upload](#upload)
- [Upload rest of versions](#upload-rest-of-versions)
- [Push tags:](#push-tags)
- [Check on a VM](#check-on-a-vm)

<!-- markdown-toc end -->

# Get latest sources:

    $ git pull

# Change version in xdis/version.py.

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

# Update NEWS.md from master branch

    $ git commit -m"Get ready for release $VERSION" .

# Make packages and tag

    $ ./admin-tools/make-dist.sh
	$ twine check dist/x-python-$VERSION*

Goto https://github.com/rocky/x-python/releases/new


# Check and Upload

	$ twine check dist/x?python-${VERSION}*
	$ twine upload dist/x?python-${VERSION}*

Check on https://pypi.org/project/x-python/

# Upload rest of versions

    $ twine upload dist/xdis-${VERSION}*

# Push tags:

    $ git push --tags

# Check on a VM

    $ cd /virtual/vagrant/virtual/vagrant/ubuntu-zesty
	$ vagrant up
	$ vagrant ssh
	$ pyenv local 3.5.2
	$ pip install --upgrade xdis
	$ exit
	$ vagrant halt
