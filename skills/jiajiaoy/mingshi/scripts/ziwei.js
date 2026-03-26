#!/usr/bin/env node
/**
 * 紫微斗数排盘脚本
 * 输入：出生年月日时分、性别
 */

const { getLunarMonth, isAfterLiChun } = require('./jieqi');

// 地支信息
const diZhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const diZhiHour = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

// 天干
const tianGan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];

// 十四正曜
const mainStars = [
  '紫微', '天机', '太阳', '武曲', '天同', '廉贞',
  '天府', '太阴', '贪狼', '巨门', '天相', '天梁',
  '七杀', '破军'
];

// 辅曜
const assistStars = [
  '左辅', '右弼', '文昌', '文曲', '天魁', '天铖',
  '禄存', '天马', '化禄', '化权', '化科', '化忌'
];

// 十二宫
const twelvePalaces = [
  '命宫', '兄弟宫', '夫妻宫', '子女宫',
  '财帛宫', '疾厄宫', '迁移宫', '奴仆宫',
  '官禄宫', '田宅宫', '福德宫', '父母宫'
];

// 紫微斗数安星法则（简化版）
// 以农历出生年为基准

/**
 * 计算天干
 */
function getYearGan(year) {
  const ganIndex = (year - 4) % 10;
  return tianGan[ganIndex < 0 ? ganIndex + 10 : ganIndex];
}

/**
 * 计算地支
 */
function getYearZhi(year) {
  const zhiIndex = (year - 4) % 12;
  return diZhi[zhiIndex < 0 ? zhiIndex + 12 : zhiIndex];
}

/**
 * 计算命宫
 */
function getMingGong(yearZhi, month, day, hour) {
  // 简化：以年支为主，配合月时
  const zhiIndex = diZhi.indexOf(yearZhi);
  let mingGongIndex = (zhiIndex + month) % 12;
  return twelvePalaces[mingGongIndex];
}

/**
 * 安紫微星（简化）
 */
function getZiWeiPosition(yearGan, yearZhi) {
  // 简化安星法
  const ganZhi = yearGan + yearZhi;
  
  // 根据年支找紫微所在宫位
  const ziWeiPalace = {
    '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
    '辰': '巳', '巳': '午', '午': '未', '未': '申',
    '申': '酉', '酉': '戌', '戌': '亥', '亥': '子'
  };
  
  return ziWeiPalace[yearZhi] || '子';
}

/**
 * 安天府星（简化）
 */
function getTianFuPosition(yearZhi) {
  const tianFuPalace = {
    '子': '卯', '丑': '辰', '寅': '巳', '卯': '午',
    '辰': '未', '巳': '申', '午': '酉', '未': '戌',
    '申': '亥', '酉': '子', '戌': '丑', '亥': '寅'
  };
  return tianFuPalace[yearZhi] || '子';
}

/**
 * 安主星到各宫
 */
function arrangeMainStars(mingGongZhi, ziWeiPalace, tianFuPalace) {
  const palaceOrder = [
    '子', '丑', '寅', '卯', '辰', '巳',
    '午', '未', '申', '酉', '戌', '亥'
  ];
  
  const mingIndex = palaceOrder.indexOf(mingGongZhi);
  
  // 简化：按顺序安星
  const starPositions = {};
  
  // 紫微在指定宫位
  starPositions[ziWeiPalace] = ['紫微'];
  
  // 天府在指定宫位
  starPositions[tianFuPalace] = starPositions[tianFuPalace] || [];
  starPositions[tianFuPalace].push('天府');
  
  // 其他主星按顺序分布
  const otherStars = ['天机', '太阳', '武曲', '天同', '廉贞', '贪狼', '巨门', '天相', '天梁', '七杀', '破军'];
  let starIndex = 0;
  
  for (let i = 0; i < 12; i++) {
    const pos = palaceOrder[(mingIndex + i) % 12];
    if (!starPositions[pos]) {
      if (starIndex < otherStars.length) {
        starPositions[pos] = [otherStars[starIndex]];
        starIndex++;
      }
    }
  }
  
  return starPositions;
}

/**
 * 安四化星
 */
function getFourTransformations(yearGan) {
  // 简化四化表
  const transforms = {
    '甲': { ziWei: '权', tianJi: '科', taiYang: '忌', WuQu: '禄' },
    '乙': { ziWei: '科', tianJi: '权', taiYang: '禄', WuQu: '忌' },
    '丙': { ziWei: '忌', tianJi: '禄', taiYang: '权', WuQu: '科' },
    '丁': { ziWei: '禄', tianJi: '忌', taiYang: '科', WuQu: '权' },
    '戊': { ziWei: '权', tianJi: '科', taiYang: '禄', WuQu: '忌' },
    '己': { ziWei: '科', tianJi: '权', taiYang: '忌', WuQu: '禄' },
    '庚': { ziWei: '忌', tianJi: '禄', taiYang: '科', WuQu: '权' },
    '辛': { ziWei: '禄', tianJi: '忌', taiYang: '权', WuQu: '科' },
    '壬': { ziWei: '权', tianJi: '禄', taiYang: '科', WuQu: '忌' },
    '癸': { ziWei: '科', tianJi: '权', taiYang: '忌', WuQu: '禄' }
  };
  
  return transforms[yearGan] || transforms['甲'];
}

