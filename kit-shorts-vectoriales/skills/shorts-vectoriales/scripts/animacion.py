"""Arma el short en EffectCraft a partir de escenas.json y lo renderiza.

Uso:
  python3 animacion.py <proyecto>                 # construye el .ecproj y renderiza animacion/animacion.mp4
  python3 animacion.py <proyecto> --sin-render    # solo construye (más rápido para iterar)
  python3 animacion.py <proyecto> --cuadros auto  # además, hoja de cuadros clave en revision/cuadros.png
  python3 animacion.py <proyecto> --cuadros 1.5,12,30

Requiere: voz/tiempos.json (voz.py), subtitulos/palabras.json (alinear.py), ilustraciones/*.svg.
Todo lo que aparece "cuando la voz dice X" se ancla a palabras, así que si cambia la voz basta re-ejecutar.
"""
import json, math, os, subprocess, sys
from comun import Proyecto, cli, correr

if len(sys.argv) < 2:
    sys.exit(__doc__)
p = Proyecto(sys.argv[1])
E = p.estilo
args = sys.argv[2:]
RENDER = "--sin-render" not in args
CUADROS = args[args.index("--cuadros") + 1] if "--cuadros" in args else None
TOTAL, INI = p.total, p.inicios
X0, Y0 = E["ilustracion_pos"]

import vc
vc.ESTILO.update(E)
FONDO_SVG = vc.fondo(p.dir)


def svg(nombre):
    ruta = p.ruta("ilustraciones", nombre + ".svg")
    if not os.path.exists(ruta):
        sys.exit(f"Falta la ilustración {ruta} (créala en dibujar.py)")
    return json.dumps(open(ruta).read())


