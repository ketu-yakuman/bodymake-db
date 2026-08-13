// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
//
// 独自ドメイン(bodymake-record.com)を設定済み。ルート直下で公開されるため
// サブパスは無し(base: '/')。
export default defineConfig({
  site: 'https://bodymake-record.com',
  base: '/',
});