/**
 * 紫微星曜特质（简化）
 */
const starTraits = {
  '紫微': { trait: '尊贵、领导', element: '土', good: '权柄、贵人', bad: '孤傲、刚愎' },
  '天机': { trait: '智慧、灵动', element: '木', good: '谋略、企划', bad: '善变、投机' },
  '太阳': { trait: '热情、光明', element: '火', good: '事业、名声', bad: '冲动、耗时' },
  '武曲': { trait: '刚毅、果断', element: '金', good: '财运、武职', bad: '固执、寡情' },
  '天同': { trait: '温和、福德', element: '水', good: '享受、人缘', bad: '懒散、无主' },
  '廉贞': { trait: '刚烈、狡黠', element: '火', good: '桃花、创意', bad: '小人、纠纷' },
  '天府': { trait: '稳重、包容', element: '土', good: '财库、守成', bad: '保守、吝啬' },
  '太阴': { trait: '柔顺、敏感', element: '水', good: '感情、文艺', bad: '依赖、情绪' },
  '贪狼': { trait: '欲望、交际', element: '木', good: '桃花、社交', bad: '贪婪、酒色' },
  '巨门': { trait: '口才、疑虑', element: '土', good: '辩才、传播', bad: '是非、口舌' },
  '天相': { trait: '印绶、辅佐', element: '水', good: '文书、权印', bad: '逢灾、易骗' },
  '天梁': { trait: '荫蔽、慈善', element: '土', good: '清贵、寿考', bad: '孤僻、疾病' },
  '七杀': { trait: '威猛、肃杀', element: '金', good: '权威、创业', bad: '刑伤、意外' },
  '破军': { trait: '耗损、变动', element: '水', good: '开创、突破', bad: '破耗、反复' }
};

/**
 * 宫位特质
 */
const palaceTraits = {
  '命宫': '性格、命运基础',
  '兄弟宫': '兄弟姐妹、手足之情',
  '夫妻宫': '配偶、婚姻、感情',
  '子女宫': '子女、桃花、创作',
  '财帛宫': '财运、理财能力',
  '疾厄宫': '健康、疾病、体质',
  '迁移宫': '出行、迁移、社交',
  '奴仆宫': '下属、贵人、小人',
  '官禄宫': '事业、仕途、学业',
  '田宅宫': '房产、家运、祖业',
  '福德宫': '福气、享受、品德',
  '父母宫': '父母、学历、文书'
};

/**
 * 判断格局
 */
function judgePattern(starPositions) {
  const patterns = [];
  
  // 检查紫微天府同宫
  const hasBoth = Object.entries(starPositions).find(([pos, stars]) => 
    stars.includes('紫微') && stars.includes('天府')
  );
  if (hasBoth) {
    patterns.push('紫府同宫 - 尊贵、权柄');
  }
  
  // 检查杀破狼
  const has狼 = Object.entries(starPositions).find(([pos, stars]) => stars.includes('贪狼'));
  const has七杀 = Object.entries(starPositions).find(([pos, stars]) => stars.includes('七杀'));
  const has破军 = Object.entries(starPositions).find(([pos, stars]) => stars.includes('破军'));
  
  if (has狼 && has七杀) {
    patterns.push('贪狼七杀同宫 - 桃花与杀伐并存');
  }
  if (has破军) {
    patterns.push('破军入命 - 开创变动');
  }
  
  // 检查机月同梁
  const has机 = Object.entries(starPositions).find(([pos, stars]) => stars.includes('天机'));
  const has月 = Object.entries(starPositions).find(([pos, stars]) => stars.includes('太阴'));
  const has同 = Object.entries(starPositions).find(([pos, stars]) => stars.includes('天同'));
  const has梁 = Object.entries(starPositions).find(([pos, stars]) => stars.includes('天梁'));
  
  if (has机 && has同 && has梁) {
    patterns.push('机月同梁 - 善谋稳定');
  }
  
  return patterns.length > 0 ? patterns : ['普通格局'];
}

/**
 * 生成紫微斗数命盘报告
 */
