#!/usr/bin/env python3
"""Genera la Vitrina de Monedas y Billetes de Colección (index.html + README.md) en /workspace/monedas-billetes
desde inventario.json. Las fotos se copian a img/ BYTE A BYTE (sin recomprimir, recortar ni rotar)."""
import json, os, re, shutil, filecmp
BASE = '/workspace/monedas-billetes'; OUT = BASE
SLUG = 'vitrina-monedas-billetes'; URL = f'https://dacam32-del.github.io/{SLUG}/'
inv = json.load(open(f'{BASE}/inventario.json', encoding='utf-8'))
os.makedirs(f'{OUT}/img', exist_ok=True)

GRADOS = [  # orden de menor a mayor conservación
 ('G', 'G / Muy Circulado'), ('VG', 'VG / Regular'), ('F', 'F / Bueno'), ('VF', 'VF / Muy Bueno'),
 ('XF', 'XF / Muy Bueno+'), ('AU', 'AU / Casi Sin Circular'), ('UNC', 'UNC / Sin Circular'), ('PROOF', 'Proof / Flor de Cuño')]
GL = dict(GRADOS)
ALIAS = {'EF': 'XF', 'MS': 'UNC', 'SC': 'UNC', 'BU': 'UNC', 'PRF': 'PROOF', 'PF': 'PROOF', 'FDC': 'PROOF'}
def grado(s):
    if isinstance(s, dict): s = s.get('grado') or s.get('escala') or ''
    c = re.split(r'[\s/(·,-]', str(s or '').strip().upper())[0]
    c = ALIAS.get(c, c)
    return c if c in GL else ''
def rng(s):
    if isinstance(s, (int, float)): return (int(s), int(s))
    n = [int(x.replace('.', '')) for x in re.findall(r'\d[\d.]*', str(s or '')) if x.replace('.', '').isdigit()]
    return (min(n), max(n)) if n else (0, 0)
def fmt(n): return f"{n:,}".replace(',', '.')
def year(p):
    y = re.findall(r'\b(1[0-9]\d\d|20[0-3]\d)\b', str(p.get('anio', '')))
    return int(y[0]) if y else 0
def epoca(y):
    if not y: return 'Sin confirmar'
    if y < 1900: return 'Anterior a 1900'
    if y < 1950: return '1900–1949'
    if y < 1970: return '1950–1969'
    if y < 2000: return f'{str(y)[:3]}0–{str(y)[:3]}9'
    return '2000 en adelante'

items = []; tmin = tmax = uds = 0
for p in inv:
    imgs = []
    for i, f in enumerate(p.get('fotos', [])):
        src = f if os.path.isabs(f) else f'{BASE}/{f}'
        if not os.path.exists(src): continue
        ext = os.path.splitext(src)[1].lower() or '.jpg'
        name = f"{p['id']}{ext}" if i == 0 else f"{p['id']}-{i+1}{ext}"
        dst = f'{OUT}/img/{name}'
        if os.path.abspath(src) != os.path.abspath(dst) and not (os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)):
            shutil.copyfile(src, dst)  # copia íntegra, byte a byte
        imgs.append('img/' + name)
    a, b = rng(p.get('venta_chile_clp')); k = int(p.get('stock', 1) or 1)
    tmin += a * k; tmax += b * k; uds += k
    y = year(p); g = grado(p.get('estado'))
    tabla = []
    for code, lab in GRADOS:
        v = (p.get('precios_por_estado') or {}).get(code)
        if v in (None, ''): continue
        x1, x2 = rng(v); tabla.append(dict(c=code, l=lab, a=x1, b=x2))
    q = {kk: v for kk, v in p.items() if kk != 'fotos'}
    q.update(imgs=imgs, pmin=a, pmax=b, y=y, ep=p.get('epoca') or epoca(y), g=g, gl=GL.get(g, str(p.get('estado') or '')), tabla=tabla,
             orig=p.get('origen_estimacion') or 'Chile / Nacional')
    items.append(q)
total = f"${fmt(tmin)} – ${fmt(tmax)}"
data = json.dumps(items, ensure_ascii=False).replace('</', '<\\/')
WA = "https://wa.me/56956592453?text=Hola!%20Vi%20tu%20vitrina%20de%20monedas%20y%20billetes%20de%20colecci%C3%B3n%20y%20quiero%20consultar"
GJS = json.dumps(GRADOS, ensure_ascii=False)

