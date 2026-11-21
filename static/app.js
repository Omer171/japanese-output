// Page logic only: shows state from /api/state and records with MediaRecorder (R5).
// All rules (XP, streak, SRS, unlocking) run on the server in japanese_output/.
"use strict";

const $ = (id) => document.getElementById(id);
const MAX_SESSION_SECONDS = 60 * 60;
const LEVEL_INFO = {
  beginner: "Just starting out",
  N5: "Basic phrases, kana",
  N4: "Everyday conversation",
  N3: "Intermediate",
  N2: "Upper intermediate",
  N1: "Advanced",
};
const STEP_NAMES = {
  describe: "Describe", story: "Tell a story", opinion: "Your opinion", other_side: "Argue the other side",
  summarize: "Summarize", details: "Details", reaction: "Your reaction",
};

let S = null;          // latest summary from server
let activeStep = 0;
let rec = null;        // {recorder, chunks, stream, startedAt, elapsedBefore, tick, paused}
let lastBlob = null;
let lastSeconds = 0;

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children) node.append(c instanceof Node ? c : document.createTextNode(c));
  return node;
}

async function api(path, opts = {}) {
  const res = await fetch(path, opts);
  const body = await res.json();
  if (!res.ok) throw new Error(body.error || res.statusText);
  return body;
}
const postJSON = (path, data) =>
  api(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });

const fmt = (sec) => `${String(Math.floor(sec / 60)).padStart(2, "0")}:${String(Math.floor(sec % 60)).padStart(2, "0")}`;

// ---------- render ----------

function render() {
  $("streak").textContent = S.streak;
  $("streak-icon").classList.toggle("dead", S.streak === 0);
  $("level").textContent = `Lv ${S.level}`;
  $("xpfill").style.width = `${(100 * S.level_into) / S.level_needed}%`;
  $("xptext").textContent = `${S.level_into} / ${S.level_needed} XP`;
  $("wordcount").textContent = S.word_count;
  $("jlpt").textContent = S.jlpt || "-";

  const needsLevel = !S.jlpt;
  $("onboarding").classList.toggle("hidden", !needsLevel);
  $("main").classList.toggle("hidden", needsLevel);
  if (needsLevel) return renderOnboarding();

  renderPlan();
  renderGrammar();
  renderGoal(rec ? currentSeconds() : 0);
  renderTree();
  loadHistory();
}

function renderOnboarding() {
  const box = $("level-buttons");
  box.replaceChildren(
    ...S.levels.map((lv) =>
      el("button", { onclick: () => chooseLevel(lv) }, el("b", {}, lv === "beginner" ? "Beginner" : lv), el("span", {}, LEVEL_INFO[lv]))
    )
  );
}

function renderPlan() {
  const p = S.plan;
  const kind = $("plan-kind");
  kind.textContent = p.kind === "retelling" ? "Retelling day" : "Today's topic";
  kind.className = "tag" + (p.kind === "retelling" ? " retelling" : "");
  $("plan-date").textContent = p.date;
  $("plan-title").textContent = p.title;
  $("source-wrap").classList.toggle("hidden", p.kind !== "retelling");
  const ol = $("prompts");
  ol.replaceChildren(
    ...p.prompts.map((pr, i) =>
      el("li", { class: i === activeStep ? "active" : i < activeStep ? "done" : "", onclick: () => { activeStep = i; renderPlan(); } },
        el("div", { class: "step-name" }, STEP_NAMES[pr.step] || pr.step),
        el("div", { class: "ja", lang: "ja" }, pr.prompt),
        el("div", { class: "en" }, pr.en))
    )
  );
  $("next-step").disabled = activeStep >= p.prompts.length - 1;
}

function grammarItem(gid, isNew) {
  const g = S.grammar[gid];
  if (!g) return null;
  return el("li", {},
    el("div", {}, el("span", { class: "pattern", lang: "ja" }, g.pattern),
      el("span", { class: "tag" + (isNew ? " gold" : "") }, isNew ? "new" : "review"),
      el("span", { class: "tag" }, g.level)),
    el("div", {}, g.meaning),
    el("div", { class: "ex", lang: "ja" }, g.example));
}

function renderGrammar() {
  const p = S.plan;
  const items = [
    ...p.new_grammar.map((g) => grammarItem(g, true)),
    ...p.review_grammar.map((g) => grammarItem(g, false)),
  ].filter(Boolean);
  $("grammar").replaceChildren(...(items.length ? items : [el("li", { class: "muted" }, "You've learned every built-in point. Nice!")]));
}

