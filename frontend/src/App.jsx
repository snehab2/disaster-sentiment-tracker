import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

// Import library for charts 
import { Chart as ChartJS } from "chart.js/auto";
import { Bar, Doughnut, Line} from "react-chartjs-2";

// Import the data from another .json file
import sourceData from "./data/sourceData.json";
import PieChart from './pieChart';


function App() {
  //const [count, setCount] = useState(0)

/*  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
   </>

  )
*/

  
    return (

      <div className = "App">
        Sentiment Trend
        <div> <PieChart/> </div>
      </div>
    )
  
}

export default App
