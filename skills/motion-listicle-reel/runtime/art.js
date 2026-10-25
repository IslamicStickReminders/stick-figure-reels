/* ===========================================================
   art.js - the flat vector library
   House rules, enforced here so every piece matches:
     - no gradients inside objects, no strokes under 3px,
       no shadows, no perspective. Flat fills only.
     - figures are a circle head on a capsule body. No faces,
       no hands, no feet. Gender-neutral, culture-neutral.
     - at most five figure colours in one frame.
     - everything sits on a single 3px ground line.
   Each piece returns {el, apply(t)} and animates itself.
   =========================================================== */

const A = {};
const P = ['var(--rose)','var(--sky)','var(--skin)','var(--sage)','var(--bone)','var(--clay)'];

/* ---------- primitives ------------------------------------- */
const rr = (x,y,w,h,r,fill,extra='') =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" ${extra}/>`;

/* a figure: circle head on a capsule body, standing on baseY */
const fig = (x, baseY, h, color, skin=P[2], opts={}) => {
  const seated = !!opts.seated;
  const hr = h * (seated ? .21 : .165);
  const bw = h * (seated ? .60 : .44);
  const gap = h * .035;
  const bodyTop = baseY - h + hr*2 + gap;
  const bodyH = baseY - bodyTop;
  const cy = baseY - h + hr;
  return `<g ${opts.id?`id="${opts.id}"`:''} ${opts.extra||''}>
    ${rr(x-bw/2, bodyTop, bw, bodyH, seated ? bw/2 : bw/2, color)}
    ${seated ? rr(x-bw/2, bodyTop+bodyH*.55, bw, bodyH*.45, h*.07, color) : ''}
    <circle cx="${x}" cy="${cy}" r="${hr}" fill="${skin}"/>
  </g>`;
};

const groundLine = (x1,x2,y,c='var(--maroon)') =>
  `<rect x="${x1}" y="${y}" width="${x2-x1}" height="3" rx="1.5" fill="${c}"/>`;

const mk = (markup, apply) => {
  const el = E.svg(markup);
  return {el, apply: apply ? (t) => apply(t, el) : () => {}};
};
const q = (el, id) => el.querySelector('#' + id);

