'use strict';
// kit.js — puente entre el kit de shorts y la skill hand-drawn-canvas-animation.
// Cargar después de core.js, studio.js, cels.js, tiempos.js (TIEMPOS) y antes de vectores.js y de las escenas.
//
// Qué aporta:
//   tiempo      escena(n) → datos de la escena · dicho(E, 'palabra', k) → segundo local en que la voz la dice
//   fondo       fondoNegro(c): negro con la retícula tenue del canal
//   texto       titulares(c, E, tau) (palabra por palabra) · focos(c, E, tau) (solo palabras clave) · rotulo(...)
//   vectores    registerVector(nombre, dataURL) (lo llama vectores.js) · vector(c, nombre, x, y, escala, o)
//   personajes  pose(raw, rellenos) · actuar(tau, claves, poses) · dibujaPose(c, pose, o)
//   marcas      circuloMano(c, x, y, r, p, semilla) · subrayado(c, x0, x1, y, p, semilla)

// ── Estilo del canal sobre negro ──
const K = {
  fondo: '#000000', reticula: '#161616', tiza: '#F3EFE6', tizaSuave: '#9A958B', acento: '#FF6A1A',
  fuente: '"Avenir Next Condensed", "Arial Narrow", sans-serif', peso: 800,
  titularY: 340, titularTam: 120, focoY: 640, focoTam: 92,
};
const PAL_CANAL = makePalette({ paper: K.fondo, ink: K.tiza, night: K.fondo, chalk: K.tiza, chalkDim: K.tizaSuave,
  light: '#2a2724', shade: '#55504a', fills: ['#C99A6B', '#8FA6B8', '#B9AFA1', '#E3B35C'], accents: [K.acento, '#4FB0C6', '#E3B35C', '#7FBF6A'],
  washBlend: 'source-over' }, 'pencilMinimal');

