# このリポジトリの更新の決まり

公開されるのは、いちばん新しいタグの中身。main に入れただけでは公開されない。

1. 更新は `feature/<内容>` のブランチに入れる。main に直に登録しない
2. main へのプルリクエストを作る。検査（check）が通ることと、目で見た確かめの承認を待つ
   - 目で見る場所: `https://raw.githack.com/math-san-bit/denken/<ブランチ名>/index.html`（プルリクエストの説明に、このアドレスを書く）
3. 承認が出たら main にマージし、main の先頭に次の番号のタグ（`v1`、`v2`、…）を付けて push する。release の作業が、そのタグを公開する
4. 公開の後に、公開中の頁を開いて確かめる
5. 問題が出たら、Actions の release を「Run workflow」で開き、戻したいタグを入れて実行する。直しは、あらためて feature のブランチから進める

- 手元での検査: `python3 .github/scripts/check_site.py .`
- 登録者の名前とアドレスは、匿名のもの（GitHub の noreply など）だけを使う
- `.md` のファイルと `.github` は公開されない
