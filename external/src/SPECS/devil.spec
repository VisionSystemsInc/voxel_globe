%include %{_sourcedir}/common.inc

Name:           DevIL
Version:        1.7.8
Release:        20%{?dist}
Summary:        A cross-platform image library
Group:          System Environment/Libraries
License:        LGPLv2
URL:            http://openil.sourceforge.net/
Source0:        http://downloads.sourceforge.net/openil/%{name}-%{version}.tar.gz
Patch0:         DevIL-1.7.5-allegropicfix.patch
Patch1:         DevIL-1.7.5-il_endian_h.patch
Patch2:         DevIL-1.7.8-CVE-2009-3994.patch
Patch3:         DevIL-1.7.8-libpng15.patch
BuildRequires:  libGLU-devel
BuildRequires:  libXext-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel

%description
Developer's Image Library (DevIL) is a programmer's library to develop
applications with very powerful image loading capabilities, yet is easy for a
developer to learn and use. Ultimate control of images is left to the
developer, so unnecessary conversions, etc. are not performed. DevIL utilizes
a simple, yet powerful, syntax. DevIL can load, save, convert, manipulate,
filter and display a wide variety of image formats.


%package devel
Summary:        Development files for DevIL
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires(post): info
Requires(preun): info

%description devel
Development files for DevIL


%package ILUT
Summary:        The libILUT component of DevIL
Group:          System Environment/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description ILUT
The libILUT component of DevIL


%package ILUT-devel
Summary:        Development files for the libILUT component of DevIL
Group:          Development/Libraries
Requires:       %{name}-ILUT%{?_isa} = %{version}-%{release}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       allegro-devel libGLU-devel

%description ILUT-devel
Development files for the libILUT component of DevIL

%prep
%setup -q -n devil-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
sed -i 's|png12|png16|g' configure

%build
%configure --enable-ILU --enable-ILUT --disable-allegrotest
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|LD_RUN_PATH|DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