// ── Tiempo (TIEMPOS sale de pelicula.py: todo en segundos locales de cada escena) ──
const escena = n => TIEMPOS.escenas[n - 1];
const limpia = w => w.toLowerCase().replace(/[,.:;¿?¡!…"'()«»]/g, '');
function dicho(E, palabra, k = 1) {
  let vistos = 0;
  for (const w of E.palabras) if (limpia(w.w) === limpia(palabra) && ++vistos === k) return w.t0;
  throw new Error(`escena ${E.n}: la voz no dice '${palabra}' (${k})`);
}
const prog = (tau, t0, d) => clamp((tau - t0) / d, 0, 1);            // 0→1 entre t0 y t0+d
const enDos = tau => Math.floor(tau * 12 + 1e-6) / 12;                 // pose "en dos" (12 dibujos/s)

// ── Fondo ──
let _ret = null;
function fondoNegro(c) {
  resetT(c); c.fillStyle = K.fondo; c.fillRect(0, 0, W, H);
  if (!_ret) {
    _ret = layer(); const g = _ret.getContext('2d'); g.setTransform(S, 0, 0, S, 0, 0);
    g.strokeStyle = K.reticula; g.lineWidth = 2; g.beginPath();
    for (let x = 60; x < W; x += 120) { g.moveTo(x, 0); g.lineTo(x, H); }
    for (let y = 60; y < H; y += 120) { g.moveTo(0, y); g.lineTo(W, y); }
    g.stroke();
  }
  blit(c, _ret);
}

// ── Texto ──
function fuente(tam) { return `${K.peso} ${tam}px ${K.fuente}`; }
// Parte un texto en líneas que caben en `ancho` y devuelve las palabras con su posición.
function maqueta(c, texto, tam, ancho = 960) {
  c.font = fuente(tam); const palabras = texto.split(' '), lineas = [[]]; let w = 0;
  const esp = c.measureText(' ').width;
  for (const p of palabras) { const pw = c.measureText(p).width; if (w + pw > ancho && lineas.at(-1).length) { lineas.push([]); w = 0; } lineas.at(-1).push({ p, pw }); w += pw + esp; }
  return { lineas, esp };
}
// Titulares de la escena: entran palabra por palabra con rebote; la palabra de acento va en naranja.
function titulares(c, E, tau) {
  const T = E.titulares; if (!T.length) return;
  let k = T.length - 1; while (k > 0 && tau < T[k].t) k--;
  const t = T[k], fin = k + 1 < T.length ? T[k + 1].t : E.dur, tam = t.tam || K.titularTam, y0 = t.y || K.titularY;
  const sal = prog(tau, fin - 0.2, 0.2);
  resetT(c); const { lineas, esp } = maqueta(c, t.texto, tam);
  const lead = tam * 0.95, alto = lineas.length * lead; let idx = 0;
  c.save(); c.textBaseline = 'middle';
  lineas.forEach((ln, j) => {
    const total = ln.reduce((a, q) => a + q.pw, 0) + esp * (ln.length - 1); let x = CX - total / 2;
    const y = y0 - alto / 2 + lead * (j + .5);
    for (const q of ln) {
      const e = prog(tau, t.t + idx * 0.09, 0.32), s = e <= 0 ? 0 : easeOutBack(e) * (1 - 0.08 * sal);
      if (s > 0) {
        c.save(); c.translate(x + q.pw / 2, y); c.scale(s, s); c.globalAlpha = Math.min(1, e * 3) * (1 - sal);
        c.font = fuente(tam); c.textAlign = 'center';
        c.fillStyle = t.acento && limpia(q.p) === limpia(t.acento) || (t.acento || '').split(' ').map(limpia).includes(limpia(q.p)) ? K.acento : K.tiza;
        c.fillText(q.p, 0, 0); c.restore();
      }
      x += q.pw + esp; idx++;
    }
  });
  c.restore();
}
// Focos: solo las palabras clave, cuando la voz las dice, con un subrayado que se dibuja a mano.
function focos(c, E, tau) {
  for (const f of E.focos) {
    if (tau < f.t0 || tau > f.t1) continue;
    const e = prog(tau, f.t0, 0.28), sal = prog(tau, f.t1 - 0.2, 0.2), tam = f.tam || K.focoTam, y = f.y || K.focoY;
    resetT(c); c.save(); c.font = fuente(tam); c.textAlign = 'center'; c.textBaseline = 'middle';
    const w = c.measureText(f.texto).width, s = easeOutBack(e);
    c.globalAlpha = Math.min(1, e * 3) * (1 - sal); c.translate(CX, y); c.scale(s, s);
    c.fillStyle = f.color === 'acento' ? K.acento : K.tiza; c.fillText(f.texto, 0, 0); c.restore();
    c.save(); c.globalAlpha = 1 - sal;
    subrayado(c, CX - w / 2, CX + w / 2, y + tam * 0.52, prog(tau, f.t0 + 0.15, 0.35), 11 + f.t0 * 7);
    c.restore();
  }
}
// Rótulo suelto (etiquetas de un diagrama), con entrada pop y salida suave.
function rotulo(c, texto, x, y, tau, t0, { tam = 48, color = K.tiza, t1 = Infinity, align = 'center' } = {}) {
  const e = prog(tau, t0, 0.25); if (e <= 0 || tau > t1) return;
  resetT(c); c.save(); c.font = fuente(tam); c.textAlign = align; c.textBaseline = 'middle';
  c.globalAlpha = Math.min(1, e * 3) * (1 - prog(tau, t1 - 0.2, 0.2)); c.translate(x, y); c.scale(easeOutBack(e), easeOutBack(e));
  c.fillStyle = color === 'acento' ? K.acento : color; c.fillText(texto, 0, 0); c.restore();
}

// brush de la skill fija su propia alfa: aquí respeta también la del contexto, para que los fundidos (globalAlpha) afecten a las líneas.
{ const _brush = brush; brush = (c, pts, o = {}) => _brush(c, pts, { ...o, al: (o.al ?? 1) * c.globalAlpha }); }

// ── Marcas a mano (acento) ──
function subrayado(c, x0, x1, y, p, semilla = 3) {
  if (p <= 0) return; brush(c, [[x0, y + 4], [lerp(x0, x1, .35), y - 2], [lerp(x0, x1, .7), y + 3], [x1, y - 1]], { w: 7, color: K.acento, p, seed: semilla, amp: 2 });
}
function circuloMano(c, x, y, r, p, semilla = 5) {
  if (p <= 0) return; const pts = [];
  for (let k = 0; k <= 30; k++) { const a = -2.2 + k / 30 * TAU * 1.08, rr = r * (1 + .06 * Math.sin(k * 1.7 + semilla)); pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr * .92]); }
  brush(c, pts, { w: 8, color: K.acento, p, seed: semilla, amp: 2.5 });
}
function flecha(c, a, b, p, semilla = 7, color = K.acento) {
  if (p <= 0) return; const m = [lerp(a[0], b[0], .5) + (b[1] - a[1]) * .12, lerp(a[1], b[1], .5) - (b[0] - a[0]) * .12];
  brush(c, [a, m, b], { w: 7, color, p, seed: semilla });
  if (p >= 1) { const ang = Math.atan2(b[1] - m[1], b[0] - m[0]);
    for (const d of [2.6, -2.6]) brush(c, [b, [b[0] + 34 * Math.cos(ang + d), b[1] + 34 * Math.sin(ang + d)]], { w: 7, color, seed: semilla + d }); }
}