js = [f"""
var comp=app.project.items.addComp("Short",{E['ancho']},{E['alto']},1,{TOTAL},{E['fps']}); comp.openInViewer();
var ACAB={json.dumps(E['acabado'])}; comp.motionBlur=!!ACAB.desenfoque;
function P(id,path,v){{app.run("prop.set",{{layer:id,path:path,value:v}});}}
function timing(id,a,b){{app.run("layer.timing",{{layers:[id],"in":a,out:b}});}}
function expr(id,path,e){{app.run("prop.setExpression",{{layer:id,path:path,expression:e}});}}
function fadeIO(id,fin,fout,maxOp){{expr(id,"transform/opacity","var a=Math.min(Math.max((time-inPoint)/"+fin+",0),1); var b=Math.min(Math.max((outPoint-time)/"+fout+",0),1); "+(maxOp||100)+"*Math.min(a,b)");}}
function popScale(id,from){{expr(id,"transform/scale","var t=Math.min(Math.max((time-inPoint)/0.35,0),1); var e=1-Math.pow(1-t,3); var s="+from+"+(100-"+from+")*e; [s,s,100]");}}
// ilustración: se 'dibuja' con trim paths, empuja la cámara (escala) y entra/sale con fundido
// modo: add (luz), multiply (tinta), screen…; entrada "pop": crece con rebote; fx/fy: desliza desde ahí
// vida (para que nada quede estático): onda = ondulación de las líneas (Wiggle Paths, px),
// deriva = vaivén lento de posición (px), temblor = vibración rápida (px), pulsos = [s,…] golpes de escala
// ritmo (sincronizado al tempo de la música, que empieza en t=0): {{bpm, cada, desfase, tap: grados de golpe por pulso,
// rebote: % de escala por pulso, vaiven: grados de balanceo (péndulo, 2 pulsos por ida y vuelta),
// vuelta: pulsos por giro completo (manecilla), destello: opacidad mínima entre pulsos (0–1)}}
// partes (rig): [{{svg, pivote:[x,y] en el lienzo del dibujo, detras, balanceo:°, periodo:s, sacudida:°, cada:s,
// parpadeo:s entre parpadeos, retraso:s, fase}}] → capas hijas que giran sobre su pivote y heredan posición/escala del padre
function svgLayer(name,svg,a,b,x,y,sc,draw,push,rot,maxOp,modo,entrada,fx,fy,mov,onda,deriva,temblor,pulsos,tw0,tw1,semilla,ritmo,partes){{
  partes=partes||[]; var hijos=[];
  for(var j=0;j<partes.length;j++) if(partes[j].detras) hijos.push(parteLayer(name,partes[j],a,b,draw,maxOp,j));
  var id=app.run("edit.pasteSvg",{{svg:svg,name:name}}).layer;
  for(var j=0;j<partes.length;j++) if(!partes[j].detras) hijos.push(parteLayer(name,partes[j],a,b,draw,maxOp,j));
  timing(id,a,b);
  app.run("prop.set",{{layer:id,path:"transform/position",value:[x,y,0]}});
  var seed=semilla>=0 ? semilla : Math.floor(Math.random()*1000);   // misma semilla = capas que se mueven juntas
  var base = fx!==null ? "var t=Math.min(Math.max((time-inPoint)/"+mov+",0),1); var e=1-Math.pow(1-t,3); var b=["+fx+"+("+x+"-"+fx+")*e,"+fy+"+("+y+"-"+fy+")*e,0];" : "var b=value;";
  // wiggle() devuelve value + ruido: se resta value para sumar solo el ruido a la posición base
  var mueve = "+[0,"+(deriva>0?4:0)+"*Math.sin(time*1.9+"+seed+"),0]" + (deriva>0 ? "+(wiggle(0.6,"+deriva+")-value)" : "") + (temblor>0 ? "+(time>"+tw0+"&&time<"+tw1+" ? wiggle(9,"+temblor+")-value : [0,0,0])" : "");
  expr(id,"transform/position","seedRandom("+seed+",true); "+base+" b"+mueve);
  if(onda>0){{ var w=app.run("layer.addShapeItem",{{layer:id,kind:"wiggle"}});
    app.run("prop.set",{{layer:id,path:"contents/wiggle/size",value:onda}});
    app.run("prop.set",{{layer:id,path:"contents/wiggle/detail",value:4}});
    app.run("prop.set",{{layer:id,path:"contents/wiggle/speed",value:1.3}});
    app.run("prop.set",{{layer:id,path:"contents/wiggle/seed",value:seed}}); }}
  if(draw>0){{ app.run("layer.addShapeItem",{{layer:id,kind:"trim"}});
    expr(id,"contents/trim/end","var t=Math.min(Math.max((time-inPoint)/"+draw+",0),1); 100*(1-Math.pow(1-t,3))"); }}
  // entrada por defecto "asentar": crece 86→~102→100 % (back-out) y se endereza de −4°; salida con ease-in a 90 %
  var pop = entrada=="pop" ? "var q=Math.min(Math.max((time-inPoint)/0.45,0),1)-1; var k=1+2.7*q*q*q+1.7*q*q;"
          : entrada=="ninguna" ? "var k=1;"
          : "var q=Math.min(Math.max((time-inPoint)/0.55,0),1)-1; var k=0.86+0.14*(1+2.7*q*q*q+1.7*q*q);";
  pop += " var o=Math.min(Math.max((outPoint-time)/0.25,0),1); k*=0.9+0.1*(1-Math.pow(1-o,2));";
  var asienta = entrada=="ninguna" ? "" : "var qa=Math.min(Math.max((time-inPoint)/0.55,0),1)-1; ";
  var asientaR = entrada=="ninguna" ? "0" : "4*(2.7*qa*qa*qa+1.7*qa*qa)";
  var pul = "var P=["+pulsos.join(",")+"]; var u=0; for(var i=0;i<P.length;i++){{ var d=time-P[i]; if(d>-0.1&&d<0.5) u+=0.045*Math.exp(-Math.pow((d-0.08)/0.1,2)); }}";
  var rz="", rfr="", rterm="0", rd="";
  if(ritmo){{ var B=60/ritmo.bpm, cada=ritmo.cada||1, des=ritmo.desfase||0;
    rfr="var ph=time/("+B+"*"+cada+")-"+des+"; var f=ph-Math.floor(ph); ";
    if(ritmo.rebote) rz=rfr+"var rb=1+"+(ritmo.rebote/100)+"*Math.exp(-f*6); ";
    var g=[];
    if(ritmo.tap) g.push(ritmo.tap+"*Math.exp(-f*5)*Math.min(f*25,1)");
    if(ritmo.vaiven) g.push(ritmo.vaiven+"*Math.sin(Math.PI*(time/"+B+"-"+des+"))");
    if(ritmo.vuelta) g.push("360*(time/"+B+"-"+des+")/"+ritmo.vuelta);
    if(g.length) rterm=g.join("+");
    if(ritmo.destello!==undefined) rd=rfr+"var dl="+ritmo.destello+"+(1-"+ritmo.destello+")*Math.exp(-f*5); ";
  }}
  expr(id,"transform/scale",pop+pul+rz+" var p=(time-inPoint)/(outPoint-inPoint); var s="+sc+"*(1+"+push+"*p)*k*(1+u)"+(rz?"*rb":"")+"; var br=0.012*Math.sin(time*2.2+"+seed+"); [s*(1+br),s*(1-br),100]");
  expr(id,"transform/rotation",(rterm!="0"?rfr:"")+asienta+"(time-inPoint)*"+rot+"+0.5*Math.sin(time*0.8+"+seed+")+("+rterm+")+("+asientaR+")");
  if(modo) comp.layer(name).blendingMode=BlendingMode[modo.toUpperCase()];
  if(ACAB.desenfoque) app.run("layer.setSwitch",{{layers:[id],switch:"motionBlur",value:true}});
  // sombra suave hacia abajo-izquierda (luz arriba a la derecha): el dibujo "se apoya" en el papel
  if(ACAB.sombra>0 && !modo){{ app.run("effect.apply",{{layer:id,effect:"Drop Shadow"}});
    P(id,"effects/#1/color",ACAB.sombra_color); P(id,"effects/#1/opacity",ACAB.sombra);
    P(id,"effects/#1/distance",9); P(id,"effects/#1/softness",14); P(id,"effects/#1/direction",150); }}
  fadeIO(id,0.15,0.2,maxOp);
  for(var j=0;j<hijos.length;j++){{ var pv=partes[hijos[j].k].pivote;
    app.run("layer.setParent",{{layers:[hijos[j].id],parent:id,compensate:false}});
    P(hijos[j].id,"transform/anchor",[pv[0],pv[1],0]); P(hijos[j].id,"transform/position",[pv[0],pv[1],0]); }}
  if(rd) expr(id,"transform/opacity",rd+" var a=Math.min(Math.max((time-inPoint)/0.15,0),1); var b=Math.min(Math.max((outPoint-time)/0.2,0),1); "+(maxOp||100)+"*Math.min(a,b)*dl");
  return id;
}}
function parteLayer(padre,pt,a,b,draw,maxOp,j){{
  var id=app.run("edit.pasteSvg",{{svg:pt.svgData,name:padre+"_"+pt.svg}}).layer; timing(id,a,b);
  var ret=pt.retraso!==undefined?pt.retraso:0.15+0.08*j, fase=j*1.3+(pt.fase||0);
  if(draw>0){{ app.run("layer.addShapeItem",{{layer:id,kind:"trim"}});
    expr(id,"contents/trim/end","var t=Math.min(Math.max((time-inPoint-"+ret+")/"+draw+",0),1); 100*(1-Math.pow(1-t,3))"); }}
  // entra creciendo desde su pivote con rebote, después del cuerpo (acción retardada)
  expr(id,"transform/scale","var q=Math.min(Math.max((time-inPoint-"+ret+")/0.4,0),1)-1; var s=100*(1+2.7*q*q*q+1.7*q*q); [s,s,100]");
  var r=[];
  if(pt.balanceo) r.push(pt.balanceo+"*Math.sin(2*Math.PI*time/"+(pt.periodo||1.8)+"+"+fase+")");
  if(pt.sacudida) r.push(pt.sacudida+"*Math.exp(-((time-inPoint+"+fase+")%"+(pt.cada||2.6)+")*5)*Math.sin(((time-inPoint+"+fase+")%"+(pt.cada||2.6)+")*22)");
  if(r.length) expr(id,"transform/rotation",r.join("+"));
  if(pt.parpadeo) expr(id,"transform/opacity","var f=(time-inPoint+"+fase+")%"+pt.parpadeo+"; var a=Math.min(Math.max((outPoint-time)/0.2,0),1); (time-inPoint>1.0 && f<0.14 ? 100 : 0)*a");
  else fadeIO(id,0.15,0.2,maxOp);
  if(ACAB.sombra>0 && !pt.parpadeo){{ app.run("effect.apply",{{layer:id,effect:"Drop Shadow"}});
    P(id,"effects/#1/color",ACAB.sombra_color); P(id,"effects/#1/opacity",ACAB.sombra);
    P(id,"effects/#1/distance",9); P(id,"effects/#1/softness",14); P(id,"effects/#1/direction",150); }}
  return {{id:id,k:j}};
}}
// titular que entra palabra por palabra con rebote (preset bounceInWords re-anclado a la entrada de la capa)
function palabrasEnRebote(id,txt){{
  app.run("layer.applyTextPreset",{{layer:id,preset:"bounceInWords"}});
  var n=txt.split(" ").length, d=Math.min(0.25+0.12*n,1.0);
  expr(id,"text/animators/animator/selectors/rangeSelector/offset","var t=Math.min(Math.max((time-inPoint)/"+d+",0),1); -100+200*t");
  expr(id,"text/animators/animator#2/selectors/rangeSelector/offset","var t=Math.min(Math.max((time-inPoint-0.1)/"+(d+0.15)+",0),1); -35+135*t");
}}
// tarjeta de cita: recuadro blanco con barra de color, nombre y lugar/año en monoespaciada
function tarjeta(t1,t2,a,b,x,y,col){{
  var w=Math.max(360,Math.max(t1.length,t2.length)*19+70), h=t2?118:76;
  var svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+w+'" height="'+h+'"><rect x="0" y="0" width="'+w+'" height="'+h+'" rx="6" fill="#F4F2EC"/><rect x="0" y="0" width="12" height="'+h+'" fill="'+col+'"/></svg>';
  var r=app.run("edit.pasteSvg",{{svg:svg,name:"tarjeta_"+a}}).layer; timing(r,a,b);
  app.run("prop.set",{{layer:r,path:"transform/position",value:[x,y,0]}}); fadeIO(r,0.2,0.2);
  var t=app.run("layer.newText",{{text:t1,box:[x-w/2+34,y-h/2+14,w-44,46],font:"Menlo",style:"Bold",size:30,fill:"#111111",justify:"left"}}).layer;
  timing(t,a,b); fadeIO(t,0.25,0.2);
  if(t2){{ var u=app.run("layer.newText",{{text:t2,box:[x-w/2+34,y-h/2+62,w-44,40],font:"Menlo",style:"Regular",size:24,fill:"#555555",justify:"left"}}).layer;
    timing(u,a,b); fadeIO(u,0.3,0.2); }}
}}
// texto: caja centrada (la posición por defecto de un texto de párrafo es el centro de su caja)
function text(txt,accent,a,b,x,cy,size,color,boxH,pop,acol,porPalabra){{
  var h=boxH||Math.round(size*3.3);
  var id=app.run("layer.newText",{{text:txt,box:[60,cy-h/2,960,h],font:"{E['fuente']}",style:"{E['estilo_fuente']}",size:size,fill:color,justify:"center",leading:Math.round(size*0.95)}}).layer;
  if(accent){{ var i=txt.indexOf(accent); if(i>=0) app.run("layer.setText",{{layer:id,range:[i,i+accent.length],fill:acol||"{E['acento']}"}}); }}
  app.run("prop.set",{{layer:id,path:"transform/position",value:[x,cy,0]}});
  timing(id,a,b);
  if(porPalabra) {{ palabrasEnRebote(id,txt); fadeIO(id,0.05,0.2); }} else {{ popScale(id,pop||82); fadeIO(id,0.2,0.2); }}
  return id;
}}
// sobre fondo claro: texto oscuro con contorno del color del fondo
function sub(txt,i0,i1,a,b,first,fill,stroke){{
  var id=app.run("layer.newText",{{text:txt,box:[40,{E['subtitulo_y']}-60,1000,120],font:"{E['fuente']}",style:"{E['estilo_fuente']}",size:{E['subtitulo_tam']},fill:fill||"{E['blanco']}",
    stroke:stroke||"{E['fondo']}",applyStroke:true,strokeWidth:12,strokeOverFill:false,justify:"center"}}).layer;
  app.run("layer.setText",{{layer:id,range:[i0,i1],fill:"{E['acento']}"}});
  timing(id,a,b); if(first) popScale(id,90);
}}
app.run("layer.newSolid",{{name:"Fondo",color:"{E['fondo']}"}});
var grid=app.run("edit.pasteSvg",{{svg:{svg(FONDO_SVG)},name:"Fondo dibujo"}}).layer;
app.run("prop.set",{{layer:grid,path:"transform/position",value:[{E['ancho'] // 2},{E['alto'] // 2},0]}});
"""]
add = js.append
r3 = lambda v: round(v, 3)