H = r'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tesoro Numismático · Monedas y Billetes de Colección de Todos los Países</title>
<meta name="description" content="Vitrina de monedas y billetes de colección de todos los países: país, época, año, estado de conservación y precio estimado en CLP según estado.">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Cormorant+Garamond:ital,wght@0,500;0,700;1,500&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a1512;--paper:#10221c;--paper2:#16302714;--ink:#f3ead2;--gold:#d9b45a;--gold2:#f5d98b;--cop:#b87333;--mut:#b9b08f;--line:#2c4a3e}
*{box-sizing:border-box}body{margin:0;color:var(--ink);font-family:'Cormorant Garamond',serif;font-size:17px;background:var(--bg) radial-gradient(ellipse at top,#1d3a30 0,#0a1512 65%)}
header{text-align:center;padding:30px 16px 34px;border-bottom:3px double var(--gold);background:repeating-radial-gradient(circle at 50% -40%,rgba(217,180,90,.07) 0 2px,transparent 2px 14px),linear-gradient(#0f2a22,#0a1512)}
.coin{width:84px;height:84px;margin:0 auto 10px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff3c4,#d9b45a 45%,#8a6a24 80%);box-shadow:0 0 0 4px #8a6a24,0 0 0 7px #d9b45a,0 8px 24px rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;font-family:Cinzel;font-weight:700;font-size:30px;color:#5a4210;animation:spin 9s ease-in-out infinite}
@keyframes spin{0%,70%,100%{transform:rotateY(0)}85%{transform:rotateY(180deg)}}
h1{font-family:Cinzel;font-weight:700;color:var(--gold2);font-size:2.3em;margin:0;letter-spacing:2px;text-shadow:0 2px 12px rgba(217,180,90,.35)}
header p{margin:8px auto 0;font-style:italic;color:#e8dcb6;max-width:760px}
.wa{display:inline-flex;gap:6px;align-items:center;margin-top:14px;background:#25d366;color:#fff;text-decoration:none;padding:8px 16px;border-radius:22px;font-family:Inter;font-weight:600;font-size:.85em}
.stats{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:18px}.stat{border:1px solid var(--gold);padding:8px 18px;border-radius:10px;background:rgba(0,0,0,.35)}
.stat b{display:block;font-family:Cinzel;font-size:1.35em;color:var(--gold2)}.stat span{font-family:Inter;font-size:.68em;text-transform:uppercase;letter-spacing:1px;color:var(--mut)}
.filters{max-width:1240px;margin:22px auto;padding:16px;background:var(--paper);border:1px solid var(--line);border-radius:12px;display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:10px}
.filters label{font-family:Inter;font-size:.68em;text-transform:uppercase;letter-spacing:1px;color:var(--gold)}
select,input{width:100%;padding:7px;border:1px solid var(--line);background:#0c1a15;color:var(--ink);font-family:Inter;font-size:.85em;border-radius:6px}
.reset{align-self:end;padding:8px;border:1px solid var(--gold);background:transparent;color:var(--gold);border-radius:6px;font-family:Inter;cursor:pointer}
#count{max-width:1240px;margin:0 auto;padding:0 16px;color:var(--mut);font-style:italic}
.grid{max-width:1240px;margin:10px auto 30px;padding:0 16px;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:22px}
.card{background:linear-gradient(180deg,#132a22,#0e1f19);border:1px solid var(--line);border-radius:12px;overflow:hidden;cursor:pointer;transition:transform .15s,border-color .15s;box-shadow:0 6px 18px rgba(0,0,0,.45);padding-bottom:30px}
.card:hover{transform:translateY(-4px);border-color:var(--gold)}.card img{width:100%;aspect-ratio:4/3;object-fit:contain;display:block;background:#07100d}
.noimg{aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;background:#07100d;font-size:3em}
.cb{padding:12px}.cb .t{font-family:Cinzel;font-weight:700;font-size:1.02em;color:var(--gold2)}.cb .a{color:var(--mut);font-size:.92em;font-style:italic;margin:3px 0 8px}
.tag{display:inline-block;font-family:Inter;font-size:.66em;padding:2px 8px;border-radius:10px;background:#1f3d33;color:#e9d9a6;margin:0 3px 3px 0}.tag.f{background:var(--gold);color:#2a1f05}.tag.i{background:#3a2a4a;color:#e6d4ff}.tag.n{background:#173a5a;color:#d4ecff}
.price{margin-top:8px;color:var(--gold2);font-weight:700;font-family:Inter;font-size:.9em}
.mini{width:100%;margin-top:8px;border-collapse:collapse;font-family:Inter;font-size:.68em}.mini td{padding:2px 4px;border-bottom:1px dotted var(--line)}.mini tr.on td{color:#2a1f05;background:var(--gold);font-weight:600}
.empty{grid-column:1/-1;text-align:center;padding:60px 20px;font-family:Cinzel;font-size:1.45em;color:var(--gold2)}.empty small{display:block;font-family:'Cormorant Garamond';font-style:italic;color:var(--mut);font-size:.7em;margin-top:10px}
.modal{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;padding:16px;z-index:9}.modal.on{display:flex}
.box{background:var(--paper);max-width:940px;width:100%;max-height:92vh;overflow:auto;border-radius:12px;border-top:6px solid var(--gold);padding:22px;position:relative}
.box h2{font-family:Cinzel;margin:0 0 4px;color:var(--gold2)}.box h3{font-family:Cinzel;color:var(--gold);font-size:1em;margin:18px 0 6px}.x{position:absolute;right:14px;top:8px;font-size:1.8em;cursor:pointer;color:var(--gold)}
.ph{display:flex;gap:8px;overflow-x:auto;margin:12px 0}.ph img{height:280px;border-radius:6px;border:1px solid var(--line)}
table.d{width:100%;border-collapse:collapse;font-size:.95em}table.d td{padding:6px;border-bottom:1px dotted var(--line);vertical-align:top}table.d td:first-child{color:var(--gold);font-family:Inter;font-size:.8em;width:34%}
table.g{width:100%;border-collapse:collapse;font-family:Inter;font-size:.82em}table.g th,table.g td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}table.g th{color:var(--gold);font-weight:600}
table.g tr.on td{background:var(--gold);color:#2a1f05;font-weight:700}
.refs{font-family:Inter;font-size:.8em}.refs li{margin:4px 0}.refs a{color:var(--gold2)}
.guide{max-width:1240px;margin:0 auto 26px;padding:0 16px}.guide details{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:12px 16px}.guide summary{cursor:pointer;font-family:Cinzel;color:var(--gold)}
footer{text-align:center;padding:16px;color:var(--mut);font-size:.85em}
</style></head><body>
<header><div class="coin">$</div><h1>Tesoro Numismático</h1><p>Monedas y billetes de colección de todos los países y épocas · Precio estimado en CLP según estado de conservación, con referencias en Chile e internacionales</p>
<a class="wa" href="__WA__" target="_blank" rel="noopener">💬 Consultar por WhatsApp</a>
<div class="stats"><div class="stat"><b>__N__</b><span>Fichas</span></div><div class="stat"><b>__U__</b><span>Piezas</span></div><div class="stat"><b>__P__</b><span>Países</span></div><div class="stat"><b>__T__</b><span>Valor total Chile (CLP)</span></div></div></header>
<div class="filters">
<div><label>Buscar</label><input id="q" placeholder="Denominación, KM/Pick, serie, material…"></div>
<div><label>Tipo</label><select id="f_tipo"></select></div><div><label>País / Territorio</label><select id="f_pais"></select></div>
<div><label>Continente</label><select id="f_cont"></select></div>
<div><label>Época</label><select id="f_ep"></select></div><div><label>Año</label><select id="f_anio"></select></div>
<div><label>Estado de conservación</label><select id="f_estado"></select></div><div><label>Material</label><select id="f_mat"></select></div>
<div><label>Origen de estimación</label><select id="f_orig"></select></div>
<div><label>Precio mín. (CLP)</label><input id="pmin" type="number" min="0" step="500"></div><div><label>Precio máx. (CLP)</label><input id="pmax" type="number" min="0" step="500"></div>
<div><label>Ordenar</label><select id="ord"><option value="d">Precio: mayor a menor</option><option value="a">Precio: menor a mayor</option><option value="yo">Año: más antiguas</option><option value="yn">Año: más recientes</option><option value="p">País A–Z</option></select></div>
<button class="reset" id="rst">Limpiar filtros</button>
</div><div id="count"></div><div class="grid" id="g"></div>
<div class="guide"><details><summary>📖 Guía de estados de conservación y precios</summary>
<p>Cada ficha muestra una <b>tabla comparativa de precio estimado en CLP según el estado</b>, destacando en dorado el estado real de la pieza.</p>
<table class="g"><tr><th>Código</th><th>Estado</th><th>Descripción</th></tr>
<tr><td>UNC</td><td>Sin Circular</td><td>Sin desgaste ni dobleces; brillo y papel/metal de origen.</td></tr>
<tr><td>AU</td><td>Casi Sin Circular</td><td>Mínimo roce en puntos altos o un doblez leve.</td></tr>
<tr><td>XF</td><td>Muy Bueno+</td><td>Desgaste ligero; detalles nítidos; billete con pocos dobleces.</td></tr>
<tr><td>VF</td><td>Muy Bueno</td><td>Desgaste moderado, diseño completo; billete con varios dobleces.</td></tr>
<tr><td>F</td><td>Bueno</td><td>Desgaste visible en relieves; billete circulado pero firme.</td></tr>
<tr><td>VG</td><td>Regular</td><td>Bastante desgaste; leyendas legibles; billete blando o con manchas.</td></tr>
<tr><td>G</td><td>Muy Circulado</td><td>Muy gastado; contornos y leyendas parciales.</td></tr></table>
<p><b>Origen de estimación:</b> «Chile / Nacional» = ventas realizadas verificables o anuncios en Chile; «Internacional (solo referencia)» = se usa cuando no hay referencias locales, convertido a CLP con el dólar indicado en la ficha.</p></details></div>
<div class="modal" id="m"><div class="box" id="mb"></div></div>
<footer>Precios estimados en CLP según estado. Prioridad: ventas realizadas en Chile → anuncios en Chile → referencias internacionales (Numista, eBay vendidos, catálogos KM/Pick) convertidas a CLP.</footer>
<script>
const D=__DATA__,WA="__WA__",GR=__GR__;const $=i=>document.getElementById(i);const e=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fm=n=>'$'+Math.round(n).toLocaleString('es-CL');const rg=(a,b)=>a==b?fm(a):fm(a)+' – '+fm(b);
const EPO=['Anterior a 1900','1900–1949','1950–1969','1970–1979','1980–1989','1990–1999','2000 en adelante','Sin confirmar'];
const F={f_tipo:p=>p.tipo,f_pais:p=>p.pais,f_cont:p=>p.continente,f_ep:p=>p.ep,f_anio:p=>p.y?String(p.y):'',f_estado:p=>p.gl,f_mat:p=>p.material,f_orig:p=>p.orig};
const ORD={f_ep:EPO,f_estado:GR.map(g=>g[1]).reverse()};
for(const[id,fn]of Object.entries(F)){let v=[...new Set(D.map(fn).filter(Boolean))];v=ORD[id]?v.sort((a,b)=>ORD[id].indexOf(a)-ORD[id].indexOf(b)):id=='f_anio'?v.sort((a,b)=>b-a):v.sort((a,b)=>a.localeCompare(b,'es'));
 if(id=='f_tipo')['Moneda','Billete','Set / Carpeta'].forEach(t=>{if(!v.includes(t))v.push(t)});
 if(id=='f_ep')EPO.slice(0,7).forEach(t=>{if(!v.includes(t))v.push(t)}),v.sort((a,b)=>EPO.indexOf(a)-EPO.indexOf(b));
 if(id=='f_estado')GR.map(g=>g[1]).reverse().forEach(t=>{if(!v.includes(t))v.push(t)}),v.sort((a,b)=>ORD[id].indexOf(a)-ORD[id].indexOf(b));
 if(id=='f_orig')['Chile / Nacional','Internacional (solo referencia)'].forEach(t=>{if(!v.includes(t))v.push(t)});
 $(id).innerHTML='<option value="">Todos</option>'+v.map(x=>`<option>${e(x)}</option>`).join('');$(id).onchange=r}
['q','pmin','pmax','ord'].forEach(i=>$(i).oninput=r);$('rst').onclick=()=>{document.querySelectorAll('.filters select,.filters input').forEach(x=>x.value='');$('ord').value='d';r()};
const nom=p=>p.nombre||[p.denominacion,p.pais].filter(Boolean).join(' · ');
const mini=p=>p.tabla.length?`<table class="mini">${p.tabla.map(t=>`<tr class="${t.c==p.g?'on':''}"><td>${t.c}</td><td style="text-align:right">${rg(t.a,t.b)}</td></tr>`).join('')}</table>`:'';
function r(){const q=$('q').value.toLowerCase(),a=+$('pmin').value||0,b=+$('pmax').value||1e15;
let L=D.filter(p=>Object.entries(F).every(([id,fn])=>!$(id).value||fn(p)==$(id).value)&&p.pmax>=a&&p.pmin<=b&&(!q||JSON.stringify(p).toLowerCase().includes(q)));
const o=$('ord').value;L.sort((x,y)=>o=='a'?x.pmin-y.pmin:o=='yo'?(x.y||9999)-(y.y||9999):o=='yn'?y.y-x.y:o=='p'?String(x.pais).localeCompare(y.pais,'es'):y.pmax-x.pmax||y.pmin-x.pmin);
$('count').textContent=D.length?`${L.length} de ${D.length} piezas`:'';
$('g').innerHTML=!D.length?'<div class="empty">🪙 Colección lista para recibir las primeras monedas y billetes<small>Muy pronto aparecerán aquí las piezas con su país, época, año, estado y precio estimado según conservación.</small></div>':!L.length?'<div class="empty">Ninguna pieza coincide con estos filtros</div>':L.map(p=>`<div class="card" data-id="${e(p.id)}" onclick="sh('${p.id}')">${p.imgs.length?`<img loading="lazy" src="${p.imgs[0]}" alt="${e(nom(p))}">`:`<div class="noimg">${p.tipo=='Billete'?'💵':'🪙'}</div>`}<div class="cb"><div class="t">${e(nom(p))}</div><div class="a">${e(p.pais||'')}${p.anio?' · '+e(p.anio):''}${p.catalogo?' · '+e(p.catalogo):''}</div><span class="tag f">${e(p.tipo||'')}</span>${p.gl?`<span class="tag">${e(p.gl)}</span>`:''}<span class="tag ${p.orig.startsWith('Chile')?'n':'i'}">${p.orig.startsWith('Chile')?'🇨🇱 Chile':'🌐 Internacional'}</span>${mini(p)}<div class="price">Chile: ${rg(p.pmin,p.pmax)} CLP</div></div></div>`).join('')}
const LB={id:'Código',tipo:'Tipo',pais:'País / Territorio',continente:'Continente',denominacion:'Denominación',anio:'Año',ep:'Época',catalogo:'Catálogo (KM / Pick / Numista)',serie:'Serie / Número',ceca:'Ceca / Imprenta',firmas:'Firmas',material:'Material',peso:'Peso',diametro:'Diámetro / Medidas',canto:'Canto',tirada:'Tirada',anverso:'Anverso',reverso:'Reverso',gl:'Estado de conservación',estado_detalle:'Detalle del estado',rareza:'Rareza',orig:'Origen de estimación',valor_internacional_usd:'Valor internacional (USD)',valor_internacional_clp:'Valor internacional (CLP)',venta_chile_clp:'Precio estimado Chile (CLP)',stock:'Unidades',notas:'Notas',dolar:'Dólar usado',fecha:'Fecha de registro'};
function sh(id){const p=D.find(x=>x.id==id);
const tg=p.tabla.length?`<h3>💰 Precio estimado según estado (CLP)</h3><table class="g"><tr><th>Estado</th><th>Precio estimado</th><th></th></tr>${p.tabla.map(t=>`<tr class="${t.c==p.g?'on':''}"><td>${e(t.l)}</td><td>${rg(t.a,t.b)}</td><td>${t.c==p.g?'◀ Estado de esta pieza':''}</td></tr>`).join('')}</table>`:'';
const rf=(p.referencias||[]).length?`<h3>🔎 Referencias de precio</h3><ul class="refs">${p.referencias.map(x=>`<li><b>${e(x.tipo||'')}</b>${x.fuente?' · '+(x.url?`<a href="${e(x.url)}" target="_blank" rel="noopener">${e(x.fuente)}</a>`:e(x.fuente)):''}${x.precio_clp?' · '+e(x.precio_clp)+' CLP':''}${x.estado?' · estado '+e(x.estado):''}${x.nota?' — '+e(x.nota):''}</li>`).join('')}</ul>`:'';
$('mb').innerHTML=`<span class="x" onclick="$('m').classList.remove('on')">×</span><h2>${e(nom(p))}</h2><i>${e(p.pais||'')}${p.anio?' · '+e(p.anio):''} · ${e(p.ep)}</i>${p.descripcion?`<p style="border-left:3px solid var(--gold);padding-left:10px">${e(p.descripcion)}</p>`:''}<div class="ph">${p.imgs.map(i=>`<a href="${i}" target="_blank"><img src="${i}" alt=""></a>`).join('')}</div>${tg}${rf}<h3>📜 Ficha técnica</h3><table class="d">${Object.entries(LB).filter(([k])=>p[k]!=null&&p[k]!=='').map(([k,l])=>`<tr><td>${l}</td><td>${e(p[k])}</td></tr>`).join('')}</table><p><a class="wa" href="${WA}%20por%20${encodeURIComponent(p.id+' '+nom(p))}" target="_blank" rel="noopener">💬 Consultar por esta pieza</a></p>`;$('m').classList.add('on')}
$('m').onclick=ev=>{if(ev.target.id=='m')$('m').classList.remove('on')};document.onkeydown=ev=>{if(ev.key=='Escape')$('m').classList.remove('on')};r();
</script></body></html>'''
paises = len({p.get('pais') for p in items if p.get('pais')})
H = H.replace('__N__', str(len(items))).replace('__U__', str(uds)).replace('__P__', str(paises)).replace('__T__', total).replace('__DATA__', data).replace('__WA__', WA).replace('__GR__', GJS)
import sys as _s; _s.path.insert(0, '/workspace/musica'); from musica_vitrina import inject as _mus
H = _mus(H, OUT, 'monedas', 'Prelude in C - BWV 846', '#0f1f1a', '#d9b45a')
_s.path.insert(0, '/workspace/calculadora'); from calculadora_vitrina import inject as _calc
H = _calc(H, 'monedas')
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(H); open(f'{OUT}/.nojekyll', 'w').close()

README = f'''# 🪙 Tesoro Numismático · Monedas y Billetes de Colección de Todos los Países

Vitrina virtual y tienda de la colección numismática y notafílica de David: monedas, billetes, sets y carpetas de todos los países y épocas.

Cada ficha incluye tipo, país/territorio, continente, denominación, año, época, catálogo (KM / Pick / Numista), serie, ceca o imprenta, material, estado de conservación y **precio estimado en pesos chilenos (CLP) según estado**, con referencias de Chile (ventas realizadas o anuncios) e internacionales cuando no hay referencias locales.

**Funciones de la vitrina:**
- Filtros por tipo (Moneda, Billete, Set / Carpeta), país/territorio, continente, época, año, estado de conservación, material, origen de la estimación (Chile / Internacional) y rango de precio en CLP.
- Búsqueda de texto por denominación, código KM/Pick, serie, material, etc.
- Orden por defecto: de mayor a menor precio (también por año o país).
- Tabla comparativa de precio por estado (G, VG, F, VF, XF, AU, UNC, Proof) con el estado real de cada pieza destacado.
- Calculadora/carrito flotante en CLP (agregar, cambiar cantidades, quitar, vaciar), guardada en el navegador.
- Botón de consulta por WhatsApp.
- Música de fondo: "Prelude in C - BWV 846" (J. S. Bach) interpretada por Kevin MacLeod (incompetech.com), licencia CC BY 4.0.
- Las fotos se publican tal como se suben, sin recortes ni recompresión.

**Totales:** {len(items)} fichas · {uds} piezas · {paises} países · {total} (CLP, venta Chile)

## 🏛️ Vitrina web
**[{URL}]({URL})**
'''
open(f'{OUT}/README.md', 'w', encoding='utf-8').write(README)
print(f"OK: {len(items)} piezas, total {total}")
