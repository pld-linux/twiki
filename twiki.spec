Summary:	TWiki Collaborative Web Space (WikiClone)
Name:		twiki
Version:	20040902
Release:	0.1
License:	GPL
Group:		Applications/WWW
Source0:	http://www.twiki.org/swd/TWiki%{version}.tar.gz
# Source0-md5:	d04b2041d83dc6c97905faa1c6b9116d
URL:		http://www.twiki.org/
Requires:	apache >= 1.3.33-2
Requires:	perl-base >= 1:5.6
Requires:	perl-CGI
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir %{_datadir}/%{name}

%description
Welcome to TWiki, a flexible, powerful, and easy to use enterprise
collaboration platform. It is a structured Wiki, typically used to run
a project development space, a document management system, a knowledge
base, or any other groupware tool, on an intranet or on the internet.
Web content can be created collaboratively by using just a browser.
Developers can create new web applications based on a Plugin API.

%prep
%setup -q -c
mv twiki/* .

%install
rm -rf $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc *.txt
