#!/usr/bin/env node

/**
 * BBDown 自动安装脚本
 * 安装 bilibit 时自动下载 BBDown
 */

const { execSync } = require('child_process');
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

console.log('🔍 检查 BBDown 依赖...\n');

// 检查 BBDown 是否已安装
function checkBBDown() {
  try {
    execSync('which BBDown', { stdio: 'ignore' });
    console.log('✅ BBDown 已安装\n');
    return true;
  } catch (error) {
    console.log('⚠️  BBDown 未安装\n');
    return false;
  }
}

// 下载 BBDown
function downloadBBDown() {
  const platform = os.platform();
  const arch = os.arch();
  
  console.log('📦 正在下载 BBDown...\n');
  
  // 选择正确的版本
  let downloadUrl = '';
  let outputName = 'BBDown';
  
  if (platform === 'darwin') {
    // macOS
    if (arch === 'arm64') {
      downloadUrl = 'https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown-net6.0-osx-arm64';
    } else {
      downloadUrl = 'https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown-net6.0-osx-x64';
    }
  } else if (platform === 'linux') {
    // Linux
    if (arch === 'arm64') {
      downloadUrl = 'https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown-net6.0-linux-arm64';
    } else {
      downloadUrl = 'https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown-net6.0-linux-x64';
    }
  } else if (platform === 'win32') {
    // Windows
    outputName = 'BBDown.exe';
    downloadUrl = 'https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown-net6.0-win-x64.exe';
  } else {
    console.log('❌ 不支持的操作系统:', platform);
    console.log('请手动安装：https://github.com/nilaoda/BBDown/releases\n');
    return false;
  }
  
  // 安装到本地 node_modules/.bin
  const installDir = path.join(__dirname, '..', 'node_modules', '.bin');
  const installPath = path.join(installDir, outputName);
  
  try {
    // 确保目录存在
    if (!fs.existsSync(installDir)) {
      fs.mkdirSync(installDir, { recursive: true });
    }
    
    // 下载文件
    return new Promise((resolve) => {
      const file = fs.createWriteStream(installPath);
      
      https.get(downloadUrl, (response) => {
        if (response.statusCode !== 200) {
          console.log('❌ 下载失败:', response.statusCode);
          console.log('请手动安装：https://github.com/nilaoda/BBDown/releases\n');
          resolve(false);
          return;
        }
        
        response.pipe(file);
        
        file.on('finish', () => {
          file.close();
          fs.chmodSync(installPath, '755');
          console.log('✅ BBDown 安装成功:', installPath);
          console.log('🎉 bilibit 已就绪！\n');
          console.log('使用示例：');
          console.log('  bilibit search "LOL 集锦"');
          console.log('  bilibit https://b23.tv/BV1xx\n');
          resolve(true);
        });
      }).on('error', (err) => {
        fs.unlink(installPath, () => {});
        console.log('❌ 下载失败:', err.message);
        console.log('请手动安装：https://github.com/nilaoda/BBDown/releases\n');
        resolve(false);
      });
    });
  } catch (error) {
    console.log('❌ 安装失败:', error.message);
    console.log('请手动安装：https://github.com/nilaoda/BBDown/releases\n');
    return false;
  }
}

// 主流程
async function main() {
  console.log('════════════════════════════════════════');
  console.log('🎬 bilibit 依赖安装');
  console.log('════════════════════════════════════════\n');
  
  if (checkBBDown()) {
    return;
  }
  
  await downloadBBDown();
}

main();
