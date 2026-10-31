// Compose a real screenshot with a bundled device frame; no network or AI redraw.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadCanvas} from './canvas_runtime.mjs';
const {createCanvas,loadImage}=loadCanvas();
const args={};
for(let i=2;i<process.argv.length;i+=2){
 const key=process.argv[i],value=process.argv[i+1];
 if(!key?.startsWith('--')||value===undefined)throw Error('Use --device ID --input screenshot --output result.png [--layers-dir folder] [--fit cover|contain] [--source-crop x,y,w,h] [--crop x,y,w,h]');
 args[key.slice(2)]=value;
}
for(const k of ['device','input','output'])if(!args[k])throw Error('Missing --'+k);
if(path.resolve(args.input)===path.resolve(args.output))throw Error('Output must not overwrite the source screenshot');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../assets/device-mockups');
const manifest=JSON.parse(await fs.readFile(path.join(root,'manifest.json'),'utf8'));
const template=manifest.templates[args.device];
if(!template)throw Error('Unknown template; available: '+Object.keys(manifest.templates).join(', '));
const fit=args.fit??'cover';
if(!['contain','cover'].includes(fit))throw Error('fit must be contain or cover');
const [frameImg,maskImg,inputImg]=await Promise.all([loadImage(path.join(root,template.frame)),loadImage(path.join(root,template.screen_mask)),loadImage(path.resolve(args.input))]);
const [w,h]=template.pixel_size,d=template.density;
if(frameImg.width!==w||maskImg.width!==w||frameImg.height!==h||maskImg.height!==h)throw Error('Template dimensions do not match manifest');
const content=createCanvas(w,h),ctx=content.getContext('2d');
const [x,y,sw,sh]=template.screen_rect.map(v=>v*d);
ctx.fillStyle=args.background??'#080B14';ctx.fillRect(x,y,sw,sh);
let sourceCrop=[0,0,inputImg.width,inputImg.height];
if(args['source-crop']){
 const a=args['source-crop'].split(',').map(Number);
 if(a.length!==4||a.some(v=>!Number.isFinite(v))||a[0]<0||a[1]<0||a[2]<=0||a[3]<=0||a[0]+a[2]>inputImg.width||a[1]+a[3]>inputImg.height)throw Error('source-crop must be a positive rectangle within screenshot pixels');
 sourceCrop=a;
}
const [sx,sy,sourceWidth,sourceHeight]=sourceCrop;
const scale=fit==='cover'?Math.max(sw/sourceWidth,sh/sourceHeight):Math.min(sw/sourceWidth,sh/sourceHeight);
const iw=sourceWidth*scale,ih=sourceHeight*scale;
const dx=x+(sw-iw)/2,dy=y+(sh-ih)/2;
ctx.drawImage(inputImg,...sourceCrop,dx,dy,iw,ih);
ctx.globalCompositeOperation='destination-in';ctx.drawImage(maskImg,0,0);
const frame=createCanvas(w,h);frame.getContext('2d').drawImage(frameImg,0,0);
const combined=createCanvas(w,h),cc=combined.getContext('2d');cc.drawImage(content,0,0);cc.drawImage(frame,0,0);
let crop=[0,0,w,h];
if(args.crop){
 const a=args.crop.split(',').map(Number);
 if(a.length!==4||a.some(v=>!Number.isFinite(v))||a[0]<0||a[1]<0||a[2]<=0||a[3]<=0||a[0]+a[2]>w||a[1]+a[3]>h)throw Error('crop must be a positive rectangle within template pixels');
 crop=a;
}
const outputWidth=Math.round(crop[2]),outputHeight=Math.round(crop[3]);
if(outputWidth<1||outputHeight<1)throw Error('crop must render at least one pixel on each axis');
const outputScaleX=outputWidth/crop[2],outputScaleY=outputHeight/crop[3];
const left=Math.max(x,dx,crop[0]),top=Math.max(y,dy,crop[1]);
const right=Math.min(x+sw,dx+iw,crop[0]+crop[2]),bottom=Math.min(y+sh,dy+ih,crop[1]+crop[3]);
const visibleSource=right>left&&bottom>top?[sx+(left-dx)/scale,sy+(top-dy)/scale,(right-left)/scale,(bottom-top)/scale]:null;
const sourceToLayer={scale_x:scale*outputScaleX,scale_y:scale*outputScaleY,offset_x:(dx-sx*scale-crop[0])*outputScaleX,offset_y:(dy-sy*scale-crop[1])*outputScaleY};
async function save(canvas,file){
 const c=createCanvas(outputWidth,outputHeight);c.getContext('2d').drawImage(canvas,...crop,0,0,c.width,c.height);
 await fs.mkdir(path.dirname(path.resolve(file)),{recursive:true});await fs.writeFile(file,c.toBuffer('image/png'));
}
const layerDir=args['layers-dir']?path.resolve(args['layers-dir']):null;
const outputs=[path.resolve(args.output),...(layerDir?['screen.png','frame.png','placement.json'].map(n=>path.join(layerDir,n)):[])];
if(outputs.includes(path.resolve(args.input)))throw Error('Output layers must not overwrite the source screenshot');
await save(combined,args.output);
if(args['layers-dir']){
 const dir=path.resolve(args['layers-dir']);await fs.mkdir(dir,{recursive:true});
 await save(content,path.join(dir,'screen.png'));await save(frame,path.join(dir,'frame.png'));
 await fs.writeFile(path.join(dir,'placement.json'),JSON.stringify({device:args.device,input:path.resolve(args.input),fit,source_crop:sourceCrop,source_pixel_size:[inputImg.width,inputImg.height],visible_source_rect:visibleSource,source_to_layer:sourceToLayer,crop,output_pixel_size:[outputWidth,outputHeight],screen_rect:template.screen_rect,source_project:manifest.source_project,source_revision:manifest.revision,layer_order:['screen.png','frame.png'],note:'Both layers share the same box. Keep native slide text separate. Cover fills the screen. Verify protected evidence and remap native annotations with source_to_layer; then scale/translate to slide coordinates.'},null,2));
}
console.log(JSON.stringify({output:path.resolve(args.output),device:args.device,fit,pixel_size:[outputWidth,outputHeight]}));
