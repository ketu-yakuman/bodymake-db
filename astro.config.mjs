// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
//
// 現状(独自ドメイン未取得)は https://ketu-yakuman.github.io/bodymake-db/ という
// サブパス配下で公開される想定の設定にしてある。
// ・リポジトリ名を変える場合は base の "bodymake-db" 部分も合わせて変更すること。
// ・独自ドメインを取得して GitHub Pages に設定したら、サブパスが無くなり
//   ルート直下で公開されるようになるので、その時点で以下2行を書き換える:
//     site: 'https://あなたのドメイン',
//     base: '/',
export default defineConfig({
  site: 'https://ketu-yakuman.github.io',
  base: '/bodymake-db/',
});