/* ---------- 1. masjid (title) ------------------------------ */
A.masjid = (o={}) => {
  const W=900,H=560, cx=W/2, base=470;
  const cols=[P[0],P[1],P[4],P[2],P[3],P[1],P[0],P[4]];
  let crowd='';
  cols.forEach((c,i)=>{
    const x = cx - 230 + i*66;
    crowd += `<g id="c${i}" opacity="0">${fig(x, base, 92, c)}</g>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="mosque">
      <rect id="min1" x="${cx-262}" y="190" width="40" height="280" fill="var(--maroon)"/>
      <path d="M${cx-262} 190 L${cx-242} 142 L${cx-222} 190 Z" fill="var(--cream-deep)"/>
      <rect id="min2" x="${cx+222}" y="190" width="40" height="280" fill="var(--maroon)"/>
      <path d="M${cx+222} 190 L${cx+242} 142 L${cx+262} 190 Z" fill="var(--cream-deep)"/>
      <rect x="${cx-190}" y="258" width="380" height="212" fill="var(--maroon)"/>
      <path d="M${cx-170} 258 A170 150 0 0 1 ${cx+170} 258 Z" fill="var(--maroon)"/>
      <rect x="${cx-7}" y="86" width="14" height="36" rx="7" fill="var(--cream-deep)"/>
      <circle cx="${cx}" cy="78" r="13" fill="var(--cream-deep)"/>
      <path d="M${cx-62} 470 L${cx-62} 360 A62 62 0 0 1 ${cx+62} 360 L${cx+62} 470 Z" fill="var(--bg)"/>
      <rect x="${cx-330}" y="316" width="118" height="12" rx="6" fill="var(--sky)"/>
      <rect x="${cx+212}" y="316" width="118" height="12" rx="6" fill="var(--cream-deep)"/>
    </g>
    ${groundLine(cx-360, cx+360, base)}
    <g id="crowd">${crowd}</g>
  </svg>`, (t, el) => {
    const grow = E.p(t, .15, .9, E.ease.out);
    q(el,'mosque').style.transform = `translateY(${(1-grow)*34}px) scale(${.94+.06*grow})`;
    q(el,'mosque').style.transformOrigin = `${cx}px ${base}px`;
    q(el,'mosque').style.opacity = grow;
    cols.forEach((_,i)=>{
      const p = E.p(t, 1.0 + i*.07, .5, E.ease.back);
      const g = q(el,'c'+i);
      g.style.opacity = Math.min(1,p*1.4);
      g.style.transform = `translateY(${(1-p)*40}px)`;
    });
  });
};

/* ---------- 2. week strip ---------------------------------- */
A.weekStrip = (o={}) => {
  const days = o.days || ['FRI','SAT','SUN','MON','TUE','WED','THU','FRI'];
  const W=900,H=130, tw=102, gap=10;
  const x0 = (W - (days.length*tw + (days.length-1)*gap))/2;
  let tiles='';
  days.forEach((d,i)=>{
    const x = x0 + i*(tw+gap);
    const end = (i===0 || i===days.length-1);
    tiles += `<g id="d${i}"><rect x="${x}" y="18" width="${tw}" height="94" rx="18"
        fill="${end?'var(--maroon)':'var(--maroon-dim)'}"/>
      <text x="${x+tw/2}" y="72" text-anchor="middle" font-family="Meta" font-weight="600"
        font-size="25" letter-spacing="2" fill="${end?'#f3dde7':'var(--ink-dim)'}">${d}</text></g>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${tiles}
    <g id="beam" opacity="0"><rect x="${x0}" y="120" width="${tw}" height="7" rx="3.5" fill="var(--cream)"/></g>
  </svg>`, (t, el) => {
    days.forEach((_,i)=>{
      const p = E.p(t, .25 + i*.055, .4, E.ease.back);
      const g = q(el,'d'+i);
      g.style.opacity = p; g.style.transform = `scale(${.7+.3*p})`;
      g.style.transformOrigin = `${x0 + i*(tw+gap) + tw/2}px 65px`;
    });
    const span = (days.length-1)*(tw+gap);
    const s = E.p(t, 1.15, 1.5, E.ease.inOut);
    const b = q(el,'beam');
    b.style.opacity = s>0 && s<1 ? 1 : (s>=1 ? 1 : 0);
    b.style.transform = `translateX(${s*span}px)`;
  });
};

/* ---------- 3. reader + rihl ------------------------------- */
A.reader = () => {
  const W=700,H=420, base=360, px=250;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="rd">${fig(px, base, 210, 'var(--sky)', 'var(--skin)', {seated:true})}</g>
    <g id="stand">
      <rect x="400" y="236" width="24" height="150" rx="6" fill="var(--clay)" transform="rotate(26 412 311)"/>
      <rect x="400" y="236" width="24" height="150" rx="6" fill="var(--clay)" transform="rotate(-26 412 311)"/>
    </g>
    <g id="book">
      <rect x="330" y="150" width="166" height="92" rx="6" fill="var(--cream)"/>
      <rect x="332" y="150" width="162" height="92" rx="6" fill="var(--cream)"/>
      <rect x="408" y="150" width="8" height="92" fill="var(--maroon)"/>
    </g>
  </svg>`, (t, el) => {
    const a = E.p(t,.2,.55,E.ease.back);
    q(el,'rd').style.opacity=a; q(el,'rd').style.transform=`translateY(${(1-a)*30}px)`;
    const b = E.p(t,.45,.5,E.ease.back);
    q(el,'stand').style.opacity=b;
    const c = E.p(t,.62,.5,E.ease.back);
    const bk=q(el,'book');
    bk.style.opacity=c;
    bk.style.transform=`translateY(${(1-c)*-24}px) scale(${.8+.2*c})`;
    bk.style.transformOrigin='412px 196px';
  });
};

/* ---------- 4. wardrobe ------------------------------------ */
A.wardrobe = () => {
  const W=620,H=560;
  const garment = (id,x,w,h,fill,top) =>
    `<g id="${id}"><rect x="${x+w/2-5}" y="${top-26}" width="10" height="28" fill="var(--maroon-dim)"/>
      <path d="M${x} ${top+40} L${x+w*.30} ${top} L${x+w*.70} ${top} L${x+w} ${top+40} L${x+w} ${top+h} L${x} ${top+h} Z" fill="${fill}"/></g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <rect x="26" y="26" width="568" height="500" rx="18" fill="none" stroke="var(--maroon)" stroke-width="7"/>
    <rect x="70" y="118" width="480" height="11" rx="5.5" fill="var(--clay)"/>
    ${garment('g1',120,130,250,'#5d4253',130)}
    ${garment('g2',210,140,268,'#7b5c6e',130)}
    ${garment('g3',330,150,300,'var(--cream)',130)}
    <g id="tag" opacity="0">
      <rect x="470" y="196" width="118" height="54" rx="10" fill="var(--sky)" transform="rotate(-12 529 223)"/>
      <text x="529" y="230" text-anchor="middle" font-family="Meta" font-weight="700" font-size="22"
        letter-spacing="2" fill="#17384a" transform="rotate(-12 529 223)">FRIDAY</text>
    </g>
  </svg>`, (t, el) => {
    ['g1','g2','g3'].forEach((id,i)=>{
      const p=E.p(t,.25+i*.16,.5,E.ease.out);
      const g=q(el,id);
      g.style.opacity=p;
      g.style.transform=`translateY(${(1-p)*-30}px) rotate(${(1-p)*(i===2?4:-3)}deg)`;
      g.style.transformOrigin=`${[185,280,405][i]}px 128px`;
    });
    const p=E.p(t,1.05,.55,E.ease.back);
    const tg=q(el,'tag');
    tg.style.opacity=p; tg.style.transform=`translateX(${(1-p)*26}px) scale(${.75+.25*p})`;
    tg.style.transformOrigin='529px 223px';
  });
};

/* ---------- 5. night row (Fajr) ---------------------------- */
A.nightRow = (o={}) => {
  const n = o.count || 5, W=900,H=420, base=330;
  const cols=[P[0],P[1],P[2],P[0],P[4],P[3]];
  let people='';
  for(let i=0;i<n;i++){
    people += `<g id="p${i}" opacity="0">${fig(130+i*98, base, 140, cols[i%cols.length])}</g>`;
  }
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="moon"><path d="M782 56 a40 40 0 1 0 34 58 a32 32 0 1 1 -34 -58Z" fill="var(--cream)"/></g>
    <path id="mihrab" d="M700 330 L700 190 A52 52 0 0 1 804 190 L804 330 Z" fill="var(--maroon)"/>
    ${groundLine(60,860,base,'rgba(185,228,244,.35)')}
    ${people}
  </svg>`, (t, el) => {
    const m=E.p(t,.1,.8,E.ease.out);
    q(el,'moon').style.opacity=m;
    q(el,'moon').style.transform=`translateY(${(1-m)*-22}px)`;
    const h=E.p(t,.3,.6,E.ease.out);
    q(el,'mihrab').style.opacity=h;
    for(let i=0;i<n;i++){
      const p=E.p(t,.55+i*.1,.45,E.ease.back);
      const g=q(el,'p'+i);
      g.style.opacity=p; g.style.transform=`translateY(${(1-p)*34}px)`;
    }
  });
};

/* ---------- 6. labelled cards ------------------------------ */
A.cards = (o={}) => {
  const items=o.items||[], W=900,H=190, cw=o.cw||320, gap=26;
  const x0=(W-(items.length*cw+(items.length-1)*gap))/2;
  let g='';
  items.forEach((it,i)=>{
    const x=x0+i*(cw+gap);
    g+=`<g id="k${i}"><rect x="${x}" y="22" width="${cw}" height="126" rx="20" fill="var(--maroon)"/>
      <text x="${x+cw/2}" y="86" text-anchor="middle" font-family="Accent" font-style="italic"
        font-weight="500" font-size="44" fill="var(--cream)">${it.t}</text>
      <text x="${x+cw/2}" y="122" text-anchor="middle" font-family="Meta" font-weight="600"
        font-size="19" letter-spacing="2.5" fill="#d7a9bd">${it.s}</text></g>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`,
    (t, el) => items.forEach((_,i)=>{
      const p=E.p(t,.3+i*.2,.5,E.ease.back), n=q(el,'k'+i);
      n.style.opacity=p;
      n.style.transform=`translateY(${(1-p)*26}px) scale(${.88+.12*p})`;
      n.style.transformOrigin=`${x0+i*(cw+gap)+cw/2}px 85px`;
    }));
};

/* ---------- 7. walk to masjid ------------------------------ */
A.walk = (o={}) => {
  const W=940,H=420, base=350, bars=o.bars||8;
  let bs='';
  for(let i=0;i<bars;i++){
    const h=28+i*17, x=150+i*34;
    bs+=`<rect id="b${i}" x="${x}" y="${base-120-h}" width="24" height="${h}" rx="5"
      fill="${i===bars-1?'var(--cream)':'var(--maroon)'}" opacity="0"/>`;
  }
  let dots='';
  for(let i=0;i<6;i++) dots+=`<rect id="s${i}" x="${236+i*52}" y="${base-22}" width="26" height="9" rx="4.5" fill="var(--cream-deep)" opacity="0"/>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="home">
      <path d="M60 ${base} L60 268 L148 196 L236 268 L236 ${base} Z" fill="var(--clay)"/>
      <rect x="128" y="300" width="40" height="${base-300}" fill="var(--maroon)"/>
    </g>
    ${bs}
    ${groundLine(40,900,base)}
    ${dots}
    <g id="masjid">
      <rect x="690" y="238" width="190" height="112" fill="var(--maroon)"/>
      <path d="M700 238 A85 72 0 0 1 870 238 Z" fill="var(--maroon)"/>
      <rect x="668" y="212" width="18" height="138" fill="var(--maroon)"/>
      <path d="M668 212 L677 186 L686 212 Z" fill="var(--cream-deep)"/>
      <rect x="884" y="212" width="18" height="138" fill="var(--maroon)"/>
      <path d="M884 212 L893 186 L902 212 Z" fill="var(--cream-deep)"/>
      <rect x="778" y="160" width="9" height="26" rx="4.5" fill="var(--cream-deep)"/>
      <path d="M760 ${base} L760 292 A24 24 0 0 1 808 292 L808 ${base} Z" fill="var(--bg)"/>
    </g>
    <g id="walker">${fig(300, base, 118, 'var(--sky)')}</g>
  </svg>`, (t, el) => {
    const a=E.p(t,.1,.5,E.ease.out);
    q(el,'home').style.opacity=a;
    q(el,'masjid').style.opacity=E.p(t,.3,.5,E.ease.out);
    const wp=E.p(t,.7,2.6,E.ease.inOut);
    const wk=q(el,'walker');
    wk.style.opacity=E.p(t,.6,.35,E.ease.out);
    wk.style.transform=`translate(${wp*400}px, ${Math.abs(Math.sin(wp*26))*-7}px)`;
    for(let i=0;i<6;i++) q(el,'s'+i).style.opacity=E.p(t,.85+i*.33,.3,E.ease.out)*.85;
    for(let i=0;i<bars;i++){
      const p=E.p(t,1.0+i*.17,.4,E.ease.out), b=q(el,'b'+i);
      b.style.opacity=p;
      b.style.transform=`scaleY(${p})`;
      b.style.transformOrigin=`0px ${base-120}px`;
    }
  });
};

/* ---------- 8. khutbah crowd ------------------------------- */
A.khutbah = (o={}) => {
  const W=940,H=400, base=330;
  const cols=[P[2],P[1],P[0],P[4],P[3],P[2],P[1],P[0]];
  let crowd='';
  for(let i=0;i<8;i++) crowd+=`<g id="q${i}" opacity="0">${fig(110+i*74, base, 104, cols[i], P[2], {seated:true})}</g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="minbar">
      <rect x="724" y="${base-54}" width="62" height="54" fill="var(--maroon)"/>
      <rect x="786" y="${base-108}" width="62" height="108" fill="var(--maroon)"/>
      <rect x="848" y="${base-162}" width="62" height="162" fill="var(--maroon)"/>
    </g>
    <g id="khatib" opacity="0">${fig(879, base-162, 150, 'var(--sky)')}</g>
    ${groundLine(60,920,base)}
    ${crowd}
    <g id="late" opacity="0">${fig(60, base, 104, 'var(--cream)')}</g>
  </svg>`, (t, el) => {
    q(el,'minbar').style.opacity=E.p(t,.1,.5,E.ease.out);
    const k=E.p(t,.4,.5,E.ease.back);
    q(el,'khatib').style.opacity=k;
    q(el,'khatib').style.transform=`translateY(${(1-k)*26}px)`;
    for(let i=0;i<8;i++){
      const p=E.p(t,.6+i*.07,.4,E.ease.back), g=q(el,'q'+i);
      g.style.opacity=p; g.style.transform=`translateY(${(1-p)*22}px)`;
    }
    const lp=E.p(t,1.7,1.5,E.ease.inOut), l=q(el,'late');
    l.style.opacity=E.p(t,1.6,.3,E.ease.out);
    l.style.transform=`translate(${lp*548}px,0)`;
  });
};

