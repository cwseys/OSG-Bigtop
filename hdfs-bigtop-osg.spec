Summary: Adapt OSG and Bigtop HDFS dependencies
Name: hdfs-bigtop-osg
Version: 3
Release: 0
License: Public
Group: Applications/System
Provides: libhdfs.so.0()(64bit)
# don't want to Obsoletes b/c this causes yum to attempt installation when package is merely in
# yum catalog
# Obsoletes: hadoop-libhdfs <= 2.7
%description
Install files and provides to adapt Bigtop and OSG packages.
Build with 'rpmbuild -bb name.specfile', then upload RPM to the extras repo

%install
#rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib64
ln -sf /usr/lib64/libhdfs.so.0.0.0 %{buildroot}/usr/lib64/libhdfs.so.0

%files
/usr/lib64/libhdfs.so.0

