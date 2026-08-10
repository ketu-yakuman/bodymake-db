// GitHub Pagesの「プロジェクトページ」は https://ユーザー名.github.io/リポジトリ名/ のように
// サブパス配下で公開される。独自ドメインを付けるとサブパスは消えてルート直下になる。
// astro.config.mjs の base 設定と連動させることで、内部リンクをどちらの状態でも
// 正しく機能させる。
export function withBase(path) {
  const base = import.meta.env.BASE_URL;
  const trimmedBase = base.endsWith("/") ? base.slice(0, -1) : base;
  return `${trimmedBase}${path}`;
}
