# このリポジトリの更新の決まり

公開されるのは、いちばん新しいタグの中身。main に入れただけでは公開されない。
公開先は Cloudflare Pages（https://hissandou.pages.dev/ ）。release の作業がタグの中身を `site` ブランチに写し、Cloudflare が `site` を本番として公開する。
このリポジトリは private。古いアドレス（https://math-san-bit.github.io/denken/ ）は、public のリポジトリ math-san-bit/math-san-bit.github.io の denken/ から新しいアドレスへ転送している。

1. 更新は `feature/<内容>` のブランチに入れる。main に直に登録しない
2. main へのプルリクエストを作る。検査（check）が通ることと、目で見た確かめの承認を待つ
   - 目で見る場所: Cloudflare がブランチごとに作る確かめ用のアドレス `https://<ブランチ名の / を - に替えた物>.hissandou.pages.dev/`（例: feature/kaizen-1124 → `https://feature-kaizen-1124.hissandou.pages.dev/`）。プルリクエストの説明に、このアドレスを書く。対象は feature/* と claude/* のブランチ。確かめ用のアドレスは検索に載らない
3. 承認が出たら main にマージし、main の先頭に次の番号のタグ（`v1`、`v2`、…）を付けて push する。release の作業が、そのタグを公開する
4. 公開の後に、公開中の頁を開いて確かめる
5. 問題が出たら、Actions の release を「Run workflow」で開き、戻したいタグを入れて実行する。直しは、あらためて feature のブランチから進める

- 手元での検査: `python3 .github/scripts/check_site.py .`
- 公開のアドレス（canonical、og:url、sitemap、feed、llms.txt など）は、`.html` を外した形で書く（例 `https://hissandou.pages.dev/tanraku-100`、`https://hissandou.pages.dev/musen/`）。Cloudflare Pages は `.html` 付きのアドレスを外した形へ転送するため。サイトの中の相対リンク（`tanraku-100.html`）はそのままでよい。検査がこれを確かめる
- 新しい頁を足したら、転送用のリポジトリ（math-san-bit.github.io）の denken/ にも同じ名前の転送の頁を足す必要はない（新しい頁は古いアドレスで出回っていないため）
- 登録者の名前とアドレスは、匿名のもの（GitHub の noreply など）だけを使う
- `.md` のファイルと `.github` は公開されない
