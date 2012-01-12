#
# Spec file generated by kdist version v0.0-23-g95cd
#
%define name		kernel-generic
%define version		3.2

%define src_uname_r	3.2-1
%define uname_r		3.2.0-1.1-generic%{nil}

%define source_release	1
%define build_release	1%{nil}

%define archive		kernel-generic-3.2-1.1

%define build_srpm	1
%define no_source	1

%define source_path	/usr/src/linux-%{src_uname_r}

%define flavour		generic

%define exclusive	%ix86

%define build_devel	1
%define build_debug	1

%define kdevel_path	/usr/src/devel/%{uname_r}
%ifarch %ix86
%define asm		x86_32
%define asmarch		x86
%endif
Name:			%{name}
Version:		%{version}
Release:		%mkrel %{source_release}.%{build_release}
License:		GPLv2
URL:			http://www.kernel.org
ExclusiveArch:		%{exclusive}
BuildRoot:		%{_tmppath}/%{name}-%{version}-root

%if %build_debug
%global __debug_package	1
%endif

%define debug_package	%{nil}
%define __check_files	%{nil}

Source0:		%{archive}.tar.bz2
Source1:		3.2.0-1.1-generic-x86_32-defconfig
Source2:		3.2.0-1.1-generic-x86-develfiles.list
Source3:		3.2.0-1.1-generic-develfiles.list
Source4:		3.2.0-1.1-generic-output-develfiles.list

Summary:		The Linux Kernel for Mandriva %{flavour} systems
Provides:		kernel = %{version}-%{release}
Group:			System/Kernel and hardware
Requires:		kernel-firmware
Requires(pre):		bootloader-utils
Requires(pre):		mkinitrd
Requires(pre):		module-init-tools
BuildRequires:		module-init-tools

%if %no_source
BuildRequires:		kernel-source = %{version}-%{mkrel %{source_release}}
%endif

%if %build_devel
%package devel
Summary:		The minimal Linux Kernel for building %{flavour} kernel modules
Provides:		kernel-devel = %{version}-%{release}
Group:			Development/Kernel
AutoReqProv:		no
%endif

%if %build_debug
%package debuginfo
Summary:		The debug information for the %{flavour} kernel
Provides:		kernel-debuginfo = %{version}-%{release}
Group:			Development/Debug
AutoReqProv:		no
%endif

%description -n %{name}

This kernel is compiled for desktop use, single or multiple i586 processor(s)/core(s),
less than 4GB RAM, using voluntary preempt, CFS cpu scheduler and cfq i/o scheduler.
This kernel relies on in-kernel smp alternatives to switch between up & smp
mode depending on detected hardware. To force the kernel to boot in single
processor mode, use the 'nosmp' boot parameter.


%if %build_devel
%description -n %{name}-devel
This package provides headers, makefiles and a couple of others files
sufficient to build external modules for %{name}.
%endif

%if %build_debug
%description -n %{name}-debuginfo
This package provides the %{name}'s debug information required
by some binary object tools like kgdb, perf, etc...
%endif

%prep
%if %build_srpm
%setup -q -n %{archive}
cp %{_sourcedir}/%{uname_r}-%{asm}-defconfig .config

%if %no_source
make -C %{source_path} O=$(pwd) outputmakefile
%endif

# localversion is updated here so the user can increase
# the release number anytime.
echo -n .%{build_release} >localversion

%endif

%build
make oldconfig
# Sanity check uname_r (it can be modified)
test %{uname_r} = $(make -s kernelrelease)

%if %build_srpm
make %{?_smp_mflags}
%endif

%install
if grep -q CONFIG_MODULES=y .config
then
	#
	# Don't specify parallel jobs here since it may break modules
	# installation somehow...
	#
	make -s INSTALL_MOD_PATH=%{buildroot} modules_install

	#
	# Mark all kernel modules as executable so they will be
	# stripped and their corresponding debug info files will be
	# generated if needed.
	#
	find %{buildroot} -name \*.ko -exec chmod u+x {} \;
else
	mkdir -p %{buildroot}/lib/modules/%{uname_r}
fi
mkdir -p %{buildroot}/boot

# symlinks are always created.
ln -snf %{kdevel_path} %{buildroot}/lib/modules/%{uname_r}/build
ln -snf build %{buildroot}/lib/modules/%{uname_r}/source
%ifarch %ix86
cp arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{uname_r}
cp System.map %{buildroot}/boot/System.map-%{uname_r}
cp .config %{buildroot}/boot/config-%{uname_r}
%endif

%if %build_devel
mkdir -p %{buildroot}%{kdevel_path}

%if %no_source
cd source
%endif

for list in %{_sourcedir}/%{uname_r}{,-%asmarch}-develfiles.list; do
	tar -cf - --files-from=$list | tar -xf - -C %{buildroot}%{kdevel_path}