# ── "Nada estático": eventos visibles por escena y pulsos automáticos en los huecos ──
VIDA = {"onda": 2.5, "deriva": 3, "temblor": 0, **p.spec.get("vida", {})}
MAX_QUIETO = p.spec.get("max_quieto", 3.0)   # segundos máximos sin un cambio nuevo en pantalla
PULSOS_TOTALES, INFORME = [], []


def eventos_escena(n, esc, a):
    ev = [a]
    for grupo in ("capas", "titulares", "textos", "tarjetas"):
        for el in esc.get(grupo, []):
            ev.append(p.instante(n, el.get("desde")))
            if el.get("hasta") is not None:
                ev.append(p.instante(n, el["hasta"]))
            ev += [p.instante(n, q) for q in el.get("pulsos", [])]
    an = esc.get("anillo")
    if an:
        cuenta = {}
        for pal in an.get("palabras", []):
            cuenta[pal] = cuenta.get(pal, 0) + 1
            ev.append(p.dicho(n, pal, cuenta[pal] + an.get("saltar", {}).get(pal, 0)))
    return sorted(ev)


def pulsos_auto(n, a, b, ev):
    """En cada hueco > MAX_QUIETO s, pulsos cada ~2.2 s en el inicio de palabras largas (las que se acentúan)."""
    largas = [w["inicio"] for w in p.palabras if w["escena"] == n and len(w["palabra"].strip(",.:;¿?¡!…")) >= 6]
    puntos, out = sorted(set(ev + [b])), []
    for t0, t1 in zip(puntos, puntos[1:]):
        if t1 - t0 <= MAX_QUIETO:
            continue
        objetivo = t0 + 2.2
        while objetivo < t1 - 0.8:
            cerca = min(largas, key=lambda t: abs(t - objetivo), default=None)
            elegido = cerca if cerca is not None and abs(cerca - objetivo) < 0.9 and t0 + 1.0 < cerca < t1 - 0.5 else objetivo
            out.append(elegido); objetivo = elegido + 2.2
    cambios = sorted(set(puntos + out))
    INFORME.append((n, max(t1 - t0 for t0, t1 in zip(cambios, cambios[1:])), len(out)))
    return out