/* ---------- 9. badge (count + tick) ------------------------ */
A.badge = (o={}) => {
  const label=o.label||'1';
  return mk(`<svg width="300" height="220" viewBox="0 0 300 220">
    <g id="bx"><rect x="90" y="40" width="120" height="120" rx="26" fill="var(--maroon)"/>
      <text x="150" y="125" text-anchor="middle" font-family="Display" font-weight="700"
        font-size="68" fill="var(--cream)">${label}</text></g>
    <g id="tick" opacity="0"><circle cx="208" cy="48" r="17" fill="var(--sage)"/>
      <path d="M200 48 l6 7 l11 -13" stroke="#143322" stroke-width="4.5" fill="none"
        stroke-linecap="round" stroke-linejoin="round"/></g>
  </svg>`, (t, el) => {
    const p=E.p(t,.3,.55,E.ease.back), b=q(el,'bx');
    b.style.opacity=p; b.style.transform=`scale(${.7+.3*p})`; b.style.transformOrigin='150px 100px';
    const k=E.p(t,.95,.45,E.ease.back), tk=q(el,'tick');
    tk.style.opacity=k; tk.style.transform=`scale(${.4+.6*k})`; tk.style.transformOrigin='208px 48px';
  });
};

/* ---------- 10. stepping over ------------------------------ */
A.stepOver = () => {
  const W=900,H=360, base=300;
  const cols=[P[4],P[1],P[0],P[2],P[3],P[1]];
  let row='';
  for(let i=0;i<6;i++) row+=`<g id="r${i}" opacity="0">${fig(150+i*100, base, 96, cols[i], P[2], {seated:true})}</g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${groundLine(80,840,base)}
    ${row}
    <g id="over">${fig(170, base, 150, 'var(--cream)')}</g>
    <g id="no" opacity="0">
      <circle cx="610" cy="118" r="46" fill="none" stroke="var(--rose)" stroke-width="9"/>
      <line x1="578" y1="86" x2="642" y2="150" stroke="var(--rose)" stroke-width="9" stroke-linecap="round"/>
    </g>
  </svg>`, (t, el) => {
    for(let i=0;i<6;i++){
      const p=E.p(t,.2+i*.07,.4,E.ease.back), g=q(el,'r'+i);
      g.style.opacity=p; g.style.transform=`translateY(${(1-p)*20}px)`;
    }
    const w=E.p(t,.9,2.0,E.ease.inOut), o=q(el,'over');
    o.style.opacity=E.p(t,.85,.3,E.ease.out);
    o.style.transform=`translate(${w*440}px, ${-Math.abs(Math.sin(w*Math.PI*3.2))*34}px)`;
    const n=E.p(t,1.85,.5,E.ease.back), nn=q(el,'no');
    nn.style.opacity=n; nn.style.transform=`scale(${.5+.5*n})`; nn.style.transformOrigin='610px 118px';
  });
};

