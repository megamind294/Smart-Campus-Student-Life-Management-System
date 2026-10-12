import {createContext,useContext,useEffect,useState,type ReactNode,type Dispatch,type SetStateAction} from 'react';
import {loadState,STORAGE_KEY,seedState,type State} from './model';
const Context=createContext<{state:State;setState:Dispatch<SetStateAction<State>>;storageError:boolean;reset:()=>void}|null>(null);
export function WorkspaceProvider({children}:{children:ReactNode}){
 const [state,setState]=useState(loadState);const [storageError,setStorageError]=useState(false);
 useEffect(()=>{try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state));setStorageError(false)}catch{setStorageError(true)}},[state]);
 return <Context.Provider value={{state,setState,storageError,reset:()=>setState(structuredClone(seedState))}}>{children}</Context.Provider>
}
export function useWorkspace(){const value=useContext(Context);if(!value)throw Error('Workspace provider missing');return value}
