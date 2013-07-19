Name: khtnotes
Version: 2.21.0
Release: 1
Summary: A note taking application with ownCloud sync
Group: office
License: gpl
URL: http://khertan.net/KhtNotes
Source0: %{name}-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildArch: noarch
BuildRequires: python-devel
Requires: python, python-pyside

%description
A note taking application for Harmattan devices (n950, n9), and Nemo Mobile / MeeGo devices. KhtNotes provide sync of notes with ownCloud, and permit to preview markdown syntax

%prep
%setup -q -n %{name}-%{version}
find -name '__init__.py' | xargs chmod +x

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/khtnotes/*
/usr/share/dbus-1/services/*
/usr/share/applications/*
/usr/share/icons/hicolor/80x80/apps/*
/usr/share/icons/hicolor/64x64/apps/*
/usr/share/icons/hicolor/scalable/apps/*
%{python_sitelib}/*egg-info
