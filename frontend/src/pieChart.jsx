// Pie Chart displaying the postive, neutral, and negative percentages

// Import library for charts 
import { Chart as ChartJS } from "chart.js/auto";
import { Bar, Doughnut, Line} from "react-chartjs-2";

// Import the data from another .json file
import sourceData from "./data/sourceData.json";

function pieChart(){
    return(
        <div className = "dataCard categoryCard">
        <Doughnut
          data = {{
            labels: sourceData.map((data) => data.label),
            datasets: [
                {
                  label: "Percentage",
                  data: sourceData.map((data) => data.value),
                  backgroundColor:[
                    "rgba(185,230,191, 0.8)", // Positive
                    "rgba(234, 234, 234, 0.8)", // Neutral
                    "rgba(255, 202, 202, 0.8)", // Negative
                  ],
                  borderColor:[
                    "rgba(185,230,191, 0.8)", 
                    "rgba(234, 234, 234, 0.8)", 
                    "rgba(255, 202, 202, 0.8)", 
                  ]

                },
              ],
          }}
        />
      </div>   
    )
}

export default pieChart;