# Kickstart Skill - 自动化安装

## 技能描述 | Skill Description

**名称 | Name:** kickstart  
**版本 | Version:** 1.0.0  
**作者 | Author:** OS Build Agent  
**领域 | Domain:** Automated System Installation  

专业的 Kickstart 自动化安装配置技能，支持 RHEL/Fedora/CentOS 等系统的无人值守安装配置生成和管理。

Professional Kickstart automated installation configuration skill supporting unattended installation configuration generation and management for RHEL/Fedora/CentOS systems.

---

## 功能列表 | Features

### 1. Kickstart 文件生成 | Kickstart File Generation
- 基础配置生成 | Basic config generation
- 完整配置生成 | Full config generation
- 模板化配置 | Template configs
- 验证语法 | Syntax validation

### 2. 分区配置 | Partition Configuration
- 自动分区 | Automatic partitioning
- 自定义分区 | Custom partitioning
- LVM 配置 | LVM configuration
- RAID 配置 | RAID configuration
- Btrfs 配置 | Btrfs configuration

### 3. 包管理 | Package Management
- 包组选择 | Package group selection
- 包安装列表 | Package install list
- 包排除 | Package exclusion
- 模块配置 | Module configuration

### 4. 网络配置 | Network Configuration
- 网络接口配置 | Network interface config
- 主机名配置 | Hostname configuration
- DNS 配置 | DNS configuration
- Bonding/Teaming | Bonding/Teaming

### 5. 用户配置 | User Configuration
- root 密码 | Root password
- 用户创建 | User creation
- SSH 密钥 | SSH keys
- 用户组 | User groups

### 6. 后期配置 | Post Installation
- 脚本执行 | Script execution
- 服务配置 | Service configuration
- 系统优化 | System optimization
- 自定义命令 | Custom commands

---

## 配置 | Configuration

### 工具安装 | Tool Installation

```bash
# RHEL/Fedora
dnf install system-config-kickstart
dnf install pykickstart

# 验证工具
# Validation tools
dnf install ksvalidator
```

### Kickstart 文件位置 | Kickstart File Locations

```bash
# 标准位置
# Standard locations
/boot/isolinux/ks.cfg
/var/www/html/ks.cfg

# 网络位置
# Network locations
http://example.com/ks.cfg
ftp://example.com/ks.cfg
nfs:server:/path/ks.cfg
```

---

## 使用示例 | Usage Examples

### 基础 Kickstart 文件 | Basic Kickstart File

```bash
# basic.ks 示例
# basic.ks example
cat > basic.ks << 'EOF'
# Platform
x86_64

# Language
lang en_US.UTF-8

# Keyboard
keyboard us

# Timezone
timezone America/New_York --utc

# Root password (encrypted)
rootpw --iscrypted $6$rounds=10000$hash...

# Bootloader
bootloader --location=mbr --boot-drive=sda

# Partition clearing
clearpart --all --initlabel

# Automatic partitioning
autopart --type=lvm

# Network
network --bootproto=dhcp --device=eth0 --onboot=on

# Services
services --enabled=sshd,NetworkManager

# Firewall
firewall --enabled --service=ssh

# SELinux
selinux --enforcing

# Packages
%packages
@core
vim
wget
curl
%end

# Reboot after installation
reboot
EOF
```

### 自定义分区 | Custom Partitioning

```bash
# custom-partition.ks 示例
# custom-partition.ks example
cat > custom-partition.ks << 'EOF'
# Bootloader
bootloader --location=mbr --append="rhgb quiet"

# Clear MBR
zerombr

# Clear partitions
clearpart --all --initlabel --drives=sda

# EFI partition
part /boot/efi --fstype="efi" --size=500

# Boot partition
part /boot --fstype="xfs" --size=1024

# Root partition
part / --fstype="xfs" --size=20000

# Home partition
part /home --fstype="xfs" --size=10000

# Swap
part swap --size=4096

# LVM 配置
# LVM configuration
part pv.01 --size=10000
volgroup myvg pv.01
logvol /var --fstype="xfs" --name=var --vgname=myvg --size=5000
logvol /tmp --fstype="xfs" --name=tmp --vgname=myvg --size=2000

# RAID 配置
# RAID configuration
raid /boot --level=1 --device=md0 raid.01 raid.02
part raid.01 --size=1024 --ondisk=sda
part raid.02 --size=1024 --ondisk=sdb
EOF
```

### 网络配置 | Network Configuration

