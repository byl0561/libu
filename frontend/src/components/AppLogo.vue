<template>
  <!--
    礼簿品牌图标：礼盒 + 蝴蝶结
    ViewBox 36×36，白色描边，CSS 容器提供渐变底色
  -->
  <svg
    viewBox="0 0 36 36"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style="display:block;width:100%;height:100%"
    aria-hidden="true"
  >
    <!-- 礼盒盒体 -->
    <rect x="5" y="20" width="26" height="13" rx="2.5"
      stroke="white" stroke-width="2.2" fill="none"/>
    <!-- 盒体上沿横向丝带 -->
    <rect x="5" y="20" width="26" height="4.5" rx="0"
      fill="rgba(255,255,255,.14)" stroke="none"/>
    <!-- 竖向丝带 -->
    <line x1="18" y1="20" x2="18" y2="33"
      stroke="white" stroke-width="1.8" stroke-linecap="round"/>
    <!-- 蝴蝶结左翼 -->
    <path d="M 18,20 C 14,13 5,11 7,17 C 8,21 18,20 18,20"
      stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
      fill="rgba(255,255,255,.14)"/>
    <!-- 蝴蝶结右翼 -->
    <path d="M 18,20 C 22,13 31,11 29,17 C 28,21 18,20 18,20"
      stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
      fill="rgba(255,255,255,.14)"/>
    <!-- 结扣（中心点）-->
    <circle cx="18" cy="20" r="2.6" fill="white"/>
  </svg>
</template>
