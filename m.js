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
  var live = location.hostname === "math-san-bit.github.io" && !off;
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
  var site = pn.indexOf("/musen/") >= 0 ? "musen" : (/\/denken\/(index\.html)?$/.test(pn) ? "top" : "denken");
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
  var BOOKS = {
    v1: ["第1巻『複素数とベクトル図』", "j の付いた数の計算と、ベクトル図の向き", "B0HLYB3HQY"],
    v2: ["第2巻『パーセントインピーダンスの計算がわかる』", "基準容量の換算と、短絡電流・短絡容量", "B0HLXHL4PM"],
    v3: ["第3巻『三相交流の計算がわかる』", "√3 を掛けるのか割るのかと、Y結線・Δ結線", "B0HMMDKGDW"],
    v4: ["第4巻『力率改善の計算がわかる』", "コンデンサーの容量と、力率を上げる計算", "B0HNDJMNTQ"],
    v5: ["第5巻『変圧器の計算がわかる』", "巻数比を掛けるのか割るのかと、効率の計算", "B0HPYX48YY"],
    v6: ["第6巻『需要率・不等率・負荷率の計算がわかる』", "需要率・不等率・負荷率と、変圧器の容量の決め方", "B0HQVZ88JP"]
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
        '<div><p class="honcard-lead">同じ形を、もう何問か解いて固めたいときの1冊</p>' +
        '<p class="honcard-title">' + book[0] + '</p>' +
        '<p>' + book[1] + 'を、途中の式から順に解く本です。全部の巻は要りません。</p>' +
        '<p><a class="btn" data-book="' + id + '" href="https://www.amazon.co.jp/dp/' + book[2] + '">Amazon で見る</a></p>' +
        '<p class="honcard-sub"><a href="hon.html">ほかの巻の案内</a></p></div>';
      link.parentNode.parentNode.replaceChild(card, link.parentNode);
      card.addEventListener("click", function (e) {
        if (e.target.closest && e.target.closest("a[data-book]")) { ev("book_click", { page: page, book: id }); }
      });
    }

    var box = document.createElement("div");
    box.className = "check";
    box.innerHTML = '<strong>この説明で、同じ形の問題を自分で解けそうですか。</strong><br>' +
      '<button type="button" class="btn" data-a="yes">解けそう</button>　<button type="button" class="btn" data-a="no">まだ少し不安</button>' +
      '<div id="helpmsg" role="status"></div>';
    up.parentNode.insertBefore(box, up);
    var sent = false, shown = false;
    box.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("button[data-a]") : null;
      if (!b) { return; }
      var yes = b.getAttribute("data-a") === "yes";
      if (!sent) { sent = true; ev(yes ? "helpful_yes" : "helpful_no", { page: page }); }
      var msg = document.getElementById("helpmsg");
      if (yes) {
        msg.innerHTML = "<p>ありがとうございます。上の「次に読む」から、次の止まる所へ進んでください。</p>";
      } else if (card) {
        msg.innerHTML = "<p>ありがとうございます。このページは、説明を足す候補にします。</p>";
        msg.appendChild(card);
        if (!shown) { shown = true; ev("book_shown", { page: page, book: id }); }
      } else {
        msg.innerHTML = "<p>ありがとうございます。このページは、説明を足す候補にします。10問の点検で、ほかに止まる所が無いかも確かめられます。</p>";
      }
    });
  });

  /* 読んだページの印。このブラウザーの中だけに置き、どこにも送らない */
  document.addEventListener("DOMContentLoaded", function () {
    try {
      var key = "jiten_read";
      var list = JSON.parse(localStorage.getItem(key) || "[]");
      var me = location.pathname.split("/denken/").pop();
      if (document.querySelector(".answer") && document.querySelector(".crumb") && list.indexOf(me) < 0) {
        list.push(me);
        localStorage.setItem(key, JSON.stringify(list.slice(-200)));
      }
      document.querySelectorAll("ul.list a").forEach(function (a) {
        if (a.host !== location.host) { return; }
        var p = a.pathname.split("/denken/").pop();
        if (p !== me && list.indexOf(p) >= 0) { a.insertAdjacentHTML("afterend", '<span class="read">読んだ</span>'); }
      });
    } catch (e) {}
  });
})();