done

%if %no_source
cd -
%endif

list=%{_sourcedir}/%{uname_r}-output-develfiles.list
tar -cf - --files-from=$list | tar -xf - -C %{buildroot}%{kdevel_path}

# localversion might exist when generating a rpm package, in that case
# use it.
test -f localversion && cp localversion %{buildroot}%{kdevel_path}

make -C %{buildroot}%{kdevel_path} modules_prepare
%endif

%clean
rm -rf %{buildroot}

%post
%ifarch %ix86
/sbin/installkernel %{uname_r}
%endif

%postun
%ifarch %ix86
/sbin/kernel_remove_initrd %{uname_r}
%endif

%preun
%ifarch %ix86
/sbin/installkernel -R %{uname_r}
%endif

%files -n %{name}
%defattr (-, root, root)
/boot
%dir /lib/modules
/lib/modules/%{uname_r}

%if %build_devel
%files -n %{name}-devel
%defattr (-, root, root)
%kdevel_path
%endif

%if %build_debug
%files -n %{name}-debuginfo -f debugfiles.list
%defattr (-, root, root)
%endif

%changelog
* Thu Jan 12 2012 Franck Bui <franck.bui@mandriva.com> 3.2.0-1.1-generic
  + Mandriva Release v3.2-1
  + Subject: vfs: fix shrink_dcache_parent() livelock
  + Prevent BCMA from taking the BCM4313 device
  + Revert "staging: brcm80211: only enable brcmsmac if bcma is not set"
  + dcache: use a dispose list in select_parent
  + [overlayfs] fs: limit filesystem stacking depth
  + [overlayfs] vfs: introduce clone_private_mount()
  + [overlayfs] vfs: export do_splice_direct() to modules
  + [overlayfs] vfs: add i_op->open()
  + [overlayfs] vfs: pass struct path to __dentry_open()
  + pci: Rework ASPM disable code
  + usb: ehci: make HC see up-to-date qh/qtd descriptor ASAP
  + Mandriva Linux boot logo.
  + media video pwc no ads in dmesg
  + media video pwc lie in proc usb devices
  + usb storage unusual_devs add id 2.6.37 buildfix
  + Change to usb storage of unusual_dev.
  + Add blacklist of usb hid modules
  + bluetooth hci_usb disable isoc transfers
  + sound alsa hda ad1884a hp dc model
  + Support a Bluetooth SCO.
  + Include kbuild export pci_ids
  + platform x86 add shuttle wmi driver
  + net netfilter psd 2.6.35 buildfix
  + ipt_psd: Mandriva changes
  + net netfilter psd
  + net netfilter IFWLOG 2.6.37 buildfix
  + IFWLOG netfilter: fix return value of ipt_IFWLOG_checkentry()
  + net netfilter IFWLOG 2.6.35 buildfix
  + netfilter ipt_IFWLOG: Mandriva changes
  + net netfilter IFWLOG
  + net sis190 fix list usage
  + kbuild compress kernel modules on installation
  + gpu drm mach64 3.2 buildfix
  + gpu drm mach64 2.6.39 buildfix
  + gpu drm mach64 2.6.37 buildfix
  + gpu drm mach64 2.6.36 buildfix
  + gpu drm mach64 fix for changed drm_ioctl
  + gpu drm mach64 fix for changed drm_pci_alloc
  + gpu drm mach64 2.6.31 buildfix
  + gpu drm mach64 fixes
  + gpu drm mach64
  + agp/intel: add new host bridge id for Q57 system
  + mpt scsi modules for VMWare's emulated
  + ide pci sis5513 965
  + ppscsi: build fix for 2.6.39
  + scsi megaraid new sysfs name
  + scsi ppscsi mdvbz45393
  + scsi ppscsi update for scsi_data_buffer
  + scsi ppscsi sg helper update
  + scsi ppscsi_fixes
  + scsi ppscsi-2.6.2
  + acpi video add blacklist to use vendor driver
  + acpi processor M720SR limit to C2
  + CLEVO M360S acpi irq workaround
  + acpi add proc event regs
  + acpi dsdt initrd v0.9c fixes
  + acpi dsdt initrd v0.9c 2.6.28
  + UBUNTU: SAUCE: isapnp_init: make isa PNP scans occur async
  + pnp pnpbios off by default
  + PCI: Add ALI M5229 IDE comaptibility mode quirk
  + Card bus's PCI last bus
  + x86, cpufreq: set reasonable default for scaling_min_freq with p4-clockmod
  + x86 cpufreq speedstep dothan 3
  + default to "power_off" when SMP kernel is used on single processor machines
  + x86 boot video 80x25 if break
  + x86 pci toshiba equium a60 assign busses
  + kdist: make the config name part of the localversion
  + kdist: give a name to the config file
