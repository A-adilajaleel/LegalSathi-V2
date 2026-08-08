import React from "react";
import FileUpload from "./components/FileUpload";
import Home from "./pages/Home";
import { Routes,Route } from "react-router-dom";

const App = ()=>{
  return(
    <div>
       {/* <FileUpload/> */}




      <Routes>
        <Route path='/' element={<Home/>}/>
        <Route path='/file' element={<FileUpload/>}/>
      </Routes>
      
     
      

    </div>
  )
}

export default App