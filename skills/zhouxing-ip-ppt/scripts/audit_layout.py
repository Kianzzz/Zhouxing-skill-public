#!/usr/bin/env python3
"""Check named spacing constraints; not an aesthetic score."""
import argparse,json,math
from pathlib import Path

def audit(doc):
    errors=[];warnings=[];measurements=[]
    tokens=doc.get('spacing_system',{})
    if not isinstance(tokens,dict) or not tokens:
        errors.append('Use a declared spacing system with at most four primary values')
        return {'errors':errors,'warnings':warnings,'measurements':measurements}
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in tokens.values()):
        return {'errors':['Spacing tokens must be positive finite numbers'],'warnings':[],'measurements':[]}
    if len(set(tokens.values()))>4:
        return {'errors':['Use at most four primary spacing values'],'warnings':[],'measurements':[]}
    slides=doc.get('slides',[])
    if not isinstance(slides,list) or not slides:
        return {'errors':['No slides to audit'],'warnings':[],'measurements':[]}
    for si,s in enumerate(slides,1):
        constraints=s.get('layout_constraints',[])
        if not isinstance(constraints,list) or not constraints:
            errors.append(f'slide {si}: no declared layout constraints');continue
        objects={o['id']:o for o in s.get('objects',[])+s.get('groups',[])}
        def bound(ids,basis):
            bs=[]
            for oid in ids:
                if oid not in objects:raise ValueError('Unknown object '+str(oid))
                o=objects[oid];key='ink_bbox' if basis=='ink' else 'bbox'
                b=o.get(key)
                if not isinstance(b,list) or len(b)!=4 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in b):raise ValueError('Missing/invalid '+key+' for '+str(oid))
                bs.append(b)
            if not bs:raise ValueError('Empty constraint group')
            x=min(b[0]for b in bs);y=min(b[1]for b in bs)
            return [x,y,max(b[0]+b[2]for b in bs)-x,max(b[1]+b[3]for b in bs)-y]
        for c in constraints:
            label=f'slide {si} / '+str(c.get('id','constraint'))
            try:
                basis=c.get('basis','layout');kind=c['kind'];tol=c.get('tolerance',4)
                if basis not in ('layout','ink'):raise ValueError('basis must be layout or ink')
                if isinstance(tol,bool) or not isinstance(tol,(int,float)) or not math.isfinite(tol) or tol<0:raise ValueError('invalid tolerance')
                if kind=='align':
                    if len(c['ids'])<2:raise ValueError('alignment needs at least two objects')
                    vals=[]
                    for oid in c['ids']:
                        b=bound([oid],basis);edge=c.get('edge','left')
                        vals.append({'left':b[0],'right':b[0]+b[2],'top':b[1],'bottom':b[1]+b[3]}[edge])
                    value=max(vals)-min(vals);ok=value<=tol
                elif kind in ('gap','gutter'):
                    if c.get('axis','x') not in ('x','y'):raise ValueError('axis must be x or y')
                    a=bound(c['a'],basis);b=bound(c['b'],basis)
                    value=b[0]-(a[0]+a[2]) if c.get('axis','x')=='x' else b[1]-(a[1]+a[3])
                    if 'token'in c:
                        target=tokens[c['token']];ok=abs(value-target)<=tol
                    else:ok=c['min']<=value<=c['max']
                else:raise ValueError('Unknown constraint kind')
                item={'slide':si,'id':c.get('id'),'value':round(value,2),'basis':basis,'passed':ok};measurements.append(item)
                if not ok:
                    (warnings if c.get('severity')=='warning' else errors).append(label+': '+str(round(value,2))+' outside declared constraint')
            except (ValueError,KeyError,TypeError)as e:errors.append(label+': '+str(e))
    return {'errors':errors,'warnings':warnings,'measurements':measurements,'note':'Constraint checks only; local ink estimates do not prove target rendering or good composition.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('measured_json',type=Path);a=p.parse_args()
    try:r=audit(json.loads(a.measured_json.read_text()))
    except (OSError,ValueError)as e:r={'errors':[str(e)],'warnings':[],'measurements':[]}
    print(json.dumps(r,ensure_ascii=False,indent=2));return bool(r['errors'])
if __name__=='__main__':raise SystemExit(main())
