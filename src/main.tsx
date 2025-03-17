import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Home from './pages/Home/Home'
import ManageData from './pages/ManageData/ManageData'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* <Home /> */}
    <ManageData />
  </StrictMode>,
)
