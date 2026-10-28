// SVG topic map adapted from the public Agents That Learn explorer's visual grammar.
import {ringLayout,graphPresentation} from './model.mjs?v=calm-graph-1';
const NS='http://www.w3.org/2000/svg';
function svg(tag,attrs={},text){const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
const intersects=(a,b)=>a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y;
export function labelPosition(point,size,occupied,width,height){
  const gap=14,side=point.x<width/2?1:-1,candidates=[];
  for(const dy of [0,-size.height-8,size.height+8,-2*size.height-16,2*size.height+16])for(const d of [side,-side])
    candidates.push({x:d>0?point.x+gap:point.x-gap-size.width,y:point.y-size.height/2+dy,...size});
  // Keep labels close to their node. If none fits, use the focus preview/list instead
  // of forcing overlapping names into the center or distant margins.
  const distance=c=>Math.hypot(c.x+c.width/2-point.x,c.y+c.height/2-point.y);
  const valid=candidates.filter(c=>c.x>=12&&c.y>=12&&c.x+c.width<=width-12&&c.y+c.height<=height-12&&
    distance(c)<=180&&!occupied.some(b=>intersects(c,b)));
  return valid.sort((a,b)=>distance(a)-distance(b))[0]||null;
}
export class TopicGraph{
  constructor(root,{onWork,onTheme,onPreview,onZoom}){
    this.root=root;this.callbacks={onWork,onTheme,onPreview,onZoom};this.view={zoom:1,x:0,y:0};this.selected='';this.hover='';
    this.svg=svg('svg',{id:'research-graph',tabindex:0,role:'group','aria-label':'Topic membership graph. Focus a node for its name; Enter opens details.'});
    this.stage=svg('g',{'data-graph-stage':''});this.svg.append(this.stage);root.replaceChildren(this.svg);
    this.svg.addEventListener('keydown',e=>{
      if(e.target!==this.svg)return;
      const delta={ArrowLeft:[35,0],ArrowRight:[-35,0],ArrowUp:[0,35],ArrowDown:[0,-35]}[e.key];
      if(delta){e.preventDefault();this.view.x+=delta[0];this.view.y+=delta[1];this.transform();}
      if(['+','=','-'].includes(e.key)){e.preventDefault();this.zoom(e.key==='-'?.8:1.25);}
      if(['Home','0'].includes(e.key)){e.preventDefault();this.reset();}
    });
    this.svg.addEventListener('pointerdown',e=>{
      if(e.button!==0||e.pointerType==='touch'||e.target.closest('.map-node'))return;
      this.drag={id:e.pointerId,x:e.clientX,y:e.clientY,startX:this.view.x,startY:this.view.y,scale:this.width/this.svg.getBoundingClientRect().width};
      this.svg.setPointerCapture(e.pointerId);this.svg.classList.add('is-panning');
    });
    this.svg.addEventListener('pointermove',e=>{if(!this.drag||e.pointerId!==this.drag.id)return;
      this.view.x=this.drag.startX+(e.clientX-this.drag.x)*this.drag.scale;this.view.y=this.drag.startY+(e.clientY-this.drag.y)*this.drag.scale;this.transform();});
    const stop=()=>{this.drag=null;this.svg.classList.remove('is-panning');};
    this.svg.addEventListener('pointerup',stop);this.svg.addEventListener('pointercancel',stop);this.svg.addEventListener('lostpointercapture',stop);
  }
  render(model,{labels,selected}){
    const focusID=this.svg.contains(document.activeElement)?document.activeElement.dataset.nodeId:null;
    const narrow=this.root.clientWidth<600;this.width=narrow?720:1100;this.height=narrow?980:720;this.narrow=narrow;
    this.labels=labels;this.selected=selected?'w:'+selected:'';this.hover='';this.model=model;
    this.presentation=graphPresentation(model,labels);
    this.nodes=ringLayout(model,this.width,this.height,narrow);this.nodeMap=new Map(this.nodes.map(n=>[n.data.id,n]));
    this.svg.setAttribute('viewBox',`0 0 ${this.width} ${this.height}`);this.stage.replaceChildren();
    const edgeLayer=svg('g',{'aria-hidden':'true'}),workLayer=svg('g'),topicLayer=svg('g'),labelLayer=svg('g',{'aria-hidden':'true'});
    this.stage.append(edgeLayer,workLayer,topicLayer,labelLayer);this.edges=[];this.elements=new Map();this.labelRecords=[];this.topicBoxes=[];
    this.guide=svg('g',{'aria-hidden':'true',class:'map-guide'});
    this.guide.append(svg('text',{x:this.width/2,y:this.height/2-9,class:'map-guide-title'},'Start with a theme'),
      svg('text',{x:this.width/2,y:this.height/2+22,class:'map-guide-hint'},'Hover to trace its connections'));
    this.stage.append(this.guide);
    for(const edge of model.edges){const a=this.nodeMap.get(edge.data.source)?.position,b=this.nodeMap.get(edge.data.target)?.position;if(!a||!b)continue;
      const e=svg('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,class:'map-edge'});edgeLayer.append(e);this.edges.push({e,...edge.data});}
    const interact=(g,n)=>{
      const d=n.data;g.dataset.nodeId=d.id;g.classList.add('map-node');g.setAttribute('tabindex','0');g.setAttribute('role','button');
      g.setAttribute('aria-label',d.type==='theme'?`${d.name}: ${d.count} matching works. Toggle theme.`:`${d.name}. Open evidence notes.`);g.append(svg('title',{},d.name));
      if(d.type==='theme')g.setAttribute('aria-pressed',String(this.activeThemes?.includes(d.theme)||false));
      const show=()=>{this.hover=d.id;this.highlight();this.callbacks.onPreview(d);};
      const clear=()=>{this.hover='';this.highlight();this.callbacks.onPreview(this.nodeMap.get(this.selected)?.data);};
      g.addEventListener('mouseenter',show);g.addEventListener('focus',show);
      g.addEventListener('mouseleave',()=>{if(document.activeElement!==g)clear();});g.addEventListener('blur',clear);
      const activate=()=>d.type==='theme'?this.callbacks.onTheme(d.theme):this.callbacks.onWork(d.work);
      g.addEventListener('click',activate);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();e.stopPropagation();activate();}});
      this.elements.set(d.id,g);return g;
    };
    for(const n of this.nodes.filter(n=>n.data.type==='work')){
      const {x,y}=n.position,d=n.data,g=svg('g',{'data-work':d.work});g.append(svg('circle',{cx:x,cy:y,r:narrow?17:12,class:'map-hit'}));
      const square=d.kind==='system',size=narrow?12:10;
      g.append(square?svg('rect',{x:x-size/2,y:y-size/2,width:size,height:size,rx:1.5,class:'map-system'}):svg('circle',{cx:x,cy:y,r:narrow?6.5:5.4,class:'map-'+d.kind}));
      workLayer.append(interact(g,n));
      const group=svg('g',{class:'map-name',visibility:'hidden'}),leader=svg('line',{class:'map-name-leader'}),text=svg('text',{'font-size':narrow?24:13,class:'map-name-text'});
      const limit=narrow?20:25,words=d.label.split(/\s+/),lines=[''];
      for(const w of words){const i=lines.length-1;if(lines[i]&&lines[i].length+w.length+1>limit&&lines.length<2)lines.push(w);else lines[i]+=(lines[i]?' ':'')+w;}
      lines.forEach((line,i)=>text.append(svg('tspan',{x:0,dy:i?'1.2em':0},line.length>limit?line.slice(0,limit-1)+'…':line)));
      group.append(leader,text);labelLayer.append(group);this.labelRecords.push({group,text,leader,n});
    }
    for(const n of this.nodes.filter(n=>n.data.type==='theme')){
      const {x,y}=n.position,d=n.data,dx=(x-this.width/2)/(narrow?205:380),dy=(y-this.height/2)/(narrow?365:235);
      const anchor=narrow||Math.abs(dx)<.25?'middle':dx>0?'start':'end',lx=x+dx*(narrow?20:26);
      let ly=y+(narrow?(dy<-.35?-36:35)+(dy>.96?45:0):dy*28);
      const words=d.name.split(' '),multiline=d.name.length>16;let countOffset=multiline?(narrow?43:29):!narrow&&dy<-.45?7:narrow?24:18;
      if(dy<-.45){ly=y-(narrow?(multiline?80:58):(multiline?40:28));countOffset=narrow?(multiline?43:24):(multiline?18:7);}
      if(narrow)ly=Math.min(ly,this.height-18-countOffset);
      const g=svg('g',{'data-theme-node':d.theme});g.append(svg('circle',{cx:x,cy:y,r:21,class:'map-hit'}),svg('circle',{cx:x,cy:y,r:9+Math.sqrt(d.count),class:'map-topic'}));
      const title=svg('text',{x:lx,y:ly-(!narrow&&dy<-.45?12:2),'text-anchor':anchor,class:'map-topic-label'});
      if(multiline){const mid=Math.ceil(words.length/2);title.append(svg('tspan',{x:lx,dy:'-.35em'},words.slice(0,mid).join(' ')),svg('tspan',{x:lx,dy:'1.15em'},words.slice(mid).join(' ')));}else title.textContent=d.name;
      const count=svg('text',{x:lx,y:ly+countOffset,'text-anchor':anchor,class:'map-topic-count'},d.count);g.append(title,count);topicLayer.append(interact(g,n));
      for(const t of [title,count]){const b=t.getBBox();this.topicBoxes.push({x:b.x-5,y:b.y-4,width:b.width+10,height:b.height+8});}
    }
    this.highlight();this.reset();this.callbacks.onPreview(this.nodeMap.get(this.selected)?.data);
    if(focusID)this.elements.get(focusID)?.focus({preventScroll:true});
  }
  setLabels(labels){this.labels=labels;this.presentation=graphPresentation(this.model,labels);this.highlight();}
  select(id){this.selected=id?'w:'+id:'';this.highlight();this.callbacks.onPreview(this.nodeMap.get(this.selected)?.data);}
  arrangeLabels(){
    const active=this.hover||this.selected;
    const items=this.labelRecords.filter(r=>this.presentation.showNames||r.n.data.id===active).sort((a,b)=>(b.n.data.id===active)-(a.n.data.id===active));
    for(const r of this.labelRecords)r.group.setAttribute('visibility','hidden');
    const occupied=[...this.topicBoxes,...this.nodes.map(n=>({x:n.position.x-9,y:n.position.y-9,width:18,height:18}))];
    for(const r of items){const b=r.text.getBBox(),size={width:b.width+12,height:b.height+8};
      const p=labelPosition(r.n.position,size,occupied,this.width,this.height);
      if(!p)continue;
      const tx=p.x+6-b.x,ty=p.y+4-b.y;r.text.setAttribute('transform',`translate(${tx} ${ty})`);
      const distance=Math.hypot(p.x+p.width/2-r.n.position.x,p.y+p.height/2-r.n.position.y);
      r.leader.setAttribute('x1',r.n.position.x);r.leader.setAttribute('y1',r.n.position.y);r.leader.setAttribute('x2',Math.max(p.x,Math.min(p.x+p.width,r.n.position.x)));r.leader.setAttribute('y2',Math.max(p.y,Math.min(p.y+p.height,r.n.position.y)));r.leader.setAttribute('visibility',distance>50?'visible':'hidden');
      r.group.setAttribute('visibility','visible');r.group.classList.toggle('is-muted',!!active&&r.n.data.id!==active);occupied.push(p);
    }
  }
  highlight(){
    const active=this.hover||this.selected,neighbors=new Set(active?[active]:[]);
    for(const edge of this.edges){const match=edge.source===active||edge.target===active;if(match){neighbors.add(edge.source);neighbors.add(edge.target);}edge.e.classList.toggle('is-emphasized',!!active&&match);edge.e.classList.toggle('is-muted',!!active&&!match);edge.e.classList.toggle('is-hidden',this.presentation.quietEdges&&!match);}
    for(const [id,g] of this.elements){g.classList.toggle('is-muted',!!active&&!neighbors.has(id));g.classList.toggle('is-chosen',id===this.selected);}
    this.guide.setAttribute('visibility',this.presentation.quietEdges&&!this.presentation.showNames&&!active?'visible':'hidden');
    this.arrangeLabels();
  }
  transform(){const {zoom,x,y}=this.view;this.stage.setAttribute('transform',`translate(${this.width/2*(1-zoom)+x} ${this.height/2*(1-zoom)+y}) scale(${zoom})`);this.callbacks.onZoom(zoom);}
  zoom(factor){this.view.zoom=Math.max(.6,Math.min(3,Math.round(this.view.zoom*factor*100)/100));this.transform();}
  reset(){this.view={zoom:1,x:0,y:0};this.transform();}
}
