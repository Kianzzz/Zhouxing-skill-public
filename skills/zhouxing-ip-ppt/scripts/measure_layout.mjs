// Measure geometry only. No modified images are emitted.
import fs from 'node:fs/promises';
import path from 'node:path';
import {loadCanvas} from './canvas_runtime.mjs';
const {createCanvas,loadImage,GlobalFonts}=loadCanvas();
const [input,output]=process.argv.slice(2);
if(!input||!output)throw Error('Usage: measure_layout.mjs input.json output.json');
const doc=JSON.parse(await fs.readFile(input,'utf8'));
const base=path.resolve(path.dirname(input),doc.asset_base??'.');
for(const f of doc.font_files??[]){if(!GlobalFonts.registerFromPath(path.resolve(base,f.path),f.family))throw Error('Font unavailable: '+f.path);}
const ctx=createCanvas(1,1).getContext('2d');
function renderedInk(line,font,size){
 ctx.font=font;const advance=ctx.measureText(line).width;
 if(!line.trim())return {advance,box:null};
 const pad=Math.ceil(size*2),scale=2;
 const c=createCanvas(Math.ceil(advance+pad*2)*scale,Math.ceil(size+pad*2)*scale),cx=c.getContext('2d');
 cx.scale(scale,scale);cx.font=font;cx.textBaseline='alphabetic';cx.fillText(line,pad,pad+size);
 const data=cx.getImageData(0,0,c.width,c.height).data;let left=c.width,top=c.height,right=-1,bottom=-1;
 for(let yy=0;yy<c.height;yy++)for(let xx=0;xx<c.width;xx++)if(data[(yy*c.width+xx)*4+3]>=16){left=Math.min(left,xx);right=Math.max(right,xx);top=Math.min(top,yy);bottom=Math.max(bottom,yy)}
 if(right<0)throw Error('No rendered glyphs for non-empty text');
 return {advance,box:[left/scale-pad,top/scale-pad,(right-left+1)/scale,(bottom-top+1)/scale]};
}
for(const s of doc.slides){
 for(const o of s.objects){
  const [x,y,w,h]=o.bbox;
  if(o.type==='text'){
   const font=`${o.bold?'bold ':''}${o.font_size}px "${o.font}"`;
   o.line_ink_boxes=[];
   for(const [n,line]of o.text.split('\n').entries()){
    const m=renderedInk(line,font,o.font_size);if(!m.box)continue;let start=x;
    if(o.align==='right')start+=w-m.advance;
    if(o.align==='center')start+=(w-m.advance)/2;
    o.line_ink_boxes.push([start+m.box[0],y+n*o.font_size*(o.line_spacing??1.2)+m.box[1],m.box[2],m.box[3]]);
   }
   const a=o.line_ink_boxes;
   const l=a.length?Math.min(...a.map(b=>b[0])):x,t=a.length?Math.min(...a.map(b=>b[1])):y;
   o.ink_bbox=a.length?[l,t,Math.max(...a.map(b=>b[0]+b[2]))-l,Math.max(...a.map(b=>b[1]+b[3]))-t]:[x,y,0,0];
   o.text_measurement='local rendered alpha at 2x; not target-app font verification';
  }else if(o.type==='image'){
   const im=await loadImage(path.resolve(base,o.file));const c=createCanvas(im.width,im.height);const cx=c.getContext('2d');cx.drawImage(im,0,0);
   const pixels=cx.getImageData(0,0,im.width,im.height).data;let l=im.width,t=im.height,r=-1,b=-1;
   const threshold=doc.alpha_threshold??32;
   for(let yy=0;yy<im.height;yy++)for(let xx=0;xx<im.width;xx++)if(pixels[(yy*im.width+xx)*4+3]>=threshold){l=Math.min(l,xx);r=Math.max(r,xx);t=Math.min(t,yy);b=Math.max(b,yy);}
   if(r<0)throw Error('Image has no visible alpha: '+o.file);
   const fit=o.fit??'contain';
   if(!['contain','stretch'].includes(fit))throw Error('Declare the actual crop before measuring unsupported fit: '+fit);
   const scale=Math.min(w/im.width,h/im.height);
   const dw=fit==='contain'?im.width*scale:w,dh=fit==='contain'?im.height*scale:h;
   const dx=x+(w-dw)/2,dy=y+(h-dh)/2;
   o.ink_bbox=[dx+l/im.width*dw,dy+t/im.height*dh,(r-l+1)/im.width*dw,(b-t+1)/im.height*dh];
   o.alpha_measurement={threshold,source_bbox:[l,t,r-l+1,b-t+1],source_size:[im.width,im.height]};
  }
 }
}
doc.measurement_note='Font ink geometry is a local estimate; alpha bounds measure opacity only. Verify target screenshots. No image content or aesthetics were evaluated.';
await fs.writeFile(output,JSON.stringify(doc,null,2));