function renderGoal(sessionSec) {
  const totalMin = S.minutes_today + sessionSec / 60;
  const min = S.min_minutes;
  const pct = Math.min(100, (totalMin / S.max_minutes) * 100);
  const fill = $("track-fill");
  fill.style.width = `${pct}%`;
  fill.classList.toggle("bonus", totalMin >= min);
  $("track-min").style.left = `${(min / S.max_minutes) * 100}%`;
  $("min-label").textContent = `${min} min streak goal`;
  const goal = $("goal-text");
  const left = Math.ceil(min - totalMin);
  if (totalMin >= S.max_minutes) {
    goal.textContent = "60 minutes today, max bonus reached!";
  } else if (left <= 0) {
    goal.textContent = `Streak safe ✓ Bonus XP until 60 min (${Math.floor(totalMin)} min today)`;
  } else {
    goal.textContent = `${left} more min today to keep your streak` + (S.minutes_today ? ` (${S.minutes_today} min done)` : "");
  }
  goal.classList.toggle("met", left <= 0);
}

function renderTree() {
  const credits = S.unlock_credits;
  const tag = $("credits");
  tag.textContent = credits ? `${credits} unlock${credits > 1 ? "s" : ""} available: pick a branch!` : "Level up to unlock branches";
  tag.className = "tag" + (credits ? " gold" : "");
  const tiers = {};
  for (const n of S.tree) (tiers[n.tier] = tiers[n.tier] || []).push(n);
  const tierNames = ["Start", "Basics", "Branches", "Deeper", "Abstract", "Philosophy"];
  $("tree").replaceChildren(
    ...Object.keys(tiers).sort().map((t) =>
      el("div", { class: "tier" },
        el("div", { class: "tier-label" }, tierNames[t] || `Tier ${t}`),
        ...tiers[t].map((n) => {
          const cls = `node ${n.status}` + (S.plan && S.plan.topic_id === n.id ? " current" : "");
          const kids = [n.status === "locked" ? "🔒 " + n.title : n.title];
          if (n.count) kids.push(el("span", { class: "count" }, `×${n.count}`));
          if (n.status === "unlockable" && credits) kids.push(el("button", { onclick: () => unlock(n.id) }, "Unlock"));
          return el("div", { class: cls, lang: "ja" }, ...kids);
        })))
  );
}

async function loadHistory() {
  const list = await api("/api/sessions");
  const ul = $("history");
  if (!list.length) return ul.replaceChildren(el("li", { class: "muted" }, "Your recordings will show up here."));
  ul.replaceChildren(
    ...list.slice(0, 30).map((s) =>
      el("li", {},
        el("div", {}, el("b", { lang: "ja" }, s.title), s.source ? ` (${s.source})` : ""),
        el("div", { class: "meta" }, `${s.date} · ${s.minutes} min · +${s.xp} XP` + (s.words.length ? ` · ${s.words.length} new words` : "")),
        s.recording ? el("audio", { controls: "", preload: "none", src: `/recordings/${encodeURIComponent(s.recording)}` }) : ""))
  );
}

// ---------- actions ----------

async function refresh() { S = await api("/api/state"); render(); }

async function chooseLevel(level) {
  S = await postJSON("/api/level", { level });
  activeStep = 0;
  render();
}

async function unlock(topicId) {
  try { S = await postJSON("/api/unlock", { topic_id: topicId }); render(); }
  catch (e) { alert(e.message); }
}

// ---------- recording (R5) ----------

function currentSeconds() {
  if (!rec) return 0;
  return rec.elapsedBefore + (rec.paused ? 0 : (Date.now() - rec.startedAt) / 1000);
}

function tick() {
  const sec = currentSeconds();
  $("timer").textContent = fmt(sec);
  renderGoal(sec);
  if (sec >= MAX_SESSION_SECONDS) stopRecording();
}

async function startRecording() {
  if (lastBlob && !confirm("You haven't claimed XP for your last recording. Start a new one and discard it?")) return;
  lastBlob = null;
  $("rec-error").classList.add("hidden");
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (e) {
    $("rec-error").textContent = "Couldn't use the microphone: " + e.message + ". Allow mic access and try again.";
    $("rec-error").classList.remove("hidden");
    return;
  }
  const recorder = new MediaRecorder(stream);
  rec = { recorder, stream, chunks: [], startedAt: Date.now(), elapsedBefore: 0, paused: false };
  recorder.ondataavailable = (e) => e.data.size && rec.chunks.push(e.data);
  recorder.onstop = onRecordingStopped;
  recorder.start(1000);
  rec.tick = setInterval(tick, 250);
  $("timer").classList.add("recording");
  $("rec-start").classList.add("hidden");
  $("rec-pause").classList.remove("hidden");
  $("rec-stop").classList.remove("hidden");
  $("review").classList.add("hidden");
  $("result").classList.add("hidden");
}

function togglePause() {
  if (rec.paused) {
    rec.recorder.resume();
    rec.startedAt = Date.now();
    rec.paused = false;
    $("rec-pause").textContent = "❚❚ Pause";
    $("timer").classList.add("recording");
  } else {
    rec.recorder.pause();
    rec.elapsedBefore = currentSeconds();
    rec.paused = true;
    $("rec-pause").textContent = "▶ Resume";
    $("timer").classList.remove("recording");
  }
}

