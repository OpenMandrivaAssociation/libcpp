%define debug_package %{nil}

%define major 1
%define beta %{nil}
%define scmrev %{nil}
%define libname %mklibname c++ %{major}
%define devname %mklibname c++ -d

Name: libc++
Version: 3.4
%if "%{beta}" == ""
%if "%{scmrev}" == ""
Release: 2
Source: http://llvm.org/releases/%{version}/libcxx-%{version}.src.tar.gz
%else
Release: 0.%{scmrev}.1
Source: %{name}-%{scmrev}.tar.xz
%endif
%else
%if "%{scmrev}" == ""
Release: 0.%{beta}.1
Source: %{name}-%{version}%{beta}.tar.bz2
%else
Release: 0.%{beta}.%{scmrev}.1
Source: %{name}-%{scmrev}.tar.xz
%endif
%endif
Summary: An alternative implementation of the C++ STL
URL: http://libcxx.llvm.org/
License: MIT
Group: System/Libraries
BuildRequires: clang >= %{version}
BuildRequires: cmake
# Actually just libsupc++
BuildRequires: libstdc++-static-devel

%track
prog %{name} = {
	url = http://llvm.org/releases/download.html
	regex = "Download LLVM (__VER__)"
	version = %{version}
}

%description
libc++ is a new implementation of the C++ standard library, targeting C++11.

Features and Goals:

* Correctness as defined by the C++11 standard.
* Fast execution.
* Minimal memory use.
* Fast compile times.
* ABI compatibility with gcc's libstdc++ for some low-level features such as
  exception objects, rtti and memory allocation.
* Extensive unit tests.


%package -n %{libname}
Summary: Runtime library for the libc++ STL implementation
Group: System/Libraries

%description -n %{libname}
Runtime library for the libc++ STL implementation

%package -n %{devname}
Summary: Development files for %{name}
Group: Development/C
Requires: %{libname} = %{EVRD}

%description -n %{devname}
Development files (Headers etc.) for %{name}.

%prep
%if "%{scmrev}" == ""
%setup -q -n libcxx-%{version}%{beta}
%else
%setup -q -n %{name}
%endif
%if "%{_lib}" != "lib"
sed -i -e 's,DESTINATION lib,DESTINATION %{_lib},g' lib/CMakeLists.txt
%endif
mkdir build
cd build
C=clang CXX=clang++ cmake -G "Unix Makefiles" -DLIBCXX_CXX_ABI=libsupc++ -DLIBCXX_LIBSUPCXX_INCLUDE_PATHS="$(dirname $(find /usr/include/c++/[4-9]* -name thread));$(dirname $(find /usr/include/c++/[4-9]* -name bits |grep -v 32 |grep -vE '[0-9]/bits' |head -n1))" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=%{_prefix} ..

%build
cd build
%make

%install
cd build
%makeinstall_std

%files -n %{libname}
%{_libdir}/*.so.%{major}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/*.so
