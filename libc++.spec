%define debug_package %{nil}

%define major 1
%define beta %{nil}
%define scmrev 245328
%define libname %mklibname c++ %{major}
%define abilibname %mklibname c++abi %{major}
%define devname %mklibname c++ -d
%define staticname %mklibname c++ -d -s
%define unwindlibname %mklibname unwind %{major}

Name: libc++
Version: 3.7.0
%if "%{scmrev}" == ""
Release: 1
Source0: http://llvm.org/releases/%{version}/libcxx-%{version}.src.tar.xz
Source1: http://llvm.org/releases/%{version}/libcxxabi-%{version}.src.tar.xz
Source2: http://llvm.org/releases/%{version}/libunwind-%{version}.src.tar.xz
%else
Release: 0.%{scmrev}.1
Source0: libcxx-%{version}.src.tar.xz
Source1: libcxxabi-%{version}.src.tar.xz
Source2: libunwind-%{version}.src.tar.xz
%endif
Summary: An alternative implementation of the C++ STL
URL: http://libcxx.llvm.org/
License: MIT
Group: System/Libraries
BuildRequires: clang >= %{version}
BuildRequires: cmake
# Actually just libsupc++
BuildRequires: libstdc++-static-devel
# Make it buildable if the system libc is something other than glibc
# and uClibc
Patch0: libc++-3.7.0-musl-compat.patch

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

%package -n %{abilibname}
Summary: The libc++abi low level C++ runtime
Group: System/Libraries

%description -n %{abilibname}
The libc++abi low level C++ runtime

%package -n %{unwindlibname}
Summary: The LLVM unwinding library
Group: System/Libraries

%description -n %{unwindlibname}
The LLVM unwinding library

%package -n %{devname}
Summary: Development files for %{name}
Group: Development/C
Requires: %{libname} = %{EVRD}
Requires: %{abilibname} = %{EVRD}
Provides: c++-devel

%description -n %{devname}
Development files (Headers etc.) for %{name}.

%package -n %{staticname}
Summary: Static libraries for %{name}
Group: Development/C
Requires: %{devname} = %{EVRD}

%description -n %{staticname}
Static libraries for %{name}.

%prep
%setup -q -n libcxx-%{version}%{beta}.src -a 1 -a 2
%apply_patches
TOP=`pwd`

cd libunwind-%{version}%{beta}.src
%cmake \
	-DLLVM_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')"
cd ..
mkdir static
cd static
%cmake \
	-DLIBUNWIND_ENABLE_SHARED:BOOL=OFF \
	-DLLVM_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	../..
cd ../../..

cd libcxxabi-%{version}%{beta}.src
%cmake \
	-DLIBCXXABI_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	-DLIBCXXABI_LIBCXX_PATH="$TOP" \
	-DLIBCXXABI_LIBCXX_INCLUDES="$TOP"/include \
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
	-DLIBCXXABI_LIBUNWIND_SOURCES="$TOP"/libunwind-%{version}%{beta}.src \
	-DLIBCXXABI_LIBUNWIND_INCLUDES_INTERNAL="$TOP"/libunwind-%{version}%{beta}.src/include \
	-DLIBCXXABI_SHARED_LINK_FLAGS=-L"$TOP"/libunwind-%{version}%{beta}.src/build/%{_lib}
cd ../..


%cmake \
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=$TOP/libcxxabi-%{version}%{beta}.src/include \
	-DCMAKE_SHARED_LINKER_FLAGS="-L$TOP/libcxxabi-%{version}%{beta}.src/build/%{_lib}" \
	-DLIBCXX_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')"
cd ..

mkdir static
cd static
%cmake \
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=$TOP/libcxxabi-%{version}%{beta}.src/include \
	-DLIBCXX_ENABLE_SHARED:BOOL=OFF \
	-DLIBCXX_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	../..

%build
cd libunwind-%{version}%{beta}.src/static/build
%make

cd ../../build
%make

cd ../../libcxxabi-%{version}%{beta}.src/build
%make

cd ../../static/build
%make

cd ../../build
%make

%install
cd libunwind-%{version}%{beta}.src/static/build
%makeinstall_std

cd ../../build
%makeinstall_std

cd ../../libcxxabi-%{version}%{beta}.src/build
%makeinstall_std

cd ../../static/build
%makeinstall_std

cd ../../build
%makeinstall_std

# Make sure system libraries are reachable at bootup
mkdir -p %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/*.so.* %{buildroot}/%{_lib}/
cd %{buildroot}%{_libdir}
ln -sf ../../%{_lib}/libc++abi.so.%{major} libc++abi.so
ln -sf ../../%{_lib}/libc++.so.%{major} libc++.so

%files -n %{libname}
/%{_lib}/libc++.so.%{major}*

%files -n %{abilibname}
/%{_lib}/libc++abi.so.%{major}*

%files -n %{unwindlibname}
/%{_lib}/libunwind.so.%{major}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/*.so

%files -n %{staticname}
%{_libdir}/*.a