function stopRecording() {
  if (!rec || rec.recorder.state === "inactive") return;
  lastSeconds = Math.min(MAX_SESSION_SECONDS, currentSeconds());
  clearInterval(rec.tick);
  rec.recorder.stop();
  rec.stream.getTracks().forEach((t) => t.stop());
}

function onRecordingStopped() {
  lastBlob = new Blob(rec.chunks, { type: rec.recorder.mimeType || "audio/webm" });
  rec = null;
  $("timer").classList.remove("recording");
  $("rec-start").classList.remove("hidden");
  $("rec-start").textContent = "● Speak more";
  $("rec-pause").classList.add("hidden");
  $("rec-pause").textContent = "❚❚ Pause";
  $("rec-stop").classList.add("hidden");
  $("playback").src = URL.createObjectURL(lastBlob);
  buildChecklist();
  $("review").classList.remove("hidden");
  $("review").scrollIntoView({ behavior: "smooth" });
}

function buildChecklist() {
  const p = S.plan;
  const todo = [...p.new_grammar, ...p.review_grammar].filter((g) => !p.graded.includes(g) && S.grammar[g]);
  $("check-wrap").classList.toggle("hidden", !todo.length);
  $("grammar-checks").replaceChildren(
    ...todo.map((gid) =>
      el("label", { lang: "ja" }, el("input", { type: "checkbox", value: gid }), `${S.grammar[gid].pattern}: ${S.grammar[gid].meaning}`))
  );
}

function parseWords(text) {
  return text.split("\n").map((line) => line.trim()).filter(Boolean).map((line) => {
    const m = line.split(/\s*[=:：]\s*|\s+-\s+/);
    return { word: m[0], meaning: m.slice(1).join(" ") };
  });
}

async function submitSession() {
  const btn = $("submit");
  btn.disabled = true;
  const form = new FormData();
  form.append("seconds", String(Math.floor(lastSeconds)));
  form.append("grammar_used", JSON.stringify([...document.querySelectorAll("#grammar-checks input:checked")].map((i) => i.value)));
  form.append("words", JSON.stringify(parseWords($("words").value)));
  form.append("source", $("source").value);
  if (lastBlob) form.append("audio", lastBlob, "session");
  try {
    S = await api("/api/session", { method: "POST", body: form });
    showResult(S.result);
    lastBlob = null;
    $("words").value = "";
    $("review").classList.add("hidden");
    render();
  } catch (e) {
    alert("Couldn't save the session: " + e.message);
  } finally {
    btn.disabled = false;
  }
}

function showResult(r) {
  const rows = [
    ["Minutes spoken", r.xp.minutes],
    ["Bonus minutes", r.xp.bonus],
    ["Grammar used", r.xp.grammar],
    ["New words", r.xp.words],
  ].filter(([, v]) => v > 0);
  const box = $("result");
  box.replaceChildren(
    el("div", { class: "big" }, `+${r.xp.total} XP`),
    el("table", {}, ...rows.map(([k, v]) => el("tr", {}, el("td", {}, k), el("td", {}, `+${v}`)))),
    r.level_after > r.level_before
      ? el("div", { class: "levelup" }, `LEVEL UP! Lv ${r.level_after}: pick a new branch on the tree 🌱`)
      : "",
    el("p", {}, r.qualified ? `🔥 ${r.streak} day streak!` : `${Math.max(0, S.min_minutes - r.minutes.day_total)} more min today to keep your streak.`)
  );
  box.classList.remove("hidden");
  box.scrollIntoView({ behavior: "smooth" });
}

// ---------- wire up ----------

$("next-step").addEventListener("click", () => { activeStep++; renderPlan(); });
$("rec-start").addEventListener("click", startRecording);
$("rec-pause").addEventListener("click", togglePause);
$("rec-stop").addEventListener("click", stopRecording);
$("submit").addEventListener("click", submitSession);
$("discard").addEventListener("click", () => {
  if (!confirm("Throw away this recording without claiming XP?")) return;
  lastBlob = null;
  $("review").classList.add("hidden");
});
$("change-level").addEventListener("click", () => {
  const lv = prompt(`Your Japanese level (${S.levels.join(", ")}):`, S.jlpt || "");
  if (lv) chooseLevel(lv.trim()).catch((e) => alert(e.message));
});

if (!window.MediaRecorder) {
  $("rec-error").textContent = "This browser can't record audio. Try a recent Chrome, Edge or Firefox.";
  $("rec-error").classList.remove("hidden");
  $("rec-start").disabled = true;
}

refresh().catch((e) => { document.body.prepend(el("p", { class: "error" }, "Couldn't load: " + e.message)); });
