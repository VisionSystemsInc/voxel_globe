%include %{_sourcedir}/common.inc

Name:           tornado
Version:        4.2
Summary:        Tornado is a Python web framework and asynchronous networking library, originally developed at FriendFeed.
Release:        1%{?dist}
Source0:        %{name}-%{version}.tar.gz
Source1:        common.inc

License:	http://www.apache.org/licenses/LICENSE-2.0
Group:		Development/Languages
URL: 		http://www.tornadoweb.org/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires: certifi, python
%description
Tornado Web Server
==================

`Tornado <http://www.tornadoweb.org>`_ is a Python web framework and
asynchronous networking library, originally developed at `FriendFeed
<http://friendfeed.com>`_.  By using non-blocking network I/O, Tornado
can scale to tens of thousands of open connections, making it ideal for
`long polling <http://en.wikipedia.org/wiki/Push_technology#Long_polling>`_,
`WebSockets <http://en.wikipedia.org/wiki/WebSocket>`_, and other
applications that require a long-lived connection to each user.


Upgrade notes
-------------

As of Tornado 3.2, the `backports.ssl_match_hostname
<https://pypi.python.org/pypi/backports.ssl_match_hostname>`_ package
must be installed when running Tornado on Python 2.  This will be
installed automatically when using ``pip`` or ``easy_install``.

Quick links
-----------

* `Documentation <http://www.tornadoweb.org/en/stable/>`_
* `Source (github) <https://github.com/facebook/tornado>`_
* `Mailing list <http://groups.google.com/group/python-tornado>`_
* `Stack Overflow <http://stackoverflow.com/questions/tagged/tornado>`_
* `Wiki <https://github.com/facebook/tornado/wiki/Links>`_

Hello, world
------------

Here is a simple "Hello, world" example web app for Tornado::

    import tornado.ioloop
    import tornado.web

    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("Hello, world")

    application = tornado.web.Application([
        (r"/", MainHandler),
    ])

    if __name__ == "__main__":
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()

This example does not use any of Tornado's asynchronous features; for
that see this `simple chat room
<https://github.com/facebook/tornado/tree/master/demos/chat>`_.

Installation
------------

**Automatic installation**::

    pip install tornado

Tornado is listed in `PyPI <http://pypi.python.org/pypi/tornado/>`_ and
can be installed with ``pip`` or ``easy_install``.  Note that the
source distribution includes demo applications that are not present
when Tornado is installed in this way, so you may wish to download a
copy of the source tarball as well.

**Manual installation**: Download the latest source from `PyPI
<http://pypi.python.org/pypi/tornado/>`_.

.. parsed-literal::

    tar xvzf tornado-$VERSION.tar.gz
    cd tornado-$VERSION
    python setup.py build
    sudo python setup.py install

The Tornado source code is `hosted on GitHub
<https://github.com/facebook/tornado>`_.

**Prerequisites**: Tornado runs on Python 2.6, 2.7, 3.2, and 3.3.  On
Python 2, the `backports.ssl_match_hostname
<https://pypi.python.org/pypi/backports.ssl_match_hostname>`_ package
must be installed (This will be installed automatically when using
``pip`` or ``easy_install``); on Python 3 there are no strict
dependencies outside the standard library.  Some Tornado features may
require one of the following optional libraries:

* `unittest2 <https://pypi.python.org/pypi/unittest2>`_ is needed to run
  Tornado's test suite on Python 2.6 (it is unnecessary on more recent
  versions of Python)
* `concurrent.futures <https://pypi.python.org/pypi/futures>`_ is the
  recommended thread pool for use with Tornado and enables the use of
  ``tornado.netutil.ThreadedResolver``.  It is needed only on Python 2;
  Python 3 includes this package in the standard library.
* `pycurl <http://pycurl.sourceforge.net>`_ is used by the optional
  ``tornado.curl_httpclient``.  Libcurl version 7.18.2 or higher is required;
  version 7.21.1 or higher is recommended.
* `Twisted <http://www.twistedmatrix.com>`_ may be used with the classes in
  `tornado.platform.twisted`.
* `pycares <https://pypi.python.org/pypi/pycares>`_ is an alternative
  non-blocking DNS resolver that can be used when threads are not
  appropriate.
* `Monotime <https://pypi.python.org/pypi/Monotime>`_ adds support for
  a monotonic clock, which improves reliability in environments
  where clock adjustments are frequent.  No longer needed in Python 3.3.

**Platforms**: Tornado should run on any Unix-like platform, although
for the best performance and scalability only Linux (with ``epoll``)
and BSD (with ``kqueue``) are recommended for production deployment
(even though Mac OS X is derived from BSD and supports kqueue, its
networking performance is generally poor so it is recommended only for
development use).  Tornado will also run on Windows, although this
configuration is not officially supported and is recommended only for
development use.

Discussion and support
----------------------

You can discuss Tornado on `the Tornado developer mailing list
<http://groups.google.com/group/python-tornado>`_, and report bugs on
the `GitHub issue tracker
<https://github.com/facebook/tornado/issues>`_.  Links to additional
resources can be found on the `Tornado wiki
<https://github.com/facebook/tornado/wiki/Links>`_.

Tornado is one of `Facebook's open source technologies
<http://developers.facebook.com/opensource/>`_. It is available under
the `Apache License, Version 2.0
<http://www.apache.org/licenses/LICENSE-2.0.html>`_.

This web site and all documentation is licensed under `Creative
Commons 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.

%prep
%setup -q

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null


%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%exclude /usr/lib/debug
/

%post

%postun

#%changelog