/* ---------- 11. rakah slots -------------------------------- */
A.rakahSlots = (o={}) => {
  const n=o.count||4, W=900,H=240, cw=186, gap=18;
  const x0=(W-(n*cw+(n-1)*gap))/2;
  const pose=(x,i)=> i%2===0
    ? `<g><circle cx="${x}" cy="62" r="17" fill="var(--cream)"/>${rr(x-13,88,26,74,13,'var(--cream)')}</g>`
    : `<g><circle cx="${x+14}" cy="78" r="16" fill="var(--cream)"/>${rr(x-18,96,62,24,12,'var(--cream)')}${rr(x-18,96,24,66,12,'var(--cream)')}</g>`;
  let g='';
  for(let i=0;i<n;i++){
    const x=x0+i*(cw+gap);
    g+=`<g id="m${i}"><rect x="${x}" y="14" width="${cw}" height="186" rx="22" fill="var(--maroon)"/>
      <g id="f${i}" opacity="0" transform="translate(${x+cw/2-14},18)">${pose(14,i)}</g>
      <text x="${x+cw/2}" y="228" text-anchor="middle" font-family="Meta" font-weight="600"
        font-size="20" fill="var(--ink-dim)">${i+1}</text></g>`;
  }
  return mk(`<svg width="${W}" height="${H+40}" viewBox="0 0 ${W} ${H+40}">${g}</svg>`,
    (t, el) => {
      for(let i=0;i<n;i++){
        const s=E.p(t,.25+i*.1,.4,E.ease.out);
        q(el,'m'+i).style.opacity=s;
        q(el,'f'+i).style.opacity=E.p(t,.75+i*.42,.35,E.ease.back);
      }
    });
};

/* ---------- 12. asr -> maghrib dial ------------------------ */
A.dial = (o={}) => {
  const W=900,H=480, cx=180, cy=150, r=74;
  const C=2*Math.PI*r;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--maroon)" stroke-width="10"/>
    <circle id="arc" cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--cream)" stroke-width="10"
      stroke-linecap="round" stroke-dasharray="${C}" stroke-dashoffset="${C}"
      transform="rotate(-90 ${cx} ${cy})"/>
    <text x="${cx}" y="${cy-4}" text-anchor="middle" font-family="Meta" font-weight="600"
      font-size="19" letter-spacing="2" fill="var(--ink-soft)">ASR</text>
    <text x="${cx}" y="${cy+24}" text-anchor="middle" font-family="Meta" font-weight="600"
      font-size="19" letter-spacing="2" fill="var(--cream)">&#8594; MAGHRIB</text>
    <circle id="sun" cx="740" cy="140" r="44" fill="var(--cream)"/>
    ${groundLine(120,820,420)}
    <g id="duaFig">${fig(430, 420, 190, 'var(--sky)', P[2], {seated:true})}
      ${rr(486,296,52,80,16,'var(--cream-deep)')}</g>
  </svg>`, (t, el) => {
    const p=E.p(t,.3,2.0,E.ease.inOut);
    q(el,'arc').setAttribute('stroke-dashoffset', C*(1-p*.72));
    const s=E.p(t,.3,2.0,E.ease.inOut);
    q(el,'sun').style.transform=`translate(${s*34}px, ${s*118}px)`;
    const f=E.p(t,.5,.6,E.ease.back);
    q(el,'duaFig').style.opacity=f;
    q(el,'duaFig').style.transform=`translateY(${(1-f)*28}px)`;
  });
};

/* ---------- 13. dua + bubbles ------------------------------ */
A.dua = () => {
  const W=940,H=560, base=470, px=470;
  const bub=(id,x,y,w)=>`<g id="${id}" opacity="0">
    ${rr(x,y,w,56,28,'var(--sky)')}
    ${[0,1,2].map(k=>`<circle cx="${x+w*0.27+k*w*0.23}" cy="${y+28}" r="6.5" fill="#1b4254"/>`).join('')}
  </g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="dial" transform="translate(146,112)">
      <circle cx="0" cy="0" r="86" fill="none" stroke="var(--maroon)" stroke-width="11"/>
      <circle id="darc" cx="0" cy="0" r="86" fill="none" stroke="var(--cream)" stroke-width="11"
        stroke-linecap="round" stroke-dasharray="540.4" stroke-dashoffset="540.4" transform="rotate(-90)"/>
      <text x="0" y="-8" text-anchor="middle" font-family="Meta" font-weight="600" font-size="21"
        letter-spacing="2" fill="var(--ink-soft)">ASR</text>
      <text x="0" y="24" text-anchor="middle" font-family="Meta" font-weight="600" font-size="21"
        letter-spacing="1.5" fill="var(--cream)">&#8594; MAGHRIB</text>
    </g>
    <circle id="sun" cx="762" cy="100" r="46" fill="var(--cream)"/>
    ${bub('b1',236,120,124)} ${bub('b2',548,152,118)} ${bub('b3',330,230,112)}
    ${groundLine(120,820,base)}
    <g id="phone" opacity="0">
      ${rr(606,384,66,96,14,'var(--maroon-dim)')}
      ${rr(614,392,50,80,8,'#3d1a2c')}
    </g>
    <g id="who">
      ${fig(px, base, 232, 'var(--sky)', P[2], {seated:true})}
      <g transform="rotate(-16 ${px-86} ${base-148})">${rr(px-106,base-200,40,116,20,'var(--cream-deep)')}</g>
      <g transform="rotate(16 ${px+86} ${base-148})">${rr(px+66,base-200,40,116,20,'var(--cream-deep)')}</g>
    </g>
  </svg>`, (t, el) => {
    const d=E.p(t,.15,2.1,E.ease.inOut);
    q(el,'darc').setAttribute('stroke-dashoffset', 540.4*(1-d*0.74));
    q(el,'dial').style.opacity=E.p(t,.1,.5,E.ease.out);
    const sp=E.p(t,.15,2.1,E.ease.inOut), sun=q(el,'sun');
    sun.style.opacity=E.p(t,.1,.5,E.ease.out);
    sun.style.transform=`translate(${sp*26}px, ${sp*150}px)`;
    const f=E.p(t,.35,.6,E.ease.back), who=q(el,'who');
    who.style.opacity=f; who.style.transform=`translateY(${(1-f)*28}px)`;
    const ph=E.p(t,.7,.5,E.ease.out), phn=q(el,'phone');
    phn.style.opacity=ph*(1-E.p(t,2.0,.5,E.ease.out));
    phn.style.transform=`translateY(${E.p(t,2.0,.6,E.ease.out)*70}px) rotate(${E.p(t,2.0,.6,E.ease.out)*22}deg)`;
    ['b1','b2','b3'].forEach((id,i)=>{
      const p2=E.p(t,1.25+i*.28,.45,E.ease.back), g=q(el,id);
      g.style.opacity=p2;
      g.style.transform=`translateY(${(1-p2)*18}px) scale(${.72+.28*p2})`;
      g.style.transformOrigin=`${[298,607,386][i]}px ${[148,180,258][i]}px`;
    });
  });
};


/* ===========================================================
   SET 2 - aqida / tanzih pieces.
   Same vocabulary: flat fills, one ground line, cream is the
   only colour that says "look here". Where a piece argues a
   negation, the negation is DRAWN (a strike, a break, a piece
   that will not come apart) rather than labelled.
   =========================================================== */

/* strike-through: a cream bar drawn across, wiping in */
const strike = (id, x1, y1, x2, y2, c = 'var(--rose)', w = 11) =>
  `<line id="${id}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c}"
     stroke-width="${w}" stroke-linecap="round"
     pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`;
const drawStrike = (el, id, t, t0, dur = .4) =>
  q(el, id).setAttribute('stroke-dashoffset', 1 - E.p(t, t0, dur, E.ease.out));

const divider = (x, y1, y2) =>
  `<line x1="${x}" y1="${y1}" x2="${x}" y2="${y2}" stroke="rgba(247,237,194,.17)" stroke-width="2"/>`;

/* ---------- 14. the human default: idol + sky-god --------- */
A.humanDefault = () => {
  const W = 960, H = 560, base = 470;
  const ix = 232, sx = 706;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="idol">
      ${rr(ix - 86, base - 40, 172, 40, 8, 'var(--maroon)')}
      ${rr(ix - 44, base - 160, 88, 124, 14, 'var(--maroon)')}
      ${rr(ix - 62, base - 300, 124, 146, 24, 'var(--maroon)')}
      ${rr(ix - 112, base - 292, 44, 112, 22, 'var(--maroon)')}
      ${rr(ix + 68, base - 292, 44, 112, 22, 'var(--maroon)')}
      <circle cx="${ix}" cy="${base - 352}" r="62" fill="var(--maroon)"/>
      <ellipse cx="${ix - 22}" cy="${base - 360}" rx="13" ry="17" fill="var(--bg)"/>
      <ellipse cx="${ix + 22}" cy="${base - 360}" rx="13" ry="17" fill="var(--bg)"/>
    </g>
    <g id="sky" opacity="0" stroke="rgba(247,237,194,.46)" stroke-width="6" fill="none">
      <path d="M${sx - 150} ${base - 112} a46 46 0 0 1 38 -66 a52 52 0 0 1 96 -8 a44 44 0 0 1 84 12 a42 42 0 0 1 -14 62 Z"
            stroke="rgba(247,237,194,.24)"/>
      <circle cx="${sx}" cy="${base - 348}" r="44"/>
      <path d="M${sx - 34} ${base - 320} q34 64 68 0"/>
      <path d="M${sx - 72} ${base - 290} L${sx - 46} ${base - 300} L${sx + 46} ${base - 300} L${sx + 72} ${base - 290} L${sx + 56} ${base - 150} L${sx - 56} ${base - 150} Z"/>
      <path d="M${sx - 72} ${base - 286} q-78 -14 -118 -56"/>
      <path d="M${sx + 72} ${base - 286} q78 -14 118 -56"/>
    </g>
    ${groundLine(90, 420, base)}
    ${strike('s1', 96, 498, 392, 86)}
    ${strike('s2', 540, 498, 872, 86)}
  </svg>`, (t, el) => {
    const a = E.p(t, .15, .55, E.ease.back), i = q(el, 'idol');
    i.style.opacity = a; i.style.transform = `translateY(${(1 - a) * 32}px)`;
    const b = E.p(t, .55, .6, E.ease.out), k = q(el, 'sky');
    k.style.opacity = b; k.style.transform = `translateY(${(1 - b) * -26}px)`;
    drawStrike(el, 's1', t, 1.5, .42); drawStrike(el, 's2', t, 1.72, .42);
  });
};

