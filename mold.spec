Name:		mold
Version:	1.1
Release:	1%{?dist}
Summary:	A Modern Linker

License:	AGPLv3+
URL:		https://github.com/rui314/mold
Source0:	%{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# The bundled build system for tbb tries to strip all Werror from the
# CFLAGS/CXXFLAGS when not building in strict mode (mold doesn't use strict
# mode). We don't want that because it causes the "Werror=format-security"
# option to become "=format-security" and break the build. (similar to a patch
# in the Fedora tbb package)
Patch0:		tbb-strip-werror.patch

# Skip failing test on aarch64
Patch1:		0001-Skip-reloc-rodata-test-on-aarch64.patch

# Fix mimalloc compatibility with libstdc++ < 9:
# https://gcc.gnu.org/bugzilla/show_bug.cgi?id=68210
Patch2: 0002-Fix-compatibility-with-libstdc-9.patch

# mold can currently produce native binaries for these architectures only
ExclusiveArch:	%{ix86} x86_64 aarch64 riscv64

BuildRequires:	cmake
%if 0%{?el7}
BuildRequires:	devtoolset-10-toolchain
%endif
%if 0%{?el8}
BuildRequires:	gcc-toolset-10-toolchain
%endif
%if 0%{!?el7} && 0%{!?el8}
BuildRequires:	gcc
BuildRequires:	gcc-c++ >= 10
%endif
BuildRequires:	mimalloc-devel
BuildRequires:	openssl-devel
BuildRequires:	xxhash-devel
BuildRequires:	zlib-devel

# The following packages are only required for executing the tests
BuildRequires:	clang
BuildRequires:	glibc-static
%ifarch x86_64
BuildRequires:	/usr/lib/libc.a
%endif
%if 0%{?fedora}
BuildRequires:	libdwarf-tools
%endif
BuildRequires:	libstdc++-static

Requires(post): %{_sbindir}/alternatives
Requires(preun): %{_sbindir}/alternatives

# API-incompatible with older tbb 2020.3 currently shipped by Fedora:
# https://bugzilla.redhat.com/show_bug.cgi?id=2036372
Provides:	bundled(tbb) = 2021.3

%define build_args PREFIX=%{_prefix} LIBDIR=%{_libdir} CC=gcc CXX=g++ CFLAGS="%{build_cflags}" CXXFLAGS="%{build_cxxflags}" LDFLAGS="%{build_ldflags}" STRIP=echo SYSTEM_MIMALLOC=1

%description
mold is a faster drop-in replacement for existing Unix linkers.
It is several times faster than the LLVM lld linker.
mold is designed to increase developer productivity by reducing
build time, especially in rapid debug-edit-rebuild cycles.

%prep
%autosetup -p1
rm -r third-party/{mimalloc,xxhash}

%build
%if 0%{?el7}
. /opt/rh/devtoolset-10/enable
%endif
%if 0%{?el8}
. /opt/rh/gcc-toolset-10/enable
%endif
%make_build %{build_args}

%install
%make_install %{build_args}
# Overwrite absolute symlink with relative symlink
ln -srf %{buildroot}%{_bindir}/mold %{buildroot}%{_libexecdir}/mold/ld
chmod +x %{buildroot}%{_libdir}/mold/mold-wrapper.so

%post
if [ "$1" = 1 ]; then
  %{_sbindir}/alternatives --install %{_bindir}/ld ld %{_bindir}/ld.mold 1
fi

%postun
if [ "$1" = 0 ]; then
  %{_sbindir}/alternatives --remove ld %{_bindir}/ld.mold
fi

%check
%if 0%{?el7}
. /opt/rh/devtoolset-10/enable
%endif
%if 0%{?el8}
. /opt/rh/gcc-toolset-10/enable
%endif
%make_build -j1 %{build_args} test

%files
%license LICENSE
%ghost %{_bindir}/ld
%{_bindir}/mold
%{_bindir}/ld.mold
%{_bindir}/ld64.mold
%{_libdir}/mold
%{_libdir}/mold/mold-wrapper.so
%{_libexecdir}/mold
%{_libexecdir}/mold/ld
%{_mandir}/man1/mold.1*

%changelog
* Mon Feb 21 2022 Christoph Erhardt <fedora@sicherha.de> - 1.1-1
- Bump version to 1.1
- Drop upstreamed patches
- Update description

* Thu Feb 17 2022 Christoph Erhardt <fedora@sicherha.de> - 1.0.2-2
- Rebuild due to mimalloc soname change

* Sun Jan 23 2022 Christoph Erhardt <fedora@sicherha.de> - 1.0.2-1
- Bump version to 1.0.2.

* Sat Jan 01 2022 Christoph Erhardt <fedora@sicherha.de> - 1.0.1-1
- Initial package for version 1.0.1.