// ── Vectores (VectorCraft) para diagramas y cosas de poco movimiento ──
const VECT = {};
function registerVector(nombre, src) {
  const img = new Image(); VECT[nombre] = img;
  _photoLoads.push(new Promise(res => { img.onload = res; img.onerror = () => { console.error('vector ' + nombre); res(); }; }));
  img.src = src;
}
// Lienzo del SVG: 900×900 con el pivote en (450,450). `escala` en %, como en escenas.json.
function vector(c, nombre, x, y, escala = 100, { al = 1, s = 1, rot = 0, revela = 1 } = {}) {
  const img = VECT[nombre]; if (!img) throw new Error('falta el vector ' + nombre); if (al <= 0 || s <= 0) return;
  const k = escala / 100 * s; c.save(); c.globalAlpha *= al; c.translate(x, y); c.rotate(rot); c.scale(k, k);
  if (revela < 1) { c.beginPath(); c.rect(-450, 450 - 900 * revela, 900, 900 * revela); c.clip(); }   // se revela de abajo arriba
  c.drawImage(img, -450, -450, 900, 900); c.restore();
}
// Entrada típica de un vector: pop con rebote + "respiración" leve (nada estático).
function vectorVivo(c, nombre, x, y, escala, tau, t0, { t1 = Infinity, semilla = 1 } = {}) {
  const e = prog(tau, t0, 0.4); if (e <= 0 || tau > t1 + 0.25) return;
  const sal = prog(tau, t1, 0.25), resp = 1 + 0.012 * Math.sin(tau * 2.2 + semilla);
  vector(c, nombre, x, y + 4 * Math.sin(tau * 1.9 + semilla), escala, { s: easeOutBack(e) * resp * (1 - .1 * sal), al: Math.min(1, e * 2) * (1 - sal), rot: 0.008 * Math.sin(tau * .8 + semilla) });
}