make install DESTDIR=%{buildroot}
mkdir %{buildroot}%{_libdir}/la
mv %{buildroot}%{_libdir}/*.la %{buildroot}%{_libdir}/la
rm %{buildroot}%{_infodir}/dir

%files
%{_bindir}/ilur
%{_libdir}/libIL.so.*
%{_libdir}/libILU.so.*
%doc AUTHORS ChangeLog COPYING CREDITS README TODO

%files devel
%{_libdir}/la/*
%{_libdir}/libIL.so
%{_libdir}/libILU.so
%{_libdir}/pkgconfig/IL.pc
%{_libdir}/pkgconfig/ILU.pc
%dir %{_includedir}/IL
%{_includedir}/IL/il.h
%{_includedir}/IL/ilu.h
%{_includedir}/IL/ilu_region.h
%{_infodir}/DevIL_manual.info
%{_libdir}/libIL.a
%{_libdir}/libILU.a

%files ILUT
%{_libdir}/libILUT.so.*

%files ILUT-devel
%{_libdir}/libILUT.so
%{_libdir}/libILUT.a
%{_libdir}/pkgconfig/ILUT.pc
%{_includedir}/IL/devil_cpp_wrapper.hpp
%{_includedir}/IL/ilut.h

%changelog
* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jun  3 2014 Hans de Goede <hdegoede@redhat.com> - 1.7.8-18
- Stop using lcms as it is being orphaned

* Mon Aug 26 2013 Jon Ciesla <limburgher@gmail.com> - 1.7.8-17
- libmng rebuild.

* Fri Aug 02 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 28 2013 Kalev Lember <kalevlember@gmail.com> - 1.7.8-15
- Rebuilt with libpng16

* Mon Apr 15 2013 Hans de Goede <hdegoede@redhat.com> - 1.7.8-14
- devil_cpp_wrapper.hpp depends on ILUT, move it to -ILUT-devel (rhbz#951901)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan 18 2013 Adam Tkac <atkac redhat com> - 1.7.8-12
- rebuild due to "jpeg8-ABI" feature drop

* Fri Dec 21 2012 Adam Tkac <atkac redhat com> - 1.7.8-11
- rebuild against new libjpeg

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May 16 2012 Hans de Goede <hdegoede@redhat.com> - 1.7.8-9
- Don't use SSE3 (x86_64) or any SSE (ix86), so that the lib will run
  on processors lacking SSE(3) (rhbz#815629)

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Nov 20 2011 Hans de Goede <hdegoede@redhat.com> - 1.7.8-7
- Rebuild for new libpng (rhbz#751583)

* Fri Jul 15 2011 Hans de Goede <hdegoede@redhat.com> - 1.7.8-6
- Rebuild for new allegro-4.4

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Dec  4 2009 Hans de Goede <hdegoede@redhat.com> 1.7.8-4
- Fix DICOM Processing Buffer Overflow Vulnerability CVE-2009-3994 (#542700)

* Fri Aug 21 2009 Hans de Goede <hdegoede@redhat.com> 1.7.8-3
- Switch Source0 to respun upstream tarbal (added a missing header)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Mar  9 2009 Hans de Goede <hdegoede@redhat.com> 1.7.8-1
- Update to latest upstream: 1.7.8

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 10 2009 Hans de Goede <hdegoede@redhat.com> 1.7.7-1
- Update to latest upstream: 1.7.7

* Mon Jan 19 2009 Hans de Goede <hdegoede@redhat.com> 1.7.5-2
- Fix missing symbols (rh 480269)
- Fix off by one error in CVE-2008-5262 check (rh 479864)

* Tue Jan 13 2009 Hans de Goede <hdegoede@redhat.com> 1.7.5-1
- Update to latest upstream: 1.7.5
- Add patch to fix CVE-2008-5262

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.6.8-0.15.rc2
- Autorebuild for GCC 4.3

* Sun Jan 13 2008 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.14.rc2
- Patch to fix headers for gcc 4.3, see BZ #428527. (Thanks to Hans de Goede)

* Wed Aug 22 2007 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.13.rc2
- Release bump for F8 mass rebuild
- Added patch to fix BZ #253639

* Tue Aug 07 2007 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.12.rc2
- Split libILUT into separate package. See BZ #250734
- Removed some old provides:
- Convert the CREDITS to UTF8
- Updated license field due to new guidelines

* Tue Jan 02 2007 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.11.rc2
- Added patch to fix endian issues with some SGI files. Courtesy of Scott A.
  Friedman (BZ #220417)

* Thu Sep 07 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.10.rc2
- Upgrade to 1.6.8-rc2
- Added libICE-devel buildrequire
- Dropped DevIL-1.6.8-rc1-64bit.patch, fixed upstream
- Updated allegropicfix.patch for new version
- Updated and split header fixes into separate files for easier maintenance

* Mon Aug 28 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.9.rc1
- Release bump for FC6 mass rebuild

* Fri Jun 09 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.8.rc1
- Added patch courtesy of Hans de Goede to fix crashes on 64bit systems

* Wed May 31 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.7.rc1
- Added libGLU-devel to buildrequires
- Dropped libGL-devel from requires for devel package

* Sun May 28 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.6.rc1.iss
- Dropped xorg-x11-devel as a buildrequire
- Dropped zlib-devel as a buildrequire
- Dropped xorg-x11-devel as a require for the devel package
- Added libGL-devel and libGLU-devel as requires for devel package
- Dropped superfluous documentation from devel package
- Added provides to offer lower case alias in preparation for probable
  policy change
- Replace autoconf generated config.h in devel package to avoid potential
  define collisions
- Replace source URL with primary sf site, rather than a mirror
- Fix ilu_region.h to use IL\il.h and not ilu_internal.h and roll into
  a single patch incorporating previous header fixes.

* Sat May 27 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.5.rc1.iss
- Added patch to stop linking against alleg_unsharable, otherwise non PIC code
  is included in the library
- Use %%{?dist} for most recent changelog entry - avoids incoherent changelog
  versions if %%{?dist} macro is missing or different.

* Fri May 26 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.4.rc1.iss
- Made zlib-devel and xorg-x11-devel explicit buildrequires
- Corrected release name format to 0.%%{X}.%%{alphatag} from 0.%%{alphatag}.%%{X}
- Added -q to %%setup
- Added %%{version}-%%{release} to provides field

* Sun May 21 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.RC1.3.iss
- Use Fedora's libtool, seems to fix rpaths problem on x86_64.

* Sun May 14 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.RC1.2.iss
- Now compiled against allegro

* Sat May 13 2006 Ian Chapman <packages[AT]amiga-hardware.com> 1.6.8-0.RC1.1.iss
- Initial Release