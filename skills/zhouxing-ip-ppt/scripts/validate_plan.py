#!/usr/bin/env python3
"""Validate the joint composition contract; no automated aesthetic approval."""
import argparse,json,math
from pathlib import Path

def validate(p):
    errors=[];warnings=[]
    def error(msg): errors.append(msg)
    def bbox(b,label):
        if not isinstance(b,list) or len(b)!=4 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in b):error(label+': invalid bbox');return None
        x,y,w,h=b
        if min(x,y)<0 or min(w,h)<=0 or x+w>960.5 or y+h>540.5:error(label+': outside canvas')
        return b
    def intersect(a,b):return min(a[0]+a[2],b[0]+b[2])>max(a[0],b[0]) and min(a[1]+a[3],b[1]+b[3])>max(a[1],b[1])
    if not isinstance(p,dict):return {'errors':['plan must be object'],'warnings':[]}
    if p.get('schema_version')!=2:error('schema_version must be 2')
    if p.get('character_mode') not in ('default','supplied-ip','supplied-person'):error('unknown character_mode')
    if p.get('canvas')!={'width':960,'height':540}:error('canvas must be 960x540')
    spacing=p.get('spacing_system')
    if not isinstance(spacing,dict) or not spacing:error('spacing_system must declare primary spacing values')
    elif any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in spacing.values()):error('spacing values must be positive finite numbers')
    elif len(set(spacing.values()))>4:error('at most four primary spacing values')
    ref=p.get('reference_contract',{})
    if not isinstance(ref,dict) or not all(ref.get(k) for k in ('path','sha256','approval_status')):error('reference_contract needs path/sha256/approval_status')
    elif not isinstance(ref['sha256'],str) or len(ref['sha256'])!=64 or any(c not in '0123456789abcdef' for c in ref['sha256']):error('invalid reference sha256')
    typ=p.get('typography',{})
    if not isinstance(typ,dict) or not all(typ.get(k) for k in ('title_family','body_family','pairing_reason')):error('typography needs title/body families and pairing_reason')
    slides=p.get('slides')
    if not isinstance(slides,list) or not slides:return {'errors':errors+['slides must be non-empty array'],'warnings':warnings}
    for n,s in enumerate(slides,1):
        label=f'slide {n}'
        if not isinstance(s,dict):error(label+': must be object');continue
        if s.get('slide_no')!=n:error(label+': slide_no must be sequential')
        if s.get('visual_priority') not in ('text-led','image-led','balanced'):error(label+': missing/invalid visual_priority')
        for k in ('key_message','layout_type','visual_focus','text_density','visual_sentence','composition','whitespace_intent'):
            if not s.get(k):error(label+': missing '+k)
        constraints=s.get('layout_constraints')
        if not isinstance(constraints,list) or not constraints:error(label+': layout_constraints must be non-empty')
        bleeds=s.get('bleed_objects',[])
        if not isinstance(bleeds,list):error(label+': bleed_objects must be array');bleeds=[]
        bleed_ids=set()
        for o in bleeds:
            if not isinstance(o,dict):error(label+': invalid bleed object');continue
            oid=o.get('id');where=label+': bleed '+str(oid)
            if not isinstance(oid,str) or not oid or oid in bleed_ids:error(where+': missing/duplicate ID')
            else:bleed_ids.add(oid)
            b=o.get('logical_bbox')
            if not isinstance(b,list) or len(b)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in b) or min(b[2:])<=0:
                error(where+': invalid logical_bbox');continue
            x,y,w,h=b;left=max(0,x);top=max(0,y);right=min(960,x+w);bottom=min(540,y+h)
            if right<=left or bottom<=top:error(where+': no visible area');continue
            actual=[left,top,right-left,bottom-top]
            visible=bbox(o.get('visible_bbox'),where)
            if visible and any(abs(a-b)>0.5 for a,b in zip(visible,actual)):error(where+': visible_bbox must equal canvas intersection')
            edges={k for k,yes in [('left',x<0),('top',y<0),('right',x+w>960),('bottom',y+h>540)] if yes}
            declared=o.get('edges')
            if not isinstance(declared,list) or not all(isinstance(k,str) for k in declared) or set(declared)!=edges or not edges:error(where+': edges must match actual crop')
            if not o.get('crop_reason'):error(where+': missing crop_reason')
            regions=o.get('protected_regions')
            if not isinstance(regions,list) or not regions:error(where+': protected_regions required');regions=[]
            for r in regions:
                rb=bbox(r,where+': protected region')
                if rb and (rb[0]<left or rb[1]<top or rb[0]+rb[2]>right+0.5 or rb[1]+rb[3]>bottom+0.5):error(where+': protected region is cropped')
        chars=s.get('characters');texts=s.get('text_boxes');ids=set();tb=[]
        if not isinstance(chars,list):error(label+': characters must be array');chars=[]
        for c in chars:
            if not isinstance(c,dict):error(label+': character must be object');continue
            cid=c.get('id');count=c.get('subject_count')
            if not isinstance(cid,str) or not cid or cid in ids:error(label+': duplicate/missing character ID')
            else:ids.add(cid)
            if not isinstance(count,int) or isinstance(count,bool) or count<1:error(label+': subject_count must be positive integer')
            if c.get('shot') not in ('full','half','close','detail','scene'):error(label+': invalid shot')
            for k in ('semantic_role','interaction_target','crop','layers'):
                if not c.get(k):error(label+': missing character '+k)
            if 'contact_anchor' not in c:error(label+': missing contact_anchor')
            bbox(c.get('visible_bbox'),label+': '+str(cid))
        if not isinstance(texts,list) or not texts:error(label+': text_boxes must be non-empty');texts=[]
        for t in texts:
            if not isinstance(t,dict):error(label+': text box must be object');continue
            tid=t.get('id')
            if not isinstance(tid,str) or not tid or tid in ids:error(label+': duplicate/missing text ID')
            else:ids.add(tid)
            b=bbox(t.get('bbox'),label+': '+str(tid));fs=t.get('font_size')
            if not isinstance(fs,(float,int)) or isinstance(fs,bool) or not math.isfinite(fs) or fs<=0:error(label+': invalid font_size')
            elif fs<16 and t.get('role') not in ('caption','footer','label'):warnings.append(label+': '+str(tid)+' below 16; verify at use size')
            if b:tb.append((tid,b))
        for i,(tid,b) in enumerate(tb):
            for oid,ob in tb[i+1:]:
                if intersect(b,ob):error(label+': text boxes overlap '+str(tid)+'/'+str(oid))
    return {'errors':errors,'warnings':warnings}

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('plan',type=Path);args=a.parse_args()
    try:r=validate(json.loads(args.plan.read_text()))
    except (OSError,ValueError) as e:r={'errors':[str(e)],'warnings':[]}
    print(json.dumps(r,ensure_ascii=False,indent=2));return bool(r['errors'])
if __name__=='__main__':raise SystemExit(main())
