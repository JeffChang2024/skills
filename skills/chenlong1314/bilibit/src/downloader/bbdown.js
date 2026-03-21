/**
 * BBDown wrapper for Bilibili video downloading
 * @module downloader/bbdown
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * Check if BBDown is installed
 * @returns {boolean}
 */
function isBBDownInstalled() {
  try {
    // 优先使用本地 BBDown
    const localBBDown = path.join(__dirname, '..', '..', 'node_modules', '.bin', 'BBDown');
    if (fs.existsSync(localBBDown)) {
      return true;
    }
    
    // 否则使用全局 BBDown
    execSync('BBDown --version', { stdio: 'ignore' });
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Get default download directory
 * @returns {string}
 */
function getDefaultDownloadDir() {
  const homeDir = process.env.HOME || process.env.USERPROFILE;
  const downloadDir = path.join(homeDir, 'Downloads', 'bilibit');
  
  if (!fs.existsSync(downloadDir)) {
    fs.mkdirSync(downloadDir, { recursive: true });
  }
  
  return downloadDir;
}

/**
 * Build BBDown command arguments
 * @param {string} url - Video URL
 * @param {Object} options - Download options
 * @returns {string[]}
 */
function buildArgs(url, options = {}) {
  const args = [];
  
  // Video URL
  args.push(url);
  
  // Quality selection
  if (options.quality) {
    args.push('-p', options.quality);
  }
  
  // Download danmaku
  if (options.danmaku) {
    args.push('--danmaku');
  }
  
  // Cookie file
  if (options.cookieFile) {
    args.push('--cookie', options.cookieFile);
  }
  
  // Output directory
  const outputDir = options.outputDir || getDefaultDownloadDir();
  args.push('-d', outputDir);
  
  // Video format
  args.push('--video-accept-ids', '127,126,125,120,116,112,80,74,64,32,16');
  
  // Audio format
  args.push('--audio-accept-ids', '30280,30232,30216,30280');
  
  return args;
}

/**
 * Download a Bilibili video using BBDown
 * @param {string} url - Video URL or BV/AV ID
 * @param {Object} options - Download options
 * @param {string} options.quality - Video quality (4K, 1080P, etc.)
 * @param {boolean} options.danmaku - Download danmaku
 * @param {string} options.cookieFile - Path to cookie file
 * @param {string} options.outputDir - Output directory
 * @returns {Promise<{success: boolean, output?: string, error?: string}>}
 */
async function download(url, options = {}) {
  return new Promise((resolve) => {
    // Check BBDown installation
    if (!isBBDownInstalled()) {
      resolve({
        success: false,
        error: 'BBDown not installed. Please install with: brew install bbdown'
      });
      return;
    }
    
    const args = buildArgs(url, options);
    console.log('Downloading:', url);
    console.log('Command: bbdown', args.join(' '));
    
    const child = spawn('bbdown', args, {
      stdio: ['inherit', 'pipe', 'pipe']
    });
    
    let output = '';
    let errorOutput = '';
    
    child.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      process.stdout.write(text);
    });
    
    child.stderr.on('data', (data) => {
      const text = data.toString();
      errorOutput += text;
      process.stderr.write(text);
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve({
          success: true,
          output: output.trim()
        });
      } else {
        resolve({
          success: false,
          error: errorOutput.trim() || `BBDown exited with code ${code}`
        });
      }
    });
    
    child.on('error', (err) => {
      resolve({
        success: false,
        error: err.message
      });
    });
  });
}

/**
 * Parse video URL to extract BV/AV ID
 * @param {string} url - Video URL
 * @returns {string|null}
 */
function extractVideoId(url) {
  const patterns = [
    /\/video\/(BV\w+)/,
    /\/video\/(av\d+)/,
    /(BV\w+)/,
    /(av\d+)/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) {
      return match[1];
    }
  }
  
  return null;
}

module.exports = {
  isBBDownInstalled,
  download,
  extractVideoId,
  getDefaultDownloadDir
};
