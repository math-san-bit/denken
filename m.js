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

  /* 解説のページの終わりに、「解けそうか」の2択を出す。押された答えだけを数える */
  document.addEventListener("DOMContentLoaded", function () {
    var up = document.querySelector("p.updated");
    if (!up || !document.querySelector(".answer") || !document.querySelector(".crumb")) { return; }
    var box = document.createElement("div");
    box.className = "check";
    box.innerHTML = '<strong>この説明で、同じ形の問題を自分で解けそうですか。</strong><br>' +
      '<button type="button" class="btn" data-a="yes">解けそう</button>　<button type="button" class="btn" data-a="no">まだ少し不安</button>' +
      '<p id="helpmsg" role="status"></p>';
    up.parentNode.insertBefore(box, up);
    var sent = false;
    box.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("button[data-a]") : null;
      if (!b) { return; }
      var yes = b.getAttribute("data-a") === "yes";
      if (!sent) { sent = true; ev(yes ? "helpful_yes" : "helpful_no", { page: (location.pathname.split("/").pop() || "index").slice(0, 40) }); }
      document.getElementById("helpmsg").textContent = yes
        ? "ありがとうございます。確かめの1問が解けたら、次のページへ進んでください。"
        : "ありがとうございます。このページは、説明を足す候補にします。10問の点検で、ほかに止まる所が無いかも確かめられます。";
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