// ── Personajes: poses completas (cels) con rellenos y capas de profundidad ──
// raw = {strokes:[{id, points, width, opacity, pressure, close, corner, color, capa}]}
//   capa: 0 = atrás (por defecto), 1, 2… delante. Cada capa pinta sus rellenos y luego sus líneas, así lo de delante tapa.
//   opacity 0 = trazo invisible que solo sirve de contorno para un relleno (p. ej. la silueta).
// rellenos = [{id: trazo cerrado que delimita, color, al}]
const PRESION = [[0, .12], [.15, .85], [.45, 1], [.8, .7], [1, .08]];
function trazo(id, points, width = 6, extra = {}) { return { id, points, width, opacity: 1, pressure: PRESION, ...extra }; }
function pose(raw, rellenos = [], id = 'pose') {
  const capas = [...new Set(raw.strokes.map(s => s.capa || 0))].sort((a, b) => a - b);
  const porId = Object.fromEntries(raw.strokes.map(s => [s.id, s]));
  for (const s of raw.strokes) if (!s.points.every(p => p.length === 2 && p.every(Number.isFinite))) throw new Error(`pose ${id}: trazo '${s.id}' con puntos no válidos`);
  const L = capas.map(cap => ({
    cel: compileCel({ strokes: raw.strokes.filter(s => (s.capa || 0) === cap) }, { id: id + '/' + cap }),
    fills: rellenos.filter(f => { if (!porId[f.id]) throw new Error('relleno sin trazo ' + f.id); return (porId[f.id].capa || 0) === cap; })
      .map(f => ({ ...f, path: curvePath(porId[f.id].points, true) })),
  }));
  return { raw, rellenos, capas: L, id };
}
const _kSprites = new Map();
// Dibuja una pose en (x, y) con escala s. Se cachea como imagen (una por pose, color y escala de salida).
function dibujaPose(c, P, { x = 0, y = 0, s = 1, rot = 0, flip = false, al = 1, material = 'pencil', color = K.tiza, R = 560 } = {}) {
  const key = P.id + '/' + material + '/' + color + '/' + S + '/' + s.toFixed(3) + '/' + R;
  let sp = _kSprites.get(key);
  if (!sp) {
    if (_kSprites.size > 500) _kSprites.clear();
    sp = document.createElement('canvas'); sp.width = sp.height = Math.ceil(2 * R * s * S);
    const g = sp.getContext('2d'); g.setTransform(S * s, 0, 0, S * s, R * s * S, R * s * S);
    for (const L of P.capas) {
      for (const f of L.fills) { g.save(); g.globalAlpha = f.al ?? 1; g.fillStyle = f.color; g.fill(f.path); g.restore(); }
      drawCel(g, L.cel, { material, color });
      if (material === 'pencil') drawCel(g, L.cel, { material: 'ink', color, opacity: .4 });   // núcleo de la línea: legible en pequeño
    }
    _kSprites.set(key, sp);
  }
  if (al <= 0) return;
  c.save(); c.globalAlpha *= al; c.translate(x, y); c.rotate(rot); if (flip) c.scale(-1, 1);
  c.drawImage(sp, -R * s, -R * s, 2 * R * s, 2 * R * s); c.restore();
}
// actuar: elige el dibujo para el instante tau. claves = [[t, 'poseA'], [t2, 'poseB'], ...]
// Mantiene cada pose y pasa a la siguiente con intermedios asistidos (en dos) durante `tr` segundos.
const _kInter = new Map();
function actuar(tau, claves, poses, { tr = 0.25, pasos = 4, facil = easeIO } = {}) {
  const tq = enDos(tau); let k = 0; while (k + 1 < claves.length && tq >= claves[k + 1][0]) k++;
  if (k === 0 && tq < claves[0][0]) return poses[claves[0][1]];
  const a = claves[k][1], sig = claves[k + 1];
  if (!sig) return poses[a];
  const [tb, b] = sig, trr = Math.min(tr, Math.max(.01, tb - claves[k][0])), u = prog(tq, tb - trr, trr);
  if (u <= 0) return poses[a];
  return entre(poses, a, b, Math.round(facil(u) * pasos) / pasos);
}
// entre: intermedio asistido (cacheado) entre dos poses compatibles.
function entre(poses, a, b, u) {
  if (u <= 0) return poses[a]; if (u >= 1) return poses[b];
  const key = a + '>' + b + '@' + u.toFixed(3);
  if (!_kInter.has(key)) { if (_kInter.size > 300) _kInter.clear(); _kInter.set(key, pose(inbetweenCel(poses[a].raw, poses[b].raw, u), poses[a].rellenos, key)); }
  return _kInter.get(key);
}