/* ---------- 15. the four-line blueprint ------------------- */
A.blueprint = (o = {}) => {
  const items = o.items || [];
  const W = 1010, H = 486, cw = 232, gap = 18;
  const x0 = (W - (items.length * cw + (items.length - 1) * gap)) / 2;
  const icon = (kind, cx, cy) => {
    if (kind === 'rings') return `
      <circle cx="${cx-28}" cy="${cy}" r="42" fill="none" stroke="var(--cream)" stroke-width="7"/>
      <circle cx="${cx+28}" cy="${cy}" r="42" fill="none" stroke="var(--cream)" stroke-width="7"/>`;
    if (kind === 'cube') return `
      ${rr(cx-46, cy-40, 84, 84, 9, 'var(--cream)')}
      <path d="M${cx+38} ${cy-40} L${cx+62} ${cy-62} L${cx+62} ${cy+20} L${cx+38} ${cy+44} Z" fill="var(--cream-deep)"/>
      <path d="M${cx-46} ${cy-40} L${cx-22} ${cy-62} L${cx+62} ${cy-62} L${cx+38} ${cy-40} Z" fill="var(--clay)"/>`;
    if (kind === 'twins') return `
      <rect x="${cx-58}" y="${cy-44}" width="70" height="70" fill="none" stroke="var(--cream)" stroke-width="7"/>
      <rect x="${cx-12}" y="${cy-8}" width="70" height="70" fill="none" stroke="var(--cream)" stroke-width="7"/>`;
    return `
      <line x1="${cx}" y1="${cy-46}" x2="${cx}" y2="${cy+36}" stroke="var(--cream)" stroke-width="8"/>
      <line x1="${cx-58}" y1="${cy-36}" x2="${cx+58}" y2="${cy-36}" stroke="var(--cream)" stroke-width="8" stroke-linecap="round"/>
      <path d="M${cx-58} ${cy-36} l-18 38 h36 Z" fill="var(--cream)"/>
      <path d="M${cx+58} ${cy-36} l-18 38 h36 Z" fill="var(--cream)"/>
      ${rr(cx-34, cy+36, 68, 12, 6, 'var(--cream)')}`;
  };
  let g = '';
  items.forEach((it, i) => {
    const x = x0 + i * (cw + gap), cx = x + cw / 2;
    g += `<g id="bp${i}">
      <text x="${cx}" y="42" text-anchor="middle" font-family="Meta" font-weight="700"
        font-size="30" fill="var(--ink-dim)">${i + 1}</text>
      <text x="${cx}" y="136" text-anchor="middle" font-family="Arabic" font-weight="700"
        font-size="68" fill="var(--cream)">${it.ar || ''}</text>
      ${icon(it.icon, cx, 286)}
      ${strike('bs' + i, cx - 84, 356, cx + 84, 208)}
      <text x="${cx}" y="440" text-anchor="middle" font-family="Display" font-weight="700"
        font-size="30" fill="var(--ink)">${it.kills || ''}</text>
      ${i ? divider(x - gap / 2, 20, 456) : ''}
    </g>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`,
    (t, el) => items.forEach((_, i) => {
      const p = E.p(t, .25 + i * .32, .45, E.ease.out), n = q(el, 'bp' + i);
      n.style.opacity = p; n.style.transform = `translateY(${(1 - p) * 20}px)`;
      drawStrike(el, 'bs' + i, t, .58 + i * .32, .34);
    }));
};

/* ---------- 16. four pieces vs one piece ------------------ */
A.indivisible = () => {
  const W = 920, H = 500, top = 70, bh = 92, bw = 230;
  let stack = '';
  for (let i = 0; i < 4; i++)
    stack += `<g id="pc${i}">${rr(96, top + i * (bh + 4), bw, bh, 10, 'var(--maroon)')}</g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${stack}
    ${divider(460, 50, 450)}
    <g id="solid">${rr(594, top, bw, bh * 4 + 12, 14, 'var(--cream)')}</g>
    <line id="cut" x1="594" y1="${top + 196}" x2="${594 + bw}" y2="${top + 196}"
      stroke="var(--rose)" stroke-width="7" stroke-dasharray="16 13"
      pathLength="1" stroke-dashoffset="0" opacity="0"/>
  </svg>`, (t, el) => {
    for (let i = 0; i < 4; i++) {
      const p = E.p(t, .15 + i * .08, .4, E.ease.out), g = q(el, 'pc' + i);
      g.style.opacity = p;
      const sp = E.p(t, 1.0, .65, E.ease.back);           // it comes apart
      g.style.transform = `translate(${(i % 2 ? 1 : -1) * sp * 58}px, ${(i - 1.5) * sp * 30}px)
                           rotate(${(i % 2 ? 1 : -1) * sp * 5}deg)`;
      g.style.transformOrigin = `211px ${top + i * (bh + 4) + bh / 2}px`;
    }
    const s2 = E.p(t, .75, .55, E.ease.back), so = q(el, 'solid');
    so.style.opacity = s2; so.style.transform = `scale(${.84 + .16 * s2})`;
    so.style.transformOrigin = `709px ${top + 196}px`;
    // a cut line tries to form across it, then gives up
    const c = E.p(t, 1.5, .35, E.ease.out), fade = E.p(t, 2.1, .45, E.ease.out);
    q(el, 'cut').style.opacity = c * (1 - fade);
  });
};