# rigs: partes animadas por dibujo ("rigs": {"burro": [{...}]} en escenas.json); una capa puede traer sus "partes"
RIGS = p.spec.get("rigs", {})
TIT_PALABRAS = p.spec.get("titulares_por_palabra", True)

def partes_js(c):
    partes = c.get("partes", RIGS.get(c["svg"], []))
    return "[" + ",".join(json.dumps(pt)[:-1] + f',"svgData":{svg(pt["svg"])}}}' for pt in partes) + "]"


def luminancia(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

for n, esc in enumerate(p.escenas, 1):
    a, b = INI[n - 1], p.fin_escena(n)
    fondo = esc.get("fondo")
    clara = bool(fondo) and luminancia(p.color(fondo)) > 0.6   # fondo claro → textos oscuros
    TXT, GRIS = ("#111111", "#444444") if clara else (E["blanco"], E["gris"])
    if fondo:
        add(f'var f{n}=app.run("layer.newSolid",{{name:"Fondo_{n}",color:"{p.color(fondo)}"}}).layer; timing(f{n},{r3(a)},{r3(b)});')
    fin = lambda el: r3(p.instante(n, el["hasta"])) if el.get("hasta") is not None else r3(b)
    pulsos = pulsos_auto(n, a, b, eventos_escena(n, esc, a))
    PULSOS_TOTALES.extend(pulsos)
    for k, c in enumerate(esc.get("capas", [])):
        x, y = c.get("pos", [X0, Y0])
        fx, fy = c.get("desde_pos", ["null", "null"])
        vida = {**VIDA, **{k2: c[k2] for k2 in VIDA if k2 in c}}
        tw = [r3(p.instante(n, q)) for q in c["temblor_en"]] if c.get("temblor_en") else [-1, 1e9]  # ventana del temblor
        add(f'svgLayer({json.dumps(c["svg"] + f"_{n}_{k}")},{svg(c["svg"])},{r3(p.instante(n, c.get("desde")))},{fin(c)},'
            f'{x},{y},{c.get("escala", 100)},{c.get("dibujo", 1.2)},{c.get("empuje", 0.05)},{c.get("rotacion", 0)},{c.get("opacidad", 100)},'
            f'{json.dumps(c.get("modo", ""))},{json.dumps(c.get("entrada", ""))},{fx},{fy},{c.get("mov", 0.8)},'
            f'{vida["onda"]},{vida["deriva"]},{vida["temblor"]},{json.dumps([r3(t) for t in pulsos + [p.instante(n, q) for q in c.get("pulsos", [])]])},'
            f'{tw[0]},{tw[1]},{c.get("semilla", -1)},{json.dumps(c.get("ritmo")) if c.get("ritmo") else "null"},{partes_js(c)});')
    for t in esc.get("tarjetas", []):
        x, y = t.get("pos", [540, 560])
        add(f'tarjeta({json.dumps(t["titulo"])},{json.dumps(t.get("sub", ""))},{r3(p.instante(n, t.get("desde")))},{fin(t)},{x},{y},"{p.color(t.get("color", "acento"))}");')
    tits = esc.get("titulares", [])
    for k, t in enumerate(tits):
        ta = p.instante(n, t.get("desde"))
        tb = p.instante(n, tits[k + 1]["desde"]) if k + 1 < len(tits) else b
        add(f'text({json.dumps(t["texto"])},{json.dumps(t.get("acento", ""))},{r3(ta)},{r3(tb)},540,'
            f'{t.get("y", E["titular_y"])},{t.get("tam", E["titular_tam"])},"{TXT}",0,0,"{p.color(t.get("color_acento", "acento"))}",{str(TIT_PALABRAS).lower()});')
    for t in esc.get("textos", []):
        col = {"gris": GRIS, "blanco": TXT}.get(t.get("color", "gris"), p.color(t.get("color", "gris")))
        add(f'text({json.dumps(t["texto"])},{json.dumps(t.get("acento", ""))},{r3(p.instante(n, t.get("desde")))},{fin(t)},'
            f'{t.get("x", 540)},{t.get("y", 1680)},{t.get("tam", 54)},"{col}",{round(t.get("tam", 54) * 1.5)},0,"{p.color(t.get("color_acento", "acento"))}");')
    if "anillo" in esc:  # números alrededor de un círculo, que se encienden al decirse
        an = esc["anillo"]; cx, cy = an.get("centro", [X0, Y0]); R = an.get("radio", 340)
        if an.get("centro_texto"):
            add(f'text({json.dumps(an["centro_texto"])},"",{r3(a + 0.3)},{r3(b)},{cx},{cy},{an.get("centro_tam", 190)},"{E["acento"]}",{round(an.get("centro_tam", 190) * 1.2)});')
        vals = an["valores"]; pals = an.get("palabras", [None] * len(vals)); cuenta = {}
        for k, (v, pal) in enumerate(zip(vals, pals)):
            if pal:
                cuenta[pal] = cuenta.get(pal, 0) + 1
                t0 = p.dicho(n, pal, cuenta[pal] + an.get("saltar", {}).get(pal, 0))
            else:
                t0 = a + 1.0 + k * 0.5
            ang = math.radians(k * 360 / len(vals))
            add(f'text({json.dumps(str(v))},"",{r3(t0)},{r3(b)},{round(cx + R * math.sin(ang))},{round(cy - R * math.cos(ang))},'
                f'{an.get("tam", 62)},"{E["blanco"]}",{round(an.get("tam", 62) * 1.45)});')

# ── acabado: grano de papel animado y viñeta, por encima de los dibujos y debajo de los subtítulos ──
if E["acabado"].get("grano"):
    add(f'''var gr=app.run("layer.newSolid",{{name:"Grano",color:"#808080"}}).layer; app.run("effect.apply",{{layer:gr,effect:"Fractal Noise"}});
P(gr,"effects/#1/transform/scale",6); P(gr,"effects/#1/contrast",140); P(gr,"effects/#1/complexity",3);
expr(gr,"effects/#1/evolution","Math.floor(time*8)*47"); comp.layer("Grano").blendingMode=BlendingMode.OVERLAY; P(gr,"transform/opacity",{E["acabado"]["grano"]});''')
if E["acabado"].get("vineta"):
    add(f'''var vg=app.run("layer.newSolid",{{name:"Vineta",color:"#FFFFFF"}}).layer; app.run("effect.apply",{{layer:vg,effect:"CC Vignette"}});
P(vg,"effects/#1/amount",{E["acabado"]["vineta"]}); comp.layer("Vineta").blendingMode=BlendingMode.MULTIPLY;''')

# ── subtítulos palabra por palabra: grupos de ≤3 palabras, la activa en acento ──
if p.spec.get("subtitulos", True):
    pal = p.palabras
    limpia = lambda w: w.replace("…", "").rstrip(",.:;").upper()
    grupos, actual = [], []
    for i, w in enumerate(pal):
        actual.append(w)
        sig = pal[i + 1] if i + 1 < len(pal) else None
        if len(actual) == 3 or w["palabra"].endswith((",", ".", "…", "?", ":", ";", "!")) or sig is None or sig["escena"] != w["escena"]:
            grupos.append(actual); actual = []
    for gi, g in enumerate(grupos):
        textos = [limpia(w["palabra"]) for w in g]
        linea = " ".join(textos)
        sig_ini = max(grupos[gi + 1][0]["inicio"] - 0.05, 0) if gi + 1 < len(grupos) else TOTAL
        fin = min(g[-1]["fin"] + 0.35, sig_ini)
        pos = 0
        for k, w in enumerate(g):
            ta = w["inicio"] if k else max(w["inicio"] - 0.05, 0)
            tb = g[k + 1]["inicio"] if k + 1 < len(g) else fin
            fondo = p.escenas[w["escena"] - 1].get("fondo")
            colores = f',"#111111","{p.color(fondo)}"' if fondo and luminancia(p.color(fondo)) > 0.6 else ""
            add(f'sub({json.dumps(linea)},{pos},{pos + len(textos[k])},{r3(ta)},{r3(tb)},{str(k == 0).lower()}{colores});')
            pos += len(textos[k]) + 1

proj = p.ruta("animacion", "proyecto.ecproj")
add(f'app.run("file.saveAs",{{path:{json.dumps(proj)}}}); writeLn("ok "+comp.duration);')
jsx = p.ruta("animacion", "construir.jsx")
open(jsx, "w").write("\n".join(js))
EC = cli("effectcraft")
correr([EC, "script", jsx])
print(f"EffectCraft: {proj} ({TOTAL} s, {len(p.escenas)} escenas)")
print(f"vida: onda {VIDA['onda']} px, deriva {VIDA['deriva']} px; {len(PULSOS_TOTALES)} pulsos automáticos")
# elementos que se verían muy poco tiempo (anclados a las últimas palabras de la escena)
breves = []
for n, esc in enumerate(p.escenas, 1):
    b_esc = p.fin_escena(n)
    for grupo in ("capas", "textos", "tarjetas"):
        for el in esc.get(grupo, []):
            t0 = p.instante(n, el.get("desde"))
            t1 = p.instante(n, el["hasta"]) if el.get("hasta") is not None else b_esc
            if t1 - t0 < 1.2:
                breves.append(f"esc {n} {grupo[:-1]} '{el.get('texto') or el.get('titulo') or el.get('svg')}' {t1 - t0:.1f}s")
if breves:
    print("⚠ visibles menos de 1.2 s (ánclalos antes):", "; ".join(breves))
peores = sorted(INFORME, key=lambda r: -r[1])[:4]
print("máximo sin cambio nuevo:", ", ".join(f"esc {n}: {m:.1f}s" for n, m, _ in peores),
      "(además de la micro-animación continua)")

if RENDER:
    out = p.ruta("animacion", "animacion.mp4")
    correr([EC, "render", "--project", proj, "--comp", "Short", "--out", out, "--format", "h264",
            "--quality", "best", "--audio", "off"])
    print("render:", out)

if CUADROS:
    ts = ([round(INI[i] + (p.fin_escena(i + 1) - INI[i]) * 0.7, 2) for i in range(len(p.escenas))]
          if CUADROS == "auto" else [float(t) for t in CUADROS.split(",")])
    tmp = p.ruta("revision", "cuadros", "x")[:-2]
    pc = [cli("photocraft"), "run", "--new", json.dumps({"width": 360 * min(4, len(ts)), "height": 640 * ((len(ts) + 3) // 4)}),
          "--cmd", "layer.newFillLayer.solidColor", "--params", json.dumps({"color": "#333333"})]
    for i, t in enumerate(ts):
        f = os.path.join(tmp, f"c{i:02d}.png")
        correr([EC, "render-frame", "--project", proj, "--comp", "Short", "--time", str(t), "--max-side", "636", "--out", f])
        pc += ["--cmd", "file.placeEmbedded", "--params", json.dumps({"path": f, "scale": 100, "center": [180 + (i % 4) * 360, 320 + (i // 4) * 640]})]
    hoja = p.ruta("revision", "cuadros.png")
    correr(pc + ["--out", hoja])
    print("cuadros clave:", hoja, ts)