```bash
# network.ks 示例
# network.ks example
cat > network.ks << 'EOF'
# DHCP 配置
# DHCP configuration
network --bootproto=dhcp --device=eth0 --onboot=on

# 静态 IP 配置
# Static IP configuration
network --bootproto=static \
  --ip=192.168.1.100 \
  --netmask=255.255.255.0 \
  --gateway=192.168.1.1 \
  --nameserver="8.8.8.8,8.8.4.4" \
  --device=eth0 \
  --onboot=on \
  --ipv6=auto

# 主机名
# Hostname
network --hostname=myserver.example.com

# Bonding 配置
# Bonding configuration
network --bootproto=dhcp \
  --device=bond0 \
  --bondslaves=eth0,eth1 \
  --bondopts=mode=active-backup,miimon=100 \
  --onboot=on

# Team 配置
# Team configuration
network --bootproto=dhcp \
  --device=team0 \
  --teamslaves="p3p1'{\"prio\": -10, \"sticky\": true}',p3p2'{\"prio\": 100}'" \
  --teamconfig="{\"runner\": {\"name\": \"activebackup\"}}" \
  --onboot=on
EOF
```

### 用户配置 | User Configuration

```bash
# user.ks 示例
# user.ks example
cat > user.ks << 'EOF'
# Root 密码（明文，不推荐）
# Root password (plaintext, not recommended)
rootpw --plaintext mypassword

# Root 密码（加密，推荐）
# Root password (encrypted, recommended)
rootpw --iscrypted $6$rounds=10000$hash...

# 创建用户
# Create user
user --name=admin \
  --groups=wheel \
  --password=mypassword \
  --iscrypted \
  --gecos="Admin User"

# 创建用户（SSH 密钥）
# Create user (SSH key)
user --name=deploy \
  --groups=wheel \
  --sshkey="ssh-rsa AAAAB3... user@example.com"

# 禁用 root 登录
# Disable root login
# (在 %post 中配置)
EOF
```

### 包管理 | Package Management

```bash
# packages.ks 示例
# packages.ks example
cat > packages.ks << 'EOF'
# 包组
# Package groups
%packages
@core
@standard
@development
@gnome-desktop

# 单个包
# Individual packages
vim
wget
curl
git
htop
iotop
tcpdump

# 排除包
# Exclude packages
%excluded
firewalld
postfix
sendmail

# 文档
# Documentation
%doc

# 忽略缺失的包组
# Ignore missing package groups
%packages --ignoremissing
@minimal-environment
%end
EOF
```

### 后期配置脚本 | Post Installation Scripts

```bash
# post.ks 示例
# post.ks example
cat > post.ks << 'EOF'
# 安装后脚本
# Post installation script
%post --interpreter=/bin/bash

# 日志
# Logging
exec > /root/ks-post.log 2>&1

# 更新系统
# Update system
dnf update -y

# 安装额外包
# Install extra packages
dnf install -y \
  vim-enhanced \
  wget \
  curl \
  git \
  htop

# 配置 SSH
# Configure SSH
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# 禁用不需要的服务
# Disable unnecessary services
systemctl disable bluetooth.service
systemctl disable cups.service

# 启用需要的服务
# Enable necessary services
systemctl enable chronyd.service
systemctl enable NetworkManager.service

# 系统优化
# System optimization
echo "vm.swappiness=10" >> /etc/sysctl.conf
echo "net.ipv4.ip_forward=0" >> /etc/sysctl.conf
sysctl -p

# 清理
# Cleanup
dnf clean all
rm -f /root/anaconda-ks.cfg

%end

# 第一次重启后脚本
# First boot script
%firstboot --interpreter=/bin/bash
dnf install -y additional-packages
%end

# 预安装脚本
# Pre installation script
%pre --interpreter=/bin/bash
# 检测硬件
# Detect hardware
lspci > /tmp/lspci.txt
%end
EOF
```

### 完整示例 | Complete Example