function generateZiWeiReport(birthDate, gender, yearGan, yearZhi, monthZhi, dayZhi, hourZhi) {
  // 计算命宫地支
  const birthYear = birthDate.getFullYear();
  const birthMonth = birthDate.getMonth() + 1;
  const birthDay = birthDate.getDate();
  
  // 命宫地支：从寅宫起顺数至出生月，再逆数至出生时辰
  const lunarMonthForMing = getLunarMonth(birthYear, birthMonth, birthDay);
  const hourZhiIndex = diZhi.indexOf(hourZhi);
  const mingGongZhiIndex = ((2 + lunarMonthForMing - 1 - hourZhiIndex) % 12 + 12) % 12;
  const mingGongZhi = diZhi[mingGongZhiIndex];
  
  // 紫微所在宫位
  const ziWeiPalace = getZiWeiPosition(yearGan, yearZhi);
  
  // 天府所在宫位
  const tianFuPalace = getTianFuPosition(yearZhi);
  
  // 安星
  const starPositions = arrangeMainStars(mingGongZhi, ziWeiPalace, tianFuPalace);
  
  // 四化
  const fourTransforms = getFourTransformations(yearGan);
  
  // 格局
  const patterns = judgePattern(starPositions);
  
  // 命宫主星
  const mingStars = starPositions[mingGongZhi] || [];
  const mainStar = mingStars[0] || '天机';
  const mainStarInfo = starTraits[mainStar] || starTraits['天机'];
  
  let report = `
✨ 【紫微斗数命盘】

📋 基本信息
   出生：${birthYear}年${monthZhi}月${dayZhi}日 ${hourZhi}时
   农历：${yearGan}${yearZhi}年
   性别：${gender === '男' ? '男' : '女'}
   命宫：${mingGongZhi}宫
   命主：${mainStar}

🌟 命宫主星
   ${mainStar}（${mainStarInfo.trait}）
   五行：${mainStarInfo.element}
   优点：${mainStarInfo.good}
   缺点：${mainStarInfo.bad}

🎯 命盘格局
`;
  
  patterns.forEach(p => {
    report += `   ◆ ${p}\n`;
  });
  
  report += `
📊 主要宫位分析

`;
  
  // 显示重要宫位
  const importantPalaces = ['命宫', '夫妻宫', '官禄宫', '财帛宫', '福德宫'];
  
  importantPalaces.forEach(palace => {
    const palaceZhi = diZhi[(diZhi.indexOf(mingGongZhi) + twelvePalaces.indexOf(palace)) % 12];
    const stars = starPositions[palaceZhi] || ['无主星'];
    const traits = palaceTraits[palace] || '';
    
    report += `【${palace}】${palaceZhi}宫\n`;
    report += `   主星：${stars.join('、')}\n`;
    report += `   含意：${traits}\n\n`;
  });
  
  report += `
🔄 四化星（${yearGan}年出生）
   化禄：${fourTransforms.WuQu || '无'}
   化权：${fourTransforms.ziWei || '无'}
   化科：${fourTransforms.tianJi || '无'}
   化忌：${fourTransforms.taiYang || '无'}

💡 综合建议
   命主${mainStar}星，${mainStarInfo.trait}
   ${patterns[0]}
   宜往${mainStarInfo.element}的方向发展
`;
  
  return report;
}

// 主入口
const args = process.argv.slice(2);

if (args[0] === '--help' || args[0] === '-h') {
  console.log(`
紫微斗数排盘

用法:
  node ziwei.js <出生日期> <性别> [时辰]
  
参数:
  出生日期: YYYY-MM-DD 或 YYYYMMDD
  性别: 男 或 女
  时辰: 子丑寅卯... (可选，默认丑时)

示例:
  node ziwei.js 1990-05-15 男
  node ziwei.js 19900515 女 寅
`);
} else if (args.length < 2) {
  console.error('请提供出生日期和性别');
  console.log('用法: node ziwei.js <出生日期> <性别>');
  process.exit(1);
} else {
  let birthDateStr = args[0];
  const gender = args[1];
  const hourZhi = args[2] || '丑';
  
  // 解析日期
  let birthDate;
  if (birthDateStr.length === 8) {
    birthDate = new Date(
      parseInt(birthDateStr.substring(0, 4)),
      parseInt(birthDateStr.substring(4, 6)) - 1,
      parseInt(birthDateStr.substring(6, 8))
    );
  } else {
    birthDate = new Date(birthDateStr);
  }
  
  if (isNaN(birthDate.getTime())) {
    console.error('日期格式无效');
    process.exit(1);
  }
  
  const birthYear = birthDate.getFullYear();
  const birthMonth = birthDate.getMonth() + 1;
  const birthDay = birthDate.getDate();
  
  // 计算年干支（以立春精确时刻为界）
  const calcYear = isAfterLiChun(birthYear, birthMonth, birthDay) ? birthYear : birthYear - 1;
  const yearGan = getYearGan(calcYear);
  const yearZhi = getYearZhi(calcYear);

  // 计算月干支（以精确节气为界）
  const lunarMonth = getLunarMonth(birthYear, birthMonth, birthDay);
  const monthZhi = diZhi[(lunarMonth + 1) % 12];

  // 计算日干支（以2024-01-01甲子日为基准）
  const baseDate = new Date('2024-01-01T12:00:00');
  const diffDays = Math.round((birthDate - baseDate) / (1000 * 60 * 60 * 24));
  const dayGanIndex = (diffDays % 10 + 10) % 10; // 2024-01-01=甲子(甲=0)
  const dayZhiIndex = (diffDays % 12 + 12) % 12; // 2024-01-01=甲子(子=0)
  const dayGan = tianGan[dayGanIndex];
  const dayZhi = diZhi[dayZhiIndex];
  
  console.log(generateZiWeiReport(birthDate, gender, yearGan, yearZhi, monthZhi, dayZhi, hourZhi));
}
