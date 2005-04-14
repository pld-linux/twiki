# TODO
# - secure access by default
# - installation guide mentioned cron. where's the cron scripts?
#
# Conditional build:
%bcond_without	intl	# experimental i18n support; see http://twiki.org/cgi-bin/view/TWiki.TWikiInstallationGuide
#
Summary:	TWiki Collaborative Web Space (WikiClone)
Name:		twiki
Version:	20040902
Release:	0.43
License:	GPL
Group:		Applications/WWW
Source0:	http://www.twiki.org/swd/TWiki%{version}.tar.gz
# Source0-md5:	d04b2041d83dc6c97905faa1c6b9116d
URL:		http://www.twiki.org/
BuildRequires:	sed >= 4.0
Requires:	apache >= 1.3.33-2
Requires:	perl-base >= 1:5.6.2
Requires:	perl-Unicode-MapUTF8
Requires:	rcs >= 5.7
Requires:	diffutils >= 2.7
Requires:	grep
Requires:	crondaemon
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir /etc/%{name}
%define		_appdir %{_datadir}/%{name}
%define		_appdatadir /var/lib/%{name}
%define		_applogdir /var/log/%{name}

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
mv bin/testenv .
mv lib/TWiki.cfg .
rm -f data/mime.types

# adjust RCS content for Apache run-time environment
sed -i -e '1,10s/nobody:/http:/' data/*/*,v
sed -i -e 's/nobody/http/g' testenv

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_appdir}/bin,%{_sysconfdir},%{_appdatadir},%{_applogdir}}

cp -a bin/* $RPM_BUILD_ROOT%{_appdir}/bin
cp -a lib templates $RPM_BUILD_ROOT%{_appdir}
cp -a data pub $RPM_BUILD_ROOT%{_appdatadir}

sed -i -e 's,^\$twikiLibPath.*,$twikiLibPath = q(%{_appdir}/lib);,' \
	$RPM_BUILD_ROOT%{_appdir}/bin/setlib.cfg

sed -i -e '
    s,do "TWiki.cfg",do "%{_sysconfdir}/TWiki.pl",
' $RPM_BUILD_ROOT%{_appdir}/lib/TWiki.pm

%{?debug:sed -e 's,require "TWiki.cfg",require "%{_sysconfdir}/TWiki.pl",' testenv > $RPM_BUILD_ROOT%{_appdir}/bin/testenv}

sed -e '
	s,!FILE_path_to_TWiki!/data,%{_appdatadir}/data,
	s,!URL_path_to_TWiki!,/%{name},g
' bin/.htaccess.txt > htaccess.txt

sed -e '
	s,http://your.domain.com,http://localhost,g
	s,/home/httpd/twiki/pub,%{_appdatadir}/pub,
	s,/home/httpd/twiki/templates,%{_appdir}/templates,
	s,/home/httpd/twiki/data,%{_appdatadir}/data,
	s,$dataDir/mime.types,/etc/mime.types,
	s,^\(\$logDir *= *\)".*,\1"%{_applogdir}";,
	%{?with_intl:s,^\$useLocale = 0;,$useLocale = 1;,}
' TWiki.cfg > $RPM_BUILD_ROOT%{_sysconfdir}/TWiki.pl

cat <<EOF > $RPM_BUILD_ROOT%{_sysconfdir}/apache-%{name}.conf
ScriptAlias /%{name}/bin %{_appdir}/bin
<Directory %{_appdir}/bin>
	Options ExecCGI

	$(cat htaccess.txt)
</Directory>

Alias /%{name}/pub %{_appdatadir}/pub
<Directory %{_appdatadir}/pub>
	Allow from all
</Directory>
# vim: filetype=apache ts=4 sw=4 et
EOF

echo '%%defattr(660,root,http,770)' > files.data
find $RPM_BUILD_ROOT%{_appdatadir} -type d | \
	sed -e "s,^$RPM_BUILD_ROOT,%%dir ," >> files.data
find $RPM_BUILD_ROOT%{_appdatadir} -type f | \
	sed -e "s#^$RPM_BUILD_ROOT#%%config(noreplace,missingok) %%verify(not md5 mtime size) #" >> files.data

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 >= 1.3.33-2
%{?debug:set -x; echo "triggerin apache1 %{name}-%{version}-%{release} 1:[$1]; 2:[$2]"}
if [ "$1" = "1" ] && [ "$2" = "1" ] && [ -d /etc/apache/conf.d ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf /etc/apache/conf.d/99_%{name}.conf
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
else
	# restart apache if the config symlink is there
	if [ -L /etc/apache/conf.d/99_%{name}.conf ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%triggerun -- apache1 >= 1.3.33-2
%{?debug:set -x; echo "triggerun apache1 %{name}-%{version}-%{release}: 1:[$1]; 2:[$2]"}
# remove link if eighter of the packages are gone
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	if [ -L /etc/apache/conf.d/99_%{name}.conf ]; then
		rm -f /etc/apache/conf.d/99_%{name}.conf
		if [ -f /var/lock/subsys/apache ]; then
			/etc/rc.d/init.d/apache restart 1>&2
		fi
	fi
fi

%triggerin -- apache >= 2.0.0
%{?debug:set -x; echo "triggerin apache2 %{name}-%{version}-%{release}: 1:[$1]; 2:[$2]"}
if [ "$1" = "1" ] && [ "$2" = "1" ] && [ -d /etc/httpd/httpd.conf ]; then
	ln -sf %{_sysconfdir}/apache-%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
else
	# restart apache if the config symlink is there
	if [ -L /etc/httpd/httpd.conf/99_%{name}.conf ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%triggerun -- apache >= 2.0.0
%{?debug:set -x; echo "triggerun apache2 %{name}-%{version}-%{release}: 1:[$1]; 2:[$2]"}
# remove link if eighter of the packages are gone
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	if [ -L /etc/httpd/httpd.conf/99_%{name}.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
		if [ -f /var/lock/subsys/httpd ]; then
			/etc/rc.d/init.d/httpd restart 1>&2
		fi
	fi
fi

%files -f files.data
%defattr(644,root,root,755)
%doc *.txt
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache-%{name}.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.pl

%dir %{_appdir}
%dir %{_appdir}/bin
%attr(755,root,root) %{_appdir}/bin/*

%{_appdir}/lib
%{_appdir}/templates

%attr(770,root,http) %{_applogdir}