```bash
# complete.ks 示例
# complete.ks example
cat > complete.ks << 'EOF'
# Kickstart file for Production Server
# version=DEVEL

# 系统信息
# System information
lang en_US.UTF-8
keyboard us
timezone Asia/Shanghai --utc

# 认证
# Authentication
rootpw --iscrypted $6$rounds=10000$hash...
user --name=admin --groups=wheel --password=hash --iscrypted

# 引导加载器
# Bootloader
bootloader --location=mbr --append="rhgb quiet"

# 分区
# Partitioning
clearpart --all --initlabel
autopart --type=lvm --encrypted --passphrase=mypassphrase

# 网络
# Network
network --bootproto=dhcp --device=eth0 --onboot=on --hostname=server.example.com

# 防火墙
# Firewall
firewall --enabled --service=ssh

# SELinux
# SELinux
selinux --enforcing

# 包
# Packages
%packages --ignoremissing
@core
@standard
vim
wget
curl
git
htop
%end

# 后期配置
# Post installation
%post
exec > /root/ks-post.log 2>&1
dnf update -y
dnf install -y vim-enhanced htop
systemctl enable chronyd
%end

# 重启
# Reboot
reboot
EOF
```

---

## 工具使用 | Tool Usage

### KSValidator 验证 | KSValidator Validation

```bash
# 验证 Kickstart 文件
# Validate Kickstart file
ksvalidator basic.ks

# 验证并输出详细信息
# Validate with verbose output
ksvalidator -v basic.ks

# 检查语法错误
# Check syntax errors
ksvalidator --syntax-only basic.ks
```

### System-config-kickstart GUI

```bash
# 启动图形界面
# Start GUI
system-config-kickstart

# 打开现有文件
# Open existing file
system-config-kickstart existing.ks
```

### 生成 Kickstart 文件 | Generate Kickstart File

```bash
# 从现有系统生成
# Generate from existing system
cp /root/anaconda-ks.cfg ~/my.ks

# 使用 pykickstart 生成
# Generate with pykickstart
ksflatten --file=base.ks --file=packages.ks > combined.ks
```

---

## 命令参考 | Command Reference

### Kickstart 命令 | Kickstart Commands

| 命令 | Command | 描述 | Description |
|------|---------|------|-------------|
| `lang` | language | 设置语言 | Set language |
| `keyboard` | keyboard | 设置键盘 | Set keyboard |
| `timezone` | timezone | 设置时区 | Set timezone |
| `rootpw` | root password | 设置 root 密码 | Set root password |
| `user` | user | 创建用户 | Create user |
| `bootloader` | bootloader | 引导配置 | Boot configuration |
| `clearpart` | clear partitions | 清除分区 | Clear partitions |
| `part`/`partition` | partition | 创建分区 | Create partition |
| `autopart` | auto partition | 自动分区 | Auto partition |
| `network` | network | 网络配置 | Network config |
| `firewall` | firewall | 防火墙配置 | Firewall config |
| `selinux` | SELinux | SELinux 配置 | SELinux config |
| `services` | services | 服务配置 | Service config |
| `%packages` | packages | 包配置 | Package config |
| `%post` | post | 安装后脚本 | Post script |
| `%pre` | pre | 安装前脚本 | Pre script |

---

## 最佳实践 | Best Practices

### 1. 安全性 | Security
- 使用加密密码 | Use encrypted passwords
- 启用 SELinux | Enable SELinux
- 配置防火墙 | Configure firewall
- 禁用 root SSH 登录 | Disable root SSH login

### 2. 可维护性 | Maintainability
- 模块化 Kickstart 文件 | Modularize Kickstart files
- 添加注释 | Add comments
- 版本控制 | Version control
- 文档化 | Document

### 3. 测试 | Testing
- 在虚拟机中测试 | Test in VM
- 验证所有配置 | Verify all configs
- 检查日志 | Check logs

---

## 故障排除 | Troubleshooting

### 安装失败 | Installation Failed
```bash
# 检查日志
# Check logs
cat /tmp/anaconda.log
cat /tmp/storage.log

# 进入救援模式
# Enter rescue mode
# 在启动参数中添加：
# linux rescue
```

### 网络问题 | Network Issues
```bash
# 测试网络连接
# Test network connection
ping -c 4 8.8.8.8

# 检查 DNS
# Check DNS
cat /etc/resolv.conf
```

---

## 参考资料 | References

- [Kickstart 官方文档 | Kickstart Official Docs](https://docs.fedoraproject.org/en-US/fedora/f39/install-guide/install/Kickstart_Syntax_Reference/)
- [Anaconda 文档 | Anaconda Docs](https://anaconda-installer.readthedocs.io/en/latest/)
- [Pykickstart 文档 | Pykickstart Docs](https://pykickstart.readthedocs.io/)

---

## 许可证 | License

MIT License

---

## 更新日志 | Changelog

### v1.0.0 (2026-03-23)
- 初始版本，完整的 Kickstart 支持
- Initial release with full Kickstart support
- 中英文双语文档
- Bilingual documentation (Chinese/English)
