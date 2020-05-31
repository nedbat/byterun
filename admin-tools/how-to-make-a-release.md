<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Get latest sources:](#get-latest-sources)
- [Change version in xpython/version.py.](#change-version-in-xpythonversionpy)
- [Update ChangeLog:](#update-changelog)
- [Update NEWS.md from ChangeLog. Then:](#update-newsmd-from-changelog-then)
- [Update NEWS.md from master branch](#update-newsmd-from-master-branch)
- [Make packages and check](#make-packages-and-check)
- [Get on PyPy](#get-on-pypy)

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

# Update NEWS.md from master branch

    $ git commit -m"Get ready for release $VERSION" .

# Make packages and check

    $ ./admin-tools/make-dist.sh
	$ twine check dist/x[-_]python-$VERSION*

# Get on PyPy

Goto https://github.com/rocky/x-python/releases/new


	$ twine upload dist/x[-_]python-${VERSION}-py3.7.egg  # Older versions don't support Markdown
	$ twine upload dist/x[-_]python-${VERSION}*

Check on https://pypi.org/project/x-python/

# Move dist files to uploaded

	$ mv -v dist/x[_-]python-${VERSION}* dist/uploaded