/* ---------- 17. the eye and the divisible thing ----------- */
A.senses = () => {
  const W = 920, H = 460, cy = 230;
  const cell = (id, x, y, fill) => `<g id="${id}">${rr(x, y, 112, 112, 10, fill)}</g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="box">
      ${cell('c0', 110, cy - 118, 'var(--maroon)')}
      ${cell('c1', 228, cy - 118, 'var(--maroon)')}
      ${cell('c2', 110, cy + 2, 'var(--maroon)')}
      ${cell('c3', 228, cy + 2, 'var(--cream)')}
    </g>
    <g id="beam" opacity="0">
      <line x1="372" y1="${cy}" x2="536" y2="${cy}" stroke="rgba(247,237,194,.45)"
        stroke-width="5" stroke-dasharray="13 12"/>
    </g>
    <g id="eye">
      <path d="M556 ${cy} q136 -126 272 0 q-136 126 -272 0 Z" fill="none" stroke="var(--cream)" stroke-width="9"/>
      <circle cx="692" cy="${cy}" r="56" fill="none" stroke="var(--cream)" stroke-width="9"/>
      <circle cx="692" cy="${cy}" r="22" fill="var(--cream)"/>
    </g>
  </svg>`, (t, el) => {
    const b = E.p(t, .2, .5, E.ease.back), bx = q(el, 'box');
    bx.style.opacity = b; bx.style.transform = `scale(${.84 + .16 * b})`;
    bx.style.transformOrigin = `284px ${cy}px`;
    q(el, 'eye').style.opacity = E.p(t, .5, .5, E.ease.out);
    q(el, 'beam').style.opacity = E.p(t, .85, .4, E.ease.out);
    const l = E.p(t, 1.3, .75, E.ease.back), c3 = q(el, 'c3');
    c3.style.transform = `translate(${l * 96}px, ${l * 78}px) rotate(${l * 18}deg)`;
    c3.style.transformOrigin = `284px ${cy + 58}px`;
  });
};

