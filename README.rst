======
Rejviz
======

Rejviz [ray-veez], VM / disk image tools built on top of
libguestfs-tools.

Design doc
==========

Use cases
---------

* Create a VM image

  * From base image

  * Having some size

  * With some script run

  * With network interfaces configured (some DHCP, some static IPs)

  * Subscribed via RHSM

* Create a VM

  * With network interface MAC addresses matching the interfaces from
    the image

  * With some RAM and vCPUs

* Amend existing VM image (or libvirt domain)

  * Reconfigure network interfaces

  * Re-subscribe via RHSM

* Tell me something about an image (or libvirt domain)

  * List network interfaces and their basic config

  * Check that MACs on the domain match MACs in
    ``/etc/sysconfig/network-scripts``

I/O view
--------

* Creating an image

  * In: params

  * Out: image

  * ``rejviz-builder`` command that proxies to virt-builder and adds
    custom params on top (RHSM, network interfaces)

* Creating a VM

  * In: image and params

  * Out: domain XML or created domain (both through virt-install)

  * ``rejviz-install`` command that proxies to virt-install and
    determines some of the parameters from the image

* Amending an image (or libvirt domain)

  * In: (image or domname) and params

  * Out: image edited in place

  * ``rejviz-customize`` command that proxies to virt-customize and
    adds custom params on top (RHSM, network interfaces)

* Image/domain introspection

  * In: (image or domname) and params

  * Out: information printed

  * ``rejviz-peek``
