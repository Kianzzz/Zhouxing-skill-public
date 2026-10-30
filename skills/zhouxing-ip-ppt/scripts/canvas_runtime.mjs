// Standard Node dependency resolution; a preconfigured runtime is optional.
import path from 'node:path';
import {createRequire} from 'node:module';
export function loadCanvas(){
 const resolvers=[createRequire(import.meta.url),createRequire(path.join(process.cwd(),'package.json'))];
 if(process.env.RUNTIME_NODE_MODULES)resolvers.push(createRequire(path.join(path.resolve(process.env.RUNTIME_NODE_MODULES),'package.json')));
 const errors=[];
 for(const resolve of resolvers){try{return resolve('@napi-rs/canvas')}catch(e){errors.push(e.message)}}
 throw Error('Cannot load @napi-rs/canvas. Install it in the working project, or set optional RUNTIME_NODE_MODULES to an existing node_modules directory. '+errors.join(' | '));
}
