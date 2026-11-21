/* 読まれ方を数える（Google アナリティクス）。入力の中身や、点検でどの選択肢を選んだかは送らない。 */
(function () {
  var ID = "G-T409Z08E27";
  /* 数えるのは、公開のアドレスだけ。確かめ用のアドレスと、「数えない」を選んだブラウザーでは送らない */
  var off = false;
  try {
    var q = /[?&]kazoenai=([01])/.exec(location.search);
    if (q) { if (q[1] === "1") { localStorage.setItem("jiten_off", "1"); } else { localStorage.removeItem("jiten_off"); } }
    off = localStorage.getItem("jiten_off") === "1";
  } catch (e) {}
  var live = location.hostname === "hissandou.pages.dev" && !off;
  window.jitenLive = live;
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  if (live) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
    document.head.appendChild(s);
    gtag("js", new Date());
    gtag("config", ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
  }

  var pn = location.pathname;
  var site = pn.indexOf("/musen/") >= 0 ? "musen" : (/^\/(index(\.html)?)?$/.test(pn) ? "top" : "denken");
  function ev(name, p) {
    p = p || {};
    p.site = site;
    if (!live) { return; }
    try { gtag("event", name, p); } catch (e) {}
  }
  window.jitenEvent = ev;

  /* 読み進めた深さ：25・50・75・100% */
  var marks = [25, 50, 75, 100], seen = {};
  function depth() {
    var h = document.documentElement;
    var max = h.scrollHeight - window.innerHeight;
    var pct = max <= 0 ? 100 : Math.round((window.scrollY / max) * 100);
    marks.forEach(function (m) {
      if (pct >= m && !seen[m]) { seen[m] = 1; ev("read_depth", { percent: m }); }
    });
  }
  window.addEventListener("scroll", depth, { passive: true });
  window.addEventListener("load", depth);

  /* 滞在：画面が見えている間だけ数えて、30秒・60秒・180秒 */
  var t = 0, steps = [30, 60, 180], passed = {};
  setInterval(function () {
    if (document.visibilityState !== "visible") { return; }
    t++;
    steps.forEach(function (m) {
      if (t >= m && !passed[m]) { passed[m] = 1; ev("stay", { seconds: m }); }
    });
  }, 1000);

  /* 押された行き先 */
  document.addEventListener("click", function (e) {
    var a = e.target.closest ? e.target.closest("a") : null;
    if (!a) { return; }
    var h = a.href || "";
    if (a.hasAttribute("data-chizu")) { ev("chizu", { kind: a.getAttribute("data-chizu"), from: (location.pathname.split("/").pop() || "index").slice(0, 40), dest: (a.pathname.split("/").pop() || "index").slice(0, 40) }); }
    if (h.indexOf("amazon.co.jp") >= 0) { ev("go_book", { dest: (h.split("/dp/")[1] || h).slice(0, 40) }); }
    else if (h.indexOf("booth.pm") >= 0) { ev("go_booth", { dest: h.slice(0, 80) }); }
    else if (h.indexOf("tenken.html") >= 0) { ev("go_tenken", {}); }
    else if (a.host === location.host) { ev("go_page", { dest: (a.pathname.split("/").pop() || "index").slice(0, 40) }); }
  });

  /* 確かめの1問の答えを開いた */
  document.addEventListener("toggle", function (e) {
    if (e.target && e.target.tagName === "DETAILS" && e.target.open) { ev("open_answer", {}); }
  }, true);

  /* 解説のページの終わり：本の1冊の案内と、「解けそうか」の2択。押された答えだけを数える。
     「まだ少し不安」の人には、案内を答えのすぐ下へ動かして見せる */
  /* 書名と ASIN は、KDP の本棚（2026-11-15）のとおり。[書名, 扱う所, Kindle 版, 紙の本] */
  var BOOKS = {
    v1: ["電験三種の数学 つまずき解消ノート1　複素数とベクトル図", "j の付いた数の計算と、ベクトル図の向き", "B0HLYB3HQY", "B0HLW1DPG8"],
    v2: ["パーセントインピーダンスの計算がわかる　電験三種の短絡電流・短絡容量・変圧器", "基準容量の換算と、短絡電流・短絡容量", "B0HLXHL4PM", "B0HLXM1YQ1"],
    v3: ["三相交流の計算がわかる　電験三種の√3・Y結線・Δ結線・三相電力", "√3 を掛けるのか割るのかと、Y結線・Δ結線", "B0HMMDKGDW", "B0HMMZH7T4"],
    v4: ["力率改善の計算がわかる　電験三種のコンデンサー容量・損失・電圧降下・直列リアクトル", "コンデンサーの容量と、力率を上げる計算", "B0HNDJMNTQ", "B0HNDJSFBW"],
    v5: ["変圧器の計算がわかる　電験三種の等価回路・損失・効率・全日効率", "巻数比を掛けるのか割るのかと、効率の計算", "B0HPYX48YY", "B0HPZ48PJ9"],
    v6: ["需要率・不等率・負荷率の計算がわかる　電験三種 法規の負荷計算と変圧器の容量", "需要率・不等率・負荷率と、変圧器の容量の決め方", "B0HQVZ88JP", "B0HQVWT9D8"]
  };
  document.addEventListener("DOMContentLoaded", function () {
    var up = document.querySelector("p.updated");
    if (!up || !document.querySelector(".answer") || !document.querySelector(".crumb")) { return; }
    var page = (location.pathname.split("/").pop() || "index").slice(0, 40);
    var link = document.querySelector('main p > a[href^="hon.html#v"]');
    var id = link ? link.getAttribute("href").split("#")[1] : "";
    var book = BOOKS[id];

    /* 本の1行を、表紙の付いた案内に置き換える。押すと Amazon の商品のページへ進む */
    var card = null;
    if (book) {
      card = document.createElement("div");
      card.className = "honcard";
      card.innerHTML = '<img src="img/cover-' + id + '.jpg" alt="' + book[0] + ' の表紙" width="360" height="576" loading="lazy">' +
        '<div><p class="honcard-lead">同じ型の問題を、もう少し解いておきたい人へ</p>' +
        '<p class="honcard-title">' + book[0] + '</p>' +
        '<p>' + book[1] + 'を、途中の式を省かずに解いていく本です。全巻をそろえる必要はなく、この1冊から読めます。</p>' +
        '<p class="honcard-lead">電験数学ノート編集室 著。Kindle 版と、紙の本があります。</p>' +
        '<p><a class="btn btn-amazon" data-micro="試し読みできます" data-book="' + id + '" href="https://www.amazon.co.jp/dp/' + book[2] + '">Kindle 版を Amazon で見る</a></p>' +
        '<p class="honcard-sub"><a data-book="' + id + '" href="https://www.amazon.co.jp/dp/' + book[3] + '">紙の本を Amazon で見る</a>　<a href="hon.html">ほかの巻の案内</a></p></div>';
      link.parentNode.parentNode.replaceChild(card, link.parentNode);
      card.addEventListener("click", function (e) {
        if (e.target.closest && e.target.closest("a[data-book]")) { ev("book_click", { page: page, book: id }); }
      });
    }

    /* 一陸特・一陸技：問題集の案内がある解説では、BOOTH の問題集を1品だけ、同じ形で用意する */
    var mlink = document.querySelector('main p > a[href="mondaishu.html"]');
    if (!card && mlink) {
      id = "booth40";
      card = document.createElement("div");
      card.className = "honcard";
      card.innerHTML = '<img src="../img/mondaishu-sample.jpg" alt="問題集の見本のページ" width="900" loading="lazy">' +
        '<div><p class="honcard-lead">同じ型の問題を、紙の上で繰り返したい人へ</p>' +
        '<p class="honcard-title">電卓なしのデシベル 書き込み式の問題集 40問</p>' +
        '<p>デシベルの出し入れを、途中の式を自分で書き込みながら固める問題集です。PDF（A4・10ページ）、300円。</p>' +
        '<p class="honcard-lead">過去問題そのものではありません。合格を約束する物でもありません。</p>' +
        '<p><a class="btn" data-micro="見本つき" data-book="' + id + '" href="mondaishu.html">中身と見本を見る</a></p>' +
        '<p class="honcard-sub"><a data-book="' + id + '" href="https://tsumazuki-techo.booth.pm/items/9144717">BOOTH の商品のページへ（300円）</a></p></div>';
      card.addEventListener("click", function (e) {
        if (e.target.closest && e.target.closest("a[data-book]")) { ev("book_click", { page: page, book: id }); }
      });
    }

    var box = document.createElement("div");
    box.className = "check";
    box.innerHTML = '<strong>この説明で、同じ形の問題を自分で解けそうですか。</strong><br>' +
      '<button type="button" class="btn" data-a="yes">解けそう</button>　<button type="button" class="btn" data-a="no">まだ少し不安</button>' +
      '<div id="helpmsg" role="status"></div>';
    /* 2択は、確かめの1問のすぐ下に置く（解いた直後に、次の一歩を1つだけ示す）。確かめの1問が無い頁では、終わりに置く */
    var qs = document.querySelectorAll("main div.check details");
    var kq = qs.length ? qs[qs.length - 1].closest("div.check") : null;
    if (kq && kq.parentNode) { kq.parentNode.insertBefore(box, kq.nextSibling); }
    else { up.parentNode.insertBefore(box, up); }
    var nx = document.querySelector("main nav.next a");
    var sent = false, shown = false;
    box.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("button[data-a]") : null;
      if (!b) { return; }
      var yes = b.getAttribute("data-a") === "yes";
      if (!sent) { sent = true; ev(yes ? "helpful_yes" : "helpful_no", { page: page }); }
      var msg = document.getElementById("helpmsg");
      if (yes) {
        if (nx) {
          msg.innerHTML = "<p>ありがとうございます。次の止まる所へ進めます。</p>";
          var na = document.createElement("a");
          na.className = "btn"; na.href = nx.getAttribute("href"); na.textContent = "次へ：" + nx.textContent;
          var np = document.createElement("p"); np.appendChild(na); msg.appendChild(np);
        } else {
          msg.innerHTML = "<p>ありがとうございます。下の「次に読む」から、次の止まる所へ進んでください。</p>";
        }
      } else if (card) {
        msg.innerHTML = "<p>ありがとうございます。このページは、説明を足す候補にします。</p>";
        msg.appendChild(card);
        if (!shown) { shown = true; ev("book_shown", { page: page, book: id }); }
      } else {
        msg.innerHTML = "<p>ありがとうございます。このページは、説明を足す候補にします。10問の点検で、ほかに止まる所が無いかも確かめられます。</p>";
      }
    });
  });

  /* 解説のページに、目次を出す */
  document.addEventListener("DOMContentLoaded", function () {
    if (!document.querySelector(".answer") || !document.querySelector(".crumb")) { return; }
    var hs = document.querySelectorAll("main > h2");
    if (hs.length < 3) { return; }
    var html = "<strong>このページの目次</strong><ol>";
    for (var i = 0; i < hs.length; i++) {
      if (!hs[i].id) { hs[i].id = "s" + (i + 1); }
      html += '<li><a href="#' + hs[i].id + '">' + hs[i].textContent + "</a></li>";
    }
    var nav = document.createElement("nav");
    nav.className = "toc";
    nav.setAttribute("aria-label", "このページの目次");
    nav.innerHTML = html + "</ol>";
    hs[0].parentNode.insertBefore(nav, hs[0]);
  });

  /* 読んだページの印。このブラウザーの中だけに置き、どこにも送らない */
  document.addEventListener("DOMContentLoaded", function () {
    try {
      var key = "jiten_read";
      var list = JSON.parse(localStorage.getItem(key) || "[]");
      var me = location.pathname.replace(/^\//, "").replace(/(index)?\.html$/, "").replace(/\/index$/, "/");
      if (document.querySelector(".answer") && document.querySelector(".crumb") && list.indexOf(me) < 0) {
        list.push(me);
        localStorage.setItem(key, JSON.stringify(list.slice(-200)));
      }
      document.querySelectorAll("ul.list a").forEach(function (a) {
        if (a.host !== location.host) { return; }
        var p = a.pathname.replace(/^\//, "").replace(/(index)?\.html$/, "").replace(/\/index$/, "/");
        if (p !== me && list.indexOf(p) >= 0) { a.insertAdjacentHTML("afterend", '<span class="read">読んだ</span>'); }
      });
    } catch (e) {}
  });
})();
