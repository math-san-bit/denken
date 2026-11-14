/* 読まれ方を数える（Google アナリティクス）。入力の中身や、点検でどの選択肢を選んだかは送らない。 */
(function () {
  var ID = "G-T409Z08E27";
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", ID, { allow_google_signals: false, allow_ad_personalization_signals: false });

  var pn = location.pathname;
  var site = pn.indexOf("/musen/") >= 0 ? "musen" : (/\/denken\/(index\.html)?$/.test(pn) ? "top" : "denken");
  function ev(name, p) {
    p = p || {};
    p.site = site;
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

  /* 解説のページの終わりに、「解けそうか」の2択を出す。押された答えだけを数える。
     「まだ少し不安」の人には、そのページに合う本を1冊だけ示す */
  var BOOKS = {
    v1: ["第1巻『複素数とベクトル図』", "j の付いた数の計算と、ベクトル図の向き"],
    v2: ["第2巻『パーセントインピーダンスの計算がわかる』", "基準容量の換算と、短絡電流・短絡容量"],
    v3: ["第3巻『三相交流の計算がわかる』", "√3 を掛けるのか割るのかと、Y結線・Δ結線"],
    v4: ["第4巻『力率改善の計算がわかる』", "コンデンサーの容量と、力率を上げる計算"],
    v5: ["第5巻『変圧器の計算がわかる』", "巻数比を掛けるのか割るのかと、効率の計算"],
    v6: ["第6巻『需要率・不等率・負荷率の計算がわかる』", "需要率・不等率・負荷率と、変圧器の容量の決め方"]
  };
  document.addEventListener("DOMContentLoaded", function () {
    var up = document.querySelector("p.updated");
    if (!up || !document.querySelector(".answer") || !document.querySelector(".crumb")) { return; }
    var page = (location.pathname.split("/").pop() || "index").slice(0, 40);
    var link = document.querySelector('main p > a[href^="hon.html#v"]');
    var id = link ? link.getAttribute("href").split("#")[1] : "";
    var book = BOOKS[id];
    var box = document.createElement("div");
    box.className = "check";
    box.innerHTML = '<strong>この説明で、同じ形の問題を自分で解けそうですか。</strong><br>' +
      '<button type="button" class="btn" data-a="yes">解けそう</button>　<button type="button" class="btn" data-a="no">まだ少し不安</button>' +
      '<div id="helpmsg" role="status"></div>';
    up.parentNode.insertBefore(box, up);
    var sent = false, shown = false;
    box.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target : null;
      if (!t) { return; }
      if (t.closest("a[data-book]")) { ev("book_click", { page: page, book: id }); return; }
      var b = t.closest("button[data-a]");
      if (!b) { return; }
      var yes = b.getAttribute("data-a") === "yes";
      if (!sent) { sent = true; ev(yes ? "helpful_yes" : "helpful_no", { page: page }); }
      var msg = document.getElementById("helpmsg");
      if (yes) {
        msg.innerHTML = "<p>ありがとうございます。上の「次に読む」から、次の止まる所へ進んでください。</p>";
      } else if (book) {
        msg.innerHTML = "<p>ありがとうございます。このページは、説明を足す候補にします。</p>" +
          "<p><strong>同じ形を、もう何問か解いて固めたいときの1冊</strong><br>" + book[0] + "は、" + book[1] +
          "を、途中の式から順に解く本です。全部の巻は要りません。この1冊で足ります。</p>" +
          '<p><a class="btn" data-book="' + id + '" href="hon.html#' + id + '">' + book[0].split("『")[0] + "の案内を見る</a></p>";
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