/* ---------- 18. everyone leans on one point --------------- */
A.leaning = (o = {}) => {
  const W = 960, H = 460, base = 380;
  const cols = [P[4], P[1], P[0], P[2], P[3], P[1], P[0]];
  const hs = [130, 176, 146, 206, 142, 182, 126];
  let row = '';
  hs.forEach((h, i) => {
    const x = 96 + i * 86;
    row += `<g id="ln${i}" opacity="0" style="transform-origin:${x}px ${base}px">
      ${fig(x, base, h, cols[i])}</g>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${groundLine(50, 740, base)}
    ${row}
    <g id="anchor" opacity="0">
      <circle cx="834" cy="${base - 150}" r="72" fill="var(--cream)"/>
      <circle cx="834" cy="${base - 150}" r="108" fill="none" stroke="rgba(247,237,194,.30)" stroke-width="6"/>
      <circle cx="834" cy="${base - 150}" r="146" fill="none" stroke="rgba(247,237,194,.15)" stroke-width="6"/>
    </g>
    <path id="arrow" d="M676 ${base - 196} q62 -52 128 -20" fill="none" stroke="var(--cream-deep)"
      stroke-width="7" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
  </svg>`, (t, el) => {
    const a = E.p(t, .15, .55, E.ease.back), an = q(el, 'anchor');
    an.style.opacity = a; an.style.transform = `scale(${.7 + .3 * a})`;
    an.style.transformOrigin = `834px ${base - 150}px`;
    hs.forEach((_, i) => {
      const p = E.p(t, .45 + i * .08, .4, E.ease.back);
      const tilt = E.p(t, 1.35 + i * .05, .6, E.ease.out);
      const g = q(el, 'ln' + i);
      g.style.opacity = p;
      g.style.transform = `translateY(${(1 - p) * 26}px) rotate(${tilt * 12}deg)`;
    });
    q(el, 'arrow').setAttribute('stroke-dashoffset', 1 - E.p(t, 1.5, .6, E.ease.out));
  });
};

/* ---------- 19. hollow vs solid --------------------------- */
A.hollowSolid = () => {
  const W = 940, H = 400, cy = 200;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="hollow">
      <path d="M150 70 h220 v260 h-220 Z M196 116 h128 v168 h-128 Z"
            fill="var(--maroon)" fill-rule="evenodd"/>
      <rect x="196" y="116" width="128" height="168" fill="none"
            stroke="var(--rose)" stroke-width="4" stroke-dasharray="11 9"/>
      <text x="260" y="208" text-anchor="middle" font-family="Meta" font-weight="600"
        font-size="21" letter-spacing="2" fill="var(--rose)">JAWF</text>
      <g id="walls" opacity="0">
        <line x1="150" y1="366" x2="196" y2="366" stroke="var(--cream)" stroke-width="5" stroke-linecap="round"/>
        <line x1="324" y1="366" x2="370" y2="366" stroke="var(--cream)" stroke-width="5" stroke-linecap="round"/>
      </g>
    </g>
    ${divider(470, 50, 350)}
    <g id="solid">${rr(570, 70, 220, 260, 10, 'var(--cream)')}</g>
  </svg>`, (t, el) => {
    const h = E.p(t, .15, .5, E.ease.out), hw = q(el, 'hollow');
    hw.style.opacity = h; hw.style.transform = `translateY(${(1 - h) * 22}px)`;
    q(el, 'walls').style.opacity = E.p(t, .9, .4, E.ease.out);
    const s = E.p(t, .7, .55, E.ease.back), so = q(el, 'solid');
    so.style.opacity = s; so.style.transform = `scale(${.82 + .18 * s})`;
    so.style.transformOrigin = `680px ${cy}px`;
  });
};

/* ---------- 20. a body needs directions ------------------- */
A.cubeDirections = () => {
  const W = 940, H = 460;
  const dot = (id, x, y, lx, ly, label, anchor) => `
    <g id="${id}" opacity="0">
      <line x1="${x}" y1="${y}" x2="${lx}" y2="${ly}" stroke="var(--cream-deep)" stroke-width="3"/>
      <circle cx="${x}" cy="${y}" r="9" fill="none" stroke="var(--cream-deep)" stroke-width="3.5"/>
      <text x="${anchor === 'end' ? lx - 14 : lx + 14}" y="${ly + 8}" text-anchor="${anchor}"
        font-family="Display" font-weight="600" font-size="27" fill="var(--ink)">${label}</text>
    </g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="cube" stroke="var(--bone)" stroke-width="4" fill="none">
      <rect x="350" y="150" width="200" height="200"/>
      <rect x="420" y="100" width="200" height="200"/>
      <line x1="350" y1="150" x2="420" y2="100"/><line x1="550" y1="150" x2="620" y2="100"/>
      <line x1="350" y1="350" x2="420" y2="300"/><line x1="550" y1="350" x2="620" y2="300"/>
    </g>
    ${dot('d1', 485, 125, 300, 92, 'Top', 'end')}
    ${dot('d2', 420, 250, 300, 250, 'Back', 'end')}
    ${dot('d3', 550, 250, 672, 250, 'Front', 'start')}
    ${dot('d4', 485, 325, 672, 400, 'Bottom', 'start')}
    ${strike('cs', 296, 400, 676, 86)}
  </svg>`, (t, el) => {
    const c = E.p(t, .15, .5, E.ease.out), cu = q(el, 'cube');
    cu.style.opacity = c; cu.style.transform = `scale(${.88 + .12 * c})`;
    cu.style.transformOrigin = '485px 225px';
    ['d1', 'd2', 'd3', 'd4'].forEach((id, i) =>
      q(el, id).style.opacity = E.p(t, .55 + i * .22, .35, E.ease.out));
    drawStrike(el, 'cs', t, 1.85, .45);
  });
};

/* ---------- 21. refuge: a cave vs light ------------------- */
A.refuge = () => {
  const W = 960, H = 440, base = 370;
  let rays = '';
  for (let i = 0; i < 11; i++) {
    const a = (-90 + (i - 5) * 15) * Math.PI / 180;
    rays += `<line id="ry${i}" x1="716" y1="${base - 150}"
      x2="${716 + Math.cos(a) * 190}" y2="${base - 150 + Math.sin(a) * 190}"
      stroke="rgba(247,237,194,.34)" stroke-width="5" stroke-linecap="round" opacity="0"/>`;
  }
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="cave">
      <path d="M70 ${base} L70 190 Q238 44 406 190 L406 ${base} Z" fill="var(--maroon)"/>
      <path d="M160 ${base} L160 268 Q238 196 316 268 L316 ${base} Z" fill="var(--bg)"/>
      <g>${fig(238, base, 84, 'var(--sky)', P[2], {seated: true})}</g>
    </g>
    ${divider(500, 60, 390)}
    ${rays}
    <g id="open">${fig(716, base, 180, 'var(--sky)')}
      <g transform="rotate(-20 ${716 - 64} ${base - 128})">${rr(716 - 82, base - 176, 34, 96, 17, 'var(--cream-deep)')}</g>
      <g transform="rotate(20 ${716 + 64} ${base - 128})">${rr(716 + 48, base - 176, 34, 96, 17, 'var(--cream-deep)')}</g>
    </g>
    ${groundLine(60, 900, base)}
  </svg>`, (t, el) => {
    const c = E.p(t, .15, .5, E.ease.out), cv = q(el, 'cave');
    cv.style.opacity = c; cv.style.transform = `translateY(${(1 - c) * 20}px)`;
    const o = E.p(t, .75, .55, E.ease.back), op = q(el, 'open');
    op.style.opacity = o; op.style.transform = `translateY(${(1 - o) * 26}px)`;
    for (let i = 0; i < 11; i++) {
      const p = E.p(t, 1.15 + Math.abs(i - 5) * .06, .5, E.ease.out), r = q(el, 'ry' + i);
      r.style.opacity = p * .9;
      r.style.transform = `scale(${.4 + .6 * p})`;
      r.style.transformOrigin = `716px ${base - 150}px`;
    }
  });
};

