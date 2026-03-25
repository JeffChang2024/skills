#!/usr/bin/env node
/**
 * test.js — 新闻转 Markdown 测试脚本
 * 
 * 测试常用新闻网站，验证三层抓取策略和内容提取效果
 */

import { extractFromUrl } from '../src/extract.js';

const TEST_URLS = [
  {
    name: '新浪新闻',
    url: 'https://news.sina.com.cn/',
    note: '静态页面，测试 curl 策略',
  },
  {
    name: '网易新闻',
    url: 'https://news.163.com/',
    note: '静态页面，测试 wget 降级',
  },
  {
    name: '腾讯新闻',
    url: 'https://news.qq.com/',
    note: '静态页面',
  },
];

async function test() {
  console.log('🧪 news-to-markdown 测试\n');

  for (const testCase of TEST_URLS) {
    console.log(`📰 ${testCase.name}`);
    console.log(`   URL: ${testCase.url}`);
    console.log(`   说明: ${testCase.note}`);

    const startTime = Date.now();

    try {
      const result = await extractFromUrl(testCase.url, {
        verbose: false,
      });

      const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

      console.log(`   ✅ 成功 (${elapsed}s)`);
      console.log(`   方式: ${result.method}`);
      console.log(`   标题: ${result.metadata.title || '(无)'}`);
      console.log(`   长度: ${result.contentLength} 字符`);
      console.log(`   图片: ${result.images.length} 张`);
    } catch (e) {
      console.log(`   ❌ 失败: ${e.message}`);
    }

    console.log('');
  }
}

test().catch(console.error);