/* ---------- 22. the offspring chain ----------------------- */
A.offspringChain = (o = {}) => {
  const steps = o.steps || [];
  const W = 1030, H = 352, bw = 228, gap = 46;
  const x0 = (W - (steps.length * bw + (steps.length - 1) * gap)) / 2;
  let g = '';
  steps.forEach((st, i) => {
    const x = x0 + i * (bw + gap), last = i === steps.length - 1;
    const lines = st.split('\n');
    g += `<g id="st${i}">
      <rect x="${x}" y="54" width="${bw}" height="186" rx="20"
        fill="${last ? '#7d1b2e' : 'none'}" stroke="${last ? 'none' : 'var(--cream-deep)'}" stroke-width="3.5"/>
      ${lines.map((ln, k) => `<text x="${x + bw / 2}" y="${lines.length > 1 ? 130 + k * 52 : 164}"
        text-anchor="middle" font-family="Display" font-weight="${last ? 700 : 500}" font-size="36"
        fill="${last ? 'var(--cream)' : 'var(--ink)'}">${ln}</text>`).join('')}
      ${last ? strike('fs', x + 12, 232, x + bw - 12, 62, 'var(--cream)', 9) : ''}
    </g>`;
    if (i < steps.length - 1) {
      const ax = x + bw + 9;
      g += `<g id="ar${i}" opacity="0">
        <line x1="${ax}" y1="147" x2="${ax + gap - 22}" y2="147" stroke="var(--cream-deep)" stroke-width="5"/>
        <path d="M${ax + gap - 22} 147 l-16 -12 v24 Z" fill="var(--cream-deep)"/></g>`;
    }
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`,
    (t, el) => {
      steps.forEach((_, i) => {
        const p = E.p(t, .2 + i * .44, .38, E.ease.out), n = q(el, 'st' + i);
        n.style.opacity = p; n.style.transform = `translateY(${(1 - p) * 16}px)`;
        if (i < steps.length - 1)
          q(el, 'ar' + i).style.opacity = E.p(t, .48 + i * .44, .3, E.ease.out);
      });
      drawStrike(el, 'fs', t, .34 + steps.length * .44, .4);
    });
};

/* ---------- 23. the broken scale -------------------------- */
A.scales = () => {
  const W = 880, H = 470, cx = 440, pivot = 150;
  const pan = (x, fill) => `
      <line x1="${x}" y1="${pivot}" x2="${x}" y2="${pivot + 78}" stroke="var(--cream-deep)" stroke-width="5"/>
      <path d="M${x - 80} ${pivot + 78} h160 l-32 58 h-96 Z" fill="var(--cream-deep)"/>
      ${fill ? rr(x - 34, pivot + 6, 68, 72, 10, 'var(--maroon)') : ''}`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${rr(cx - 20, pivot, 40, 250, 10, 'var(--cream-deep)')}
    ${rr(cx - 110, 400, 220, 22, 11, 'var(--cream-deep)')}
    <g id="beam" style="transform-origin:${cx}px ${pivot}px">
      ${rr(cx - 240, pivot - 11, 480, 22, 11, 'var(--cream-deep)')}
      <g id="panL">${pan(cx - 210, true)}</g>
      <g id="panR">${pan(cx + 210, false)}</g>
    </g>
  </svg>`, (t, el) => {
    const b = E.p(t, .2, .55, E.ease.out), bm = q(el, 'beam');
    bm.style.opacity = b;
    const tip = E.p(t, .9, .85, E.ease.out);
    bm.style.transform = `rotate(${tip * 16}deg)`;
    const br = E.p(t, 1.95, .5, E.ease.out), pr = q(el, 'panR');
    pr.style.opacity = 1 - br;
    pr.style.transform = `translate(${br * 62}px, ${br * 110}px) rotate(${br * 40}deg)`;
    pr.style.transformOrigin = `${cx + 210}px ${pivot}px`;
  });
};

/* ---------- 24. the name, in rings ------------------------ */
A.nameOrb = (o = {}) => {
  const W = 900, H = 620, cx = 450, cy = 300;
  let rings = '';
  [138, 186, 238, 292].forEach((r, i) =>
    rings += `<circle id="rg${i}" cx="${cx}" cy="${cy}" r="${r}" fill="none"
      stroke="rgba(247,237,194,${.30 - i * .06})" stroke-width="${4 - i * .5}"/>`);
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${rings}
    <text id="nm" x="${cx}" y="${cy + 36}" text-anchor="middle" font-family="Arabic"
      font-weight="700" font-size="158" fill="var(--cream)">${o.ar || ''}</text>
    <text id="tr" x="${cx}" y="${cy + 214}" text-anchor="middle" font-family="Meta"
      font-weight="700" font-size="30" letter-spacing="7" fill="var(--ink-soft)">${o.tr || ''}</text>
  </svg>`, (t, el) => {
    [0, 1, 2, 3].forEach(i => {
      const p = E.p(t, .2 + i * .14, .7, E.ease.out), r = q(el, 'rg' + i);
      r.style.opacity = p; r.style.transform = `scale(${.72 + .28 * p})`;
      r.style.transformOrigin = `${cx}px ${cy}px`;
    });
    const n = E.p(t, .4, .7, E.ease.back), nm = q(el, 'nm');
    nm.style.opacity = n; nm.style.transform = `scale(${.8 + .2 * n})`;
    nm.style.transformOrigin = `${cx}px ${cy}px`;
    q(el, 'tr').style.opacity = E.p(t, 1.0, .5, E.ease.out);
  });
};

/* ---------- 25. three overlapping vs one solid ------------ */
A.threeVsOne = () => {
  const W = 940, H = 470, cy = 235, lx = 234, r = 92;
  /* a trefoil: three rings that LOOK like one shape until they drift apart,
     which is the whole argument in one movement */
  const seats = [[0, -62], [-58, 36], [58, 36]];
  let rings = '';
  seats.forEach((_, i) => {
    rings += `<circle id="tr${i}" cx="${lx}" cy="${cy}" r="${r}"
      fill="var(--maroon)" stroke="var(--cream-deep)" stroke-width="5"/>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="tri">${rings}</g>
    ${strike('ts', lx - 140, cy + 150, lx + 140, cy - 150)}
    ${divider(470, 44, 426)}
    <circle id="one" cx="706" cy="${cy}" r="142" fill="var(--cream)"/>
  </svg>`, (t, el) => {
    const a = E.p(t, .15, .5, E.ease.out);
    q(el, 'tri').style.opacity = a;
    const sp = E.p(t, .85, .7, E.ease.back);          // they come apart: three
    seats.forEach(([dx, dy], i) => {
      const c = q(el, 'tr' + i);
      c.style.transform = `translate(${dx * sp}px, ${dy * sp}px)`;
    });
    drawStrike(el, 'ts', t, 1.75, .42);
    const o = E.p(t, 1.1, .6, E.ease.back), on = q(el, 'one');
    on.style.opacity = o;
    on.style.transform = `scale(${.78 + .22 * o})`;
    on.style.transformOrigin = `706px ${cy}px`;
  });
};

window.A = A;
